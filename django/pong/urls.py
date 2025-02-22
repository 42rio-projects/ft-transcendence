from django.urls import path
from pong import views

urlpatterns = [
    path('', views.index),
    path('pong/', views.pong, name='pongMenu'),
    path('pong/local-game/', views.localGame),
    path(
        'pong/online-game/<int:game_id>/', views.onlineGame, name='onlineGame'
    ),
    path(
        'pong/local-tournament/', views.localTournament, name='localTournament'
    ),
    path(
        "pong/online-tournament/menu",
        views.tournamentMenu,
        name="tournamentMenu"
    ),
    path(
        'pong/online-tournament/<int:tournament_id>/',
        views.onlineTournament,
        name='onlineTournament'
    ),
    path(
        'pong/online-tournament/<int:tournament_id>/invite',
        views.inviteToTournament,
        name='inviteToTournament'
    ),
    path(
        'pong/online-tournament/<int:tournament_id>/cancel',
        views.cancelTournament,
        name='cancelTournament'
    ),
]
