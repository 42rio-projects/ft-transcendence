from django.urls import path
from . import views

urlpatterns = [
    path('friends/', views.friends),
    path('friends/invites-sent/', views.friend_invites_sent),
    path('friends/invites-received/', views.friend_invites_received),
    path('friends/block-list/', views.block_list),
    path('search-user/', views.search_user),

    # Temporary routes for adding/blocking users
    path('friends/send-invite/', views.send_friend_invites),
    path('friends/block/', views.block_user),
]
