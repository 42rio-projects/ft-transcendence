from django.urls import path
from pong import views

urlpatterns = [
    path('', views.index, name='index'),
    path('main/', views.main, name='main'),
    path('game-menu/', views.gameMenu, name='gameMenu'),
    path('local-game/', views.localGame, name='localGame'),
    path('online-game/', views.onlineGame, name='onlineGame'),
]
