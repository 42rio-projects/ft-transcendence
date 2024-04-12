from django.urls import re_path

from pong import consumers

urlpatterns = [
    re_path(r"ws/local-game/", consumers.LocalGameCosumer.as_asgi()),
    re_path(r"ws/online-game/", consumers.OnlineGameCosumer.as_asgi()),
]
