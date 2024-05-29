from django.urls import path
from pong import views

urlpatterns = [
    path('', views.index),
    path('pong/', views.pong),
    path('pong/local-game/', views.localGame),
    path(
        'pong/online-game/<int:game_id>/', views.onlineGame, name='onlineGame'
    ),
    path(
        'pong/local-tournament/', views.localTournament, name='localTournament'
    ),
    path("game-invites/", views.gameInvites, name="gameInvites"),
    path(
        "game-invites/respond-invite/<int:invite_id>/",
        views.respondGameInvite,
        name="respondGameInvite"
    ),
    path('tournament-menu/', views.tournamentMenu, name='tournamentMenu'),
    path(
        "tournament-invites/",
        views.tournamentInvites,
        name="tournamentInvites"
    ),
    path(
        "tournament-invites/respond-invite/<int:invite_id>/",
        views.respondTournamentInvite,
        name="respondTournamentInvite"
    ),
    path(
        'online-tournament/create',
        views.createTournament,
        name='createTournament'
    ),
    path(
        'online-tournament/<int:tournament_id>/',
        views.onlineTournament,
        name='onlineTournament'
    ),
    path(
        'online-tournament/<int:tournament_id>/invite',
        views.inviteToTournament,
        name='inviteToTournament'
    ),
    path(
        'online-tournament/<int:tournament_id>/cancel',
        views.cancelTournament,
        name='cancelTournament'
    ),
]
