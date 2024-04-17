from django.urls import path

from relations import views

urlpatterns = [
    path("friends/", views.friends, name="friendsIndex"),
    path("friends/friendlist/", views.friendlist, name="friendList"),
    path("friends/blocklist/", views.blocklist, name="blockList"),
    path(
        "friends/exclude/<int:user_id>/",
        views.excludeFriend,
        name="excludeFriend"
    ),
    path(
        "friends/invites-sent/",
        views.friendInvitesSent,
        name="friendInvitesSent"
    ),
    path(
        "friends/invites-received/",
        views.friendInvitesReceived,
        name="friendInvitesReceived"
    ),
    path(
        "friends/respond-invite/<int:invite_id>/",
        views.respondFriendInvite,
        name="respondFriendInvite"
    ),
    path(
        "friends/cancel-invite/<int:invite_id>/",
        views.cancelFriendInvite,
        name="cancelFriendInvite"
    ),
    path(
        "friends/send-invites/",
        views.sendFriendInvites,
        name="sendFriendInvites"
    ),
    path("friends/block-user/", views.blockUser, name="blockUser"),
    path(
        "friends/unblock/<int:user_id>/",
        views.unblockUser,
        name="unblockUser"
    ),
]
