from django.urls import path
from . import views

urlpatterns = [
    path("", views.menu, name="menu"),
    path("game/", views.game, name="game"),
    path("api/users", views.UserEndpoint.as_view(), name="users"),
    path("api/games", views.GameEndpoint.as_view(), name="games"),
    path(
        "api/tournaments",
        views.TournamentEndpoint.as_view(),
        name="tournaments"
    ),
]
