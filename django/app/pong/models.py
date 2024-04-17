from django.db import models
from user.models import User


class Tournament(models.Model):
    name = models.CharField(max_length=100, unique=True)
    date = models.DateField(auto_now_add=True)
    players = models.ManyToManyField(User, related_name='tournaments')
    winner = models.ForeignKey(
        User,
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
                Game(player_1=pair[0], player_2=pair[1], round=self).save()
                pair.clear()
        if len(pair) == 1:
            Game(player_1=pair[0], round=self).save()

    def next_games(self, previous):
        pair = []
        previous_games = previous.games.iterator()
        for game in previous_games:
            pair.append(game.winner())
            if len(pair) == 2:
                Game(player_1=pair[0], player_2=pair[1], round=self).save()
                pair.clear()
        if len(pair) == 1:
            Game(player_1=pair[0], round=self).save()

    def __str__(self):
        return (f'{self.tournament.name} round {self.number}')


class Game(models.Model):
    player_1 = models.ForeignKey(
        User,
        null=True,
        on_delete=models.SET_NULL,
        related_name='home_games'
    )
    player_2 = models.ForeignKey(
        User,
        null=True,
        on_delete=models.SET_NULL,
        related_name='away_games'
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

    # Placeholder method to return winner
    def winner(self):
        return self.player_1

    # Placeholder method to return loser
    def loser(self):
        return self.player_2

    def __str__(self):
        try:
            return (f'{self.player_1.username} vs {self.player_2.username}')
        except Exception:
            return (f'{self.player_1.username} vs NULL')


class Score(models.Model):
    p1_points = models.PositiveSmallIntegerField(default=0)
    p2_points = models.PositiveSmallIntegerField(default=0)
    game = models.OneToOneField(
        Game,
        related_name='score',
        on_delete=models.CASCADE
    )

    def __str__(self):
        return (f'{self.p1_points} - {self.p2_points}')
