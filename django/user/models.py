import sys
from channels.db import database_sync_to_async
from django.db import models
from django.contrib.auth.models import AbstractUser
from django.db.models import Q
from relations.models import IsFriendsWith
from relations.models import IsBlockedBy
from relations.models import FriendInvite
from chat.models import Chat, Message
from pong.models import Game, GameInvite
from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer

@async_to_sync
async def send_channel_message(group, message):
    channel_layer = get_channel_layer()
    await channel_layer.group_send(group, message,)


class User(AbstractUser):
    email_verified = models.BooleanField(default=False)
    friends = models.ManyToManyField(
        'self',
        through="relations.IsFriendsWith",
        symmetrical=True
    )
    nickname = models.CharField(max_length=255, unique=True, blank=True)
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

    def change_username(self, new_username):
        if (User.objects.filter(username=new_username).exists()):
            raise ValueError("Username already exists")
        if (len(new_username) < 3):
            raise ValueError("Username is too short")
        self.username = new_username
        self.save()

    def change_nickname(self, new_nickname):
        if (User.objects.filter(nickname=new_nickname).exists()):
            raise ValueError("Nickname already exists")
        if (len(new_nickname) < 3):
            raise ValueError("Nickname is too short")
        self.nickname = new_nickname
        self.save()

    def change_email(self, new_email):
        if (User.objects.filter(email=new_email).exists()):
            raise ValueError("Email already exists")
        if (len(new_email) < 3):
            raise ValueError("Email is too short")
        self.email = new_email
        self.email_verified = False
        self.save()

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

    def get_tournaments(self):
        admin = self.my_tournaments.all()
        player = self.tournaments.all()
        return admin.union(player)

    def get_games(self, filters=None):
        queryFilters = {}
        if filters and 'winner' in filters:
            queryFilters['winner'] = filters['winner']

        home_games = self.home_games.filter(**queryFilters).prefetch_related('player1','player2')
        away_games = self.away_games.filter(**queryFilters).prefetch_related('player1', 'player2')

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

    def all_tournaments(self):
        admin = self.my_tournaments.filter(Q(finished=False))
        player = self.tournaments.filter(Q(finished=False))
        tournaments = player.union(admin).all()
        return tournaments

    def current_player_tournaments(self):
        return self.tournaments.filter(Q(finished=False)).all()

    def current_admin_tournaments(self):
        return self.my_tournaments.filter(Q(finished=False)).all()

    def finished_player_tournaments(self):
        return self.my_tournaments.filter(Q(finished=True)).all()

    def finished_admin_tournaments(self):
        return self.my_tournaments.filter(Q(finished=True)).all()

    def notify(self, message):
        try:
            notifications = Chat.objects.get(starter=self, receiver=self)
        except Exception:
            notifications = Chat(starter=self, receiver=self)
            notifications.save()
        message = Message(sender=self, chat=notifications, content=message)
        message.save()
        send_channel_message(
            f'chat_{notifications.pk}',
            {'type': 'chat.message', 'id': message.pk}
        )

    @database_sync_to_async
    def a_notify(self, message):
        self.notify(message)

    def __str__(self):
        return (self.username)
