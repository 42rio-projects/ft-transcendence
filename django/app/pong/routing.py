from django.urls import re_path

from pong import consumers

websocket_urlpatterns = [
    re_path(r"ws/local-game/", consumers.LocalGameCosumer.as_asgi()),
    re_path(
        r"ws/online-game/(?P<room_id>\d+)/$",
        consumers.OnlineGameCosumer.as_asgi()
    ),
    re_path(
        r"ws/local-tournament/",
        consumers.LocalTournamentCosumer.as_asgi()
    ),
    re_path(
        r"ws/online-tournament/(?P<room_id>\d+)/$",
        consumers.OnlineTournamentCosumer.as_asgi()
    ),
]
