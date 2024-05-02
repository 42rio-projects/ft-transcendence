from django.urls import path
from pong import views

urlpatterns = [
    path('', views.index, name='index'),
    path('main/', views.main, name='main'),
    path('game-menu/', views.gameMenu, name='gameMenu'),
    path('local-game/', views.localGame, name='localGame'),
    path('online-game/<int:game_id>/', views.onlineGame, name='onlineGame'),
    path("game-invites/", views.gameInvites, name="gameInvites"),
    path(
        "game-invites/respond-invite/<int:invite_id>/",
        views.respondGameInvite,
        name="respondGameInvite"
    ),
]
