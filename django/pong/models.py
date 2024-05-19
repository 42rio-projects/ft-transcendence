import asyncio
import random
from django.db import models
from django.core.exceptions import ValidationError
from channels.db import database_sync_to_async
from django.template.loader import render_to_string
from channels.layers import get_channel_layer


UPPER_PLAYER_LIMIT = 16
LOWER_PLAYER_LIMIT = 4
TOURNAMENT_START_LIMIT = 60 * 5  # seconds
ROUND_TIMEOUT = 60 * 5  # seconds


class TournamentFinished(Exception):
    pass


class Tournament(models.Model):
    name = models.CharField(max_length=100, unique=True)
    admin = models.ForeignKey(
        'user.User',
        on_delete=models.CASCADE,
        related_name='my_tournaments'
    )
    date = models.DateField(auto_now_add=True)
    players = models.ManyToManyField('user.User', related_name='tournaments')
    winner = models.ForeignKey(
        'user.User',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='championships'
    )
    started = models.BooleanField(default=False)
    finished = models.BooleanField(default=False)

    def new_round(self):
        if self.finished:
            raise TournamentFinished('Tournament already over')
        elif self.rounds.count() == 0:
            t_round = Round(tournament=self, number=1)
            t_round.save()
            try:
                t_round.first_games(self.players.all().order_by('?'))
            except Exception:
                t_round.delete()
                raise
        else:
            previous = self.rounds.last()
            previous.finished = True
            previous.save()
            if previous.games.count() == 1:
                if previous.games.last().finished is False:
                    previous.games.last().end()
                self.winner = previous.games.last().winner
                self.finished = True
                self.save()
                raise TournamentFinished()
            else:
                t_round = Round(tournament=self, number=previous.number + 1)
                t_round.save()
                try:
                    t_round.next_games(previous)
                except Exception:
                    t_round.delete()
                    raise
        return t_round

    def invite(self, user):
        if self.started:
            raise Exception("Tournament already started.")
        if self.players.count() + self.invites_sent.count() >= UPPER_PLAYER_LIMIT:
            raise Exception("Player limit reached")
        invite = TournamentInvite(tournament=self, receiver=user)
        invite.save()
        return invite

    def cancel(self):
        if self.started:
            raise Exception("Tournament already started.")
        self.delete()

    def start(self):
        if self.started:
            raise Exception("Tournament already started.")
        if self.players.count() < LOWER_PLAYER_LIMIT:
            raise Exception("Not enough players")
        self.started = True
        self.save()

    @database_sync_to_async
    def a_start(self):
        self.start()

    @database_sync_to_async
    def a_cancel(self):
        self.cancel()

    @database_sync_to_async
    def a_new_round(self):
        return self.new_round()

    @database_sync_to_async
    def a_refresh(self):
        self.refresh_from_db()

    @database_sync_to_async
    def render_winner(self):
        return render_to_string(
            'pong/tournament/online/winner.html', {"tournament": self}
        )

    async def send_channel_message(self, message):
        channel_layer = get_channel_layer()
        await channel_layer.group_send(
            f'tournament_{self.pk}',
            {"type": "tournament.update", "json": message}
        )

    async def advance(self):
        try:
            t_round = await self.a_new_round()
            html = await t_round.render()
            asyncio.create_task(t_round.timeout())
        except TournamentFinished:
            await self.a_refresh()
            html = await self.render_winner()
        await self.send_channel_message(
            {"status": "new_round", "html": html}
        )

    async def timeout(self):
        await asyncio.sleep(TOURNAMENT_START_LIMIT)
        await self.a_refresh()
        if self.started is False:
            await self.a_cancel()

    def __str__(self):
        return (self.name)


class TournamentInvite(models.Model):
    tournament = models.ForeignKey(
        Tournament,
        on_delete=models.CASCADE,
        related_name='invites_sent'
    )
    receiver = models.ForeignKey(
        'user.User',
        on_delete=models.CASCADE,
        related_name='tournament_invites_received'
    )

    def respond(self, accepted):
        tournament = self.tournament
        if accepted is True and tournament.started is False:
            tournament.players.add(self.receiver)
            tournament.save()
        self.delete()

    def clean(self):
        if self.receiver in self.tournament.players.all():
            raise ValidationError(
                'You cannot send a invite to someone who is already in\
                the tournament.'
            )

    def save(self, *args, **kwargs):
        """
        Overridden save method to enforce validation
        """
        self.clean()
        super().save(*args, **kwargs)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                name="%(app_label)s_%(class)s_unique_relationships",
                fields=["tournament", "receiver"]
            ),
        ]


