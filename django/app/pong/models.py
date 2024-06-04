import asyncio
from django.db.models import Q
import random
from django.db import models
from django.core.exceptions import ValidationError
from channels.db import database_sync_to_async
from django.template.loader import render_to_string
from channels.layers import get_channel_layer
from relations.models import IsBlockedBy
from asgiref.sync import async_to_sync


UPPER_PLAYER_LIMIT = 16
LOWER_PLAYER_LIMIT = 4
TOURNAMENT_START_LIMIT = 60 * 15  # seconds
ROUND_TIMEOUT = 60 * 10  # seconds


@async_to_sync
async def send_channel_message(group, message):
    channel_layer = get_channel_layer()
    await channel_layer.group_send(group, message,)


def tournament_update(pk, json):
    send_channel_message(
        f'tournament_{pk}', {"type": "tournament.update", "json": json}
    )


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
            raise ValidationError("Tournament already started.")
        if self.players.count() + self.invites_sent.count() >= UPPER_PLAYER_LIMIT:
            raise ValidationError("Player limit reached")
        if self.admin == user:
            self.players.add(self.admin)
            html = render_to_string(
                'pong/tournament/online/player.html', {'player': self.admin}
            )
            tournament_update(
                self.pk, {"status": "new_player", "html": html}
            )
            return
        invite = TournamentInvite(tournament=self, receiver=user)
        invite.save()
        html = render_to_string(
            'pong/tournament/online/invite_sent.html', {'invite': invite}
        )
        tournament_update(
            self.pk, {"status": "new_invite", "html": html}
        )

    def cancel(self):
        if self.started:
            raise Exception("Tournament already started.")
        html = render_to_string('pong/tournament/online/cancelled.html')
        tournament_update(self.pk, {"status": "cancelled", "html": html})
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
    def notify_players(self, notification):
        for player in self.players.all():
            player.notify(notification)

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
            notification = f'New round available for tournament {self.name}.'
        except TournamentFinished:
            await self.a_refresh()
            html = await self.render_winner()
            notification = f'Tournament {self.name} finished.'
        await self.send_channel_message(
            {"status": "new_round", "html": html}
        )
        await self.notify_players(notification)

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
            html = render_to_string(
                'pong/tournament/online/player.html', {'player': self.receiver}
            )
            tournament_update(
                tournament.pk, {"status": "new_player", "html": html}
            )
        self.delete()
        tournament_update(
            self.tournament.pk, {"status": "delete_invite", "id": self.pk}
        )

    def clean(self):
        if self.receiver in self.tournament.players.all():
            raise ValidationError(
                'You cannot send a invite to someone who is already in\
                the tournament.'
            )
        if IsBlockedBy.objects.filter(
            Q(blocker=self.tournament.admin, blocked=self.receiver) | Q(
                blocker=self.receiver, blocked=self.tournament.admin)
        ).exists():
            raise ValidationError("User blocked")

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
                fields=["tournament", "receiver"],
                violation_error_message="Invite already sent"
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
        return (f'round {self.number}')


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

    @database_sync_to_async
    def a_refresh(self):
        self.refresh_from_db()
        self.round
        self.player1
        self.player2

    @database_sync_to_async
    def raw_render(self):
        return render_to_string(
            'pong/game/online/raw_result.html', {"game": self}
        )

    def __str__(self):
        if self.player1 is None:
            p1 = 'Deleted User'
        elif self.player1.nickname and self.round:
            p1 = self.player1.nickname
        else:
            p1 = self.player1.username
        if self.player2 is None:
            p2 = 'Deleted User'
        elif self.player2.nickname and self.round:
            p2 = self.player2.nickname
        else:
            p2 = self.player2.username
        return (f'{p1} vs {p2}')


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
        if IsBlockedBy.objects.filter(
            Q(blocker=self.sender, blocked=self.receiver) | Q(
                blocker=self.receiver, blocked=self.sender)
        ).exists():
            raise ValidationError("User blocked")
        if GameInvite.objects.filter(
                sender=self.sender, receiver=self.receiver
        ).exists():
            raise ValidationError(
                'You have already sent a game invite to this user'
            )
        if GameInvite.objects.filter(
                sender=self.receiver, receiver=self.sender
        ).exists():
            raise ValidationError('User has already invited you')

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
            html = render_to_string('pong/game/online/canceled.html',)
            models.send_channel_message(
                f'game_{self.pk}',
                {
                    'type': 'game.update',
                    'json': {'status': 'canceled', 'html': html}
                },
            )
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
