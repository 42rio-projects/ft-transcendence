from django.urls import path

from relations import views

urlpatterns = [
    path("friends/", views.friends_index),

    path("friends/friend-list/", views.friend_list),
    path("friends/remove/<int:user_id>/", views.remove_friend),

    path("friends/invites-sent/", views.friend_invites_sent),
    path("friends/send-invite/", views.send_friend_invites),
    path("friends/cancel-invite/<int:invite_id>/", views.cancel_friend_invite),

    path("friends/invites-received/", views.friend_invites_received),
    path("friends/respond-invite/<int:invite_id>/", views.respond_friend_invite),

    path("friends/block-list/", views.block_list),
    path("friends/block/", views.block_user),
    path("friends/unblock/<int:user_id>/", views.unblock_user),
]
