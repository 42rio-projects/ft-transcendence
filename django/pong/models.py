from django.db import models
from django.core.exceptions import ValidationError


class Tournament(models.Model):
    name = models.CharField(max_length=100, unique=True)
    date = models.DateField(auto_now_add=True)
    players = models.ManyToManyField('user.User', related_name='tournaments')
    winner = models.ForeignKey(
        'user.User',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='championships'
    )

    def new_round(self):
        if self.winner is not None:
            raise Exception('Tournament already over')
        elif self.players.count() < 4:
            raise Exception('Not enough players in the tournament.')
        elif self.rounds.count() == 0:
            round = Round(tournament=self, number=1)
            round.save()
            round.first_games(self.players.iterator())
        else:
            previous = self.rounds.last()
            if previous.games.count() == 1:
                self.winner = previous.games.last().winner()
                self.save()
                return
            else:
                round = Round(tournament=self, number=previous.number + 1)
                round.save()
                round.next_games(previous)

    def __str__(self):
        return (self.name)


class Round(models.Model):
    tournament = models.ForeignKey(
        Tournament,
        related_name='rounds',
        on_delete=models.CASCADE
    )
    number = models.PositiveSmallIntegerField()

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
        previous_games = previous.games.iterator()
        for game in previous_games:
            pair.append(game.winner())
            if len(pair) == 2:
                Game(player1=pair[0], player2=pair[1], round=self).save()
                pair.clear()
        if len(pair) == 1:
            Game(player1=pair[0], round=self).save()

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