class Round(models.Model):
    tournament = models.ForeignKey(
        Tournament,
        related_name='rounds',
        on_delete=models.CASCADE
    )
    number = models.PositiveSmallIntegerField()
    finished = models.BooleanField(default=False)

    def first_games(self, players):
        pair = []
        for player in players:
            pair.append(player)
            if len(pair) == 2:
                Game(player1=pair[0], player2=pair[1], round=self).save()
                pair.clear()
        if len(pair) == 1:
            Game(player1=pair[0], round=self).save()

    def next_games(self, previous):
        pair = []
        players = []
        previous_games = previous.games.all().order_by('?')
        for game in previous_games:
            if game.finished is False:
                game.end()
            players.append(game.winner)
        if len(players) % 2 != 0:
            players.append(None)
        pairs = list(zip(players[::2], players[1::2]))
        for pair in pairs:
            Game(player1=pair[0], player2=pair[1], round=self).save()

    @database_sync_to_async
    def render(self):
        return render_to_string(
            'pong/tournament/online/round.html', {"round": self}
        )

    @database_sync_to_async
    def a_tournament(self):
        return self.tournament

    @database_sync_to_async
    def games_are_over(self):
        for game in self.games.all():
            if game.finished is False:
                return False
        return True

    @database_sync_to_async
    def a_refresh(self):
        self.refresh_from_db()

    async def timeout(self):
        await asyncio.sleep(ROUND_TIMEOUT)
        await self.a_refresh()
        if self.finished is False:
            tournament = await self.a_tournament()
            await tournament.advance()

    async def try_advance(self):
        await self.a_refresh()
        over = await self.games_are_over()
        if over is False:
            return
        tournament = await self.a_tournament()
        await tournament.advance()

    def __str__(self):
        return (f'{self.tournament.name} round {self.number}')


class Game(models.Model):
    player1 = models.ForeignKey(
        'user.User',
        null=True,
        on_delete=models.SET_NULL,
        related_name='home_games'
    )
    player2 = models.ForeignKey(
        'user.User',
        null=True,
        on_delete=models.SET_NULL,
        related_name='away_games'
    )
    player1_points = models.PositiveSmallIntegerField(default=0)
    player2_points = models.PositiveSmallIntegerField(default=0)
    winner = models.ForeignKey(
        'user.User',
        null=True,
        on_delete=models.SET_NULL,
        related_name='wins'
    )
    round = models.ForeignKey(
        Round,
        null=True,
        blank=True,
        default=None,
        on_delete=models.CASCADE,
        related_name='games'
    )
    date = models.DateField(auto_now_add=True)
    finished = models.BooleanField(default=False)

    def end(self):
        if self.player1 is None:
            self.winner = self.player2
        elif self.player2 is None:
            self.winner = self.player1
        else:
            if self.player1_points > self.player2_points:
                self.winner = self.player1
            elif self.player2_points > self.player1_points:
                self.winner = self.player2
            else:
                if bool(random.getrandbits(1)):
                    self.winner = self.player1
                else:
                    self.winner = self.player2
        self.finished = True
        self.save()

    # Take tournament into consideration
    def __str__(self):
        if self.player1 is not None and self.player2 is not None:
            return (f'{self.player1.username} vs {self.player2.username}')
        elif self.player1 is not None and self.player2 is None:
            return (f'{self.player1.username} vs "Deleted User"')
        elif self.player1 is None and self.player2 is not None:
            return (f'"Deleted User" vs {self.player2.username}')
        else:
            return ('"Deleted User" vs "Deleted User"')


class GameInvite(models.Model):
    sender = models.ForeignKey(
        'user.User',
        on_delete=models.CASCADE,
        related_name='game_invites_sent'
    )
    receiver = models.ForeignKey(
        'user.User',
        on_delete=models.CASCADE,
        related_name='game_invites_received'
    )
    game = models.OneToOneField(
        Game,
        on_delete=models.CASCADE
    )

    def clean(self):
        """
        Custom validation to prevent sending invites to friends.
        """
        invite = GameInvite.objects.filter(
            sender=self.receiver, receiver=self.sender
        )
        if invite.exists():
            raise ValidationError(
                'You cannot send a game invite to someone who has invited you.'
            )

    def save(self, *args, **kwargs):
        """
        Overridden save method to enforce validation
        """
        self.clean()
        super().save(*args, **kwargs)

    def respond(self, accepted):
        game = self.game
        if accepted is True:
            game.player2 = self.receiver
            game.save()
        else:
            game.delete()
        self.delete()

    class Meta:
        constraints = [
            models.UniqueConstraint(
                name="%(app_label)s_%(class)s_unique_relationships",
                fields=["sender", "receiver"]
            ),
            models.CheckConstraint(
                name="%(app_label)s_%(class)s_prevent_self_invite",
                check=~models.Q(sender=models.F("receiver")),
            ),
        ]
