from django.db import models
from django.contrib.auth.models import AbstractUser
from django.db.models import Q
from phonenumber_field.modelfields import PhoneNumberField
from relations.models import IsFriendsWith
from relations.models import IsBlockedBy
from relations.models import FriendInvite
from chat.models import Chat
from pong.models import Game, GameInvite

class User(AbstractUser):
    email_verified = models.BooleanField(default=False)
    mobile_number = PhoneNumberField(
        blank=True, region='BR', help_text='Número de celular')
    friends = models.ManyToManyField(
        'self',
        through="relations.IsFriendsWith",
        symmetrical=True
    )
    nickname = models.CharField(max_length=255, unique=True, null=True, blank=True)
    blocked_list = models.ManyToManyField(
        'self',
        through="relations.IsBlockedBy",
        symmetrical=False
    )
    friend_invites = models.ManyToManyField(
        'self',
        through='relations.FriendInvite',
        symmetrical=False,
        related_name='friend_invites_set'
    )
    avatar = models.ImageField(
        upload_to='user/avatars/',
        null=True,
        blank=True,
        default='user/avatars/default.png'
    )

    def get_friends(self):
        friendships = IsFriendsWith.objects.filter(
            Q(user1=self) | Q(user2=self)
        ).prefetch_related('user1', 'user2')
        friends = []
        for friendship in friendships:
            if friendship.user1 != self:
                friends.append(friendship.user1)
            elif friendship.user2 != self:
                friends.append(friendship.user2)
        return friends

    def get_games(self, filters=None):
        queryFilters = {}
        if filters and 'winner' in filters:
            queryFilters['winner'] = filters['winner']

        home_games = self.home_games.filter(**queryFilters).prefetch_related('player_1','player_2')
        away_games = self.away_games.filter(**queryFilters).prefetch_related('player_1', 'player_2')

        return home_games.union(away_games)

    def count_wins(self):
        filters = {'winner': self}
        gamesWon = self.get_games(filters)
        return gamesWon.count()

    def count_losses(self):
        filters = {'winner': self}
        gamesWon = self.get_games(filters)
        allGames = self.get_games()
        return allGames.count() - gamesWon.count()

    def get_blocks(self):
        blocks = IsBlockedBy.objects.filter(
            Q(blocker=self)
        ).prefetch_related('blocked')
        blocked_users = []
        for block in blocks:
            blocked_users.append(block.blocked)
        return blocked_users

    def get_chats(self):
        blocked_users = self.get_blocks()
        excluded_chats = Chat.objects.filter(
            Q(starter__in=blocked_users) | Q(receiver__in=blocked_users)
        )
        self_chats = Chat.objects.filter(
            Q(starter=self) | Q(receiver=self)
        )
        chats = self_chats.exclude(
            pk__in=excluded_chats
        ).prefetch_related('starter', 'receiver')
        return chats

    def add_friend(self, user):
        FriendInvite(sender=self, receiver=user).save()

    def del_friend(self, user):
        friendship = IsFriendsWith.objects.filter(
            Q(user1=self, user2=user) |
            Q(user1=user, user2=self)
        )
        if friendship.exists():
            friendship[0].delete()

    def block_user(self, user):
        IsBlockedBy(blocker=self, blocked=user).save()

    def unblock_user(self, user):
        block = IsBlockedBy.objects.filter(Q(blocker=self, blocked=user))
        if block.exists():
            block[0].delete()

    def invite_to_game(self, user):
        game = Game(player1=self)
        game.save()
        try:
            GameInvite(sender=self, receiver=user, game=game).save()
            return game
        except Exception as e:
            game.delete()
            raise e
