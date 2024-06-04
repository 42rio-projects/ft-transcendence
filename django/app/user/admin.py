from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from user.models import User
from relations.models import IsFriendsWith
from relations.models import IsBlockedBy


class IsFriendsWithInline(admin.TabularInline):
    model = IsFriendsWith
    fk_name = 'user1'


class IsBlockedByInline(admin.TabularInline):
    model = IsBlockedBy
    fk_name = 'blocker'


class UserAdm(UserAdmin):
    inlines = [IsFriendsWithInline, IsBlockedByInline]


admin.site.register(User, UserAdm)
