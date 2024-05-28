from django.urls import re_path

from . import consumers

urlpatterns = [
    re_path(r"wss/chat/(?P<room_id>\d+)/$", consumers.ChatConsumer.as_asgi()),
]
