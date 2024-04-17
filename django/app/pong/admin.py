from django.contrib import admin
import pong.models as models

# Register your models here.

admin.site.register(models.Game)
admin.site.register(models.Tournament)
admin.site.register(models.Round)
admin.site.register(models.Score)
