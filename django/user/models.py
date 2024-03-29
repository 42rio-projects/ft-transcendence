from django.db import models
from django.contrib.auth.models import AbstractUser
from django.db.models import Q

from relations.models import IsFriendsWith
from relations.models import IsBlockedBy
from relations.models import FriendInvite
from chat.models import Chat


class User(AbstractUser):
    friends = models.ManyToManyField(
        'self',
        through="relations.IsFriendsWith",
        symmetrical=True
    )
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
