from django.contrib import admin
import chat.models as models

admin.site.register(models.Chat)
admin.site.register(models.Message)
