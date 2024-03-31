from django.contrib import admin

import relations.models as models

admin.site.register(models.IsFriendsWith)
admin.site.register(models.IsBlockedBy)
admin.site.register(models.FriendInvite)
