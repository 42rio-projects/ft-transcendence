from django.urls import path
from . import views
from django.conf import settings
from django.conf.urls.static import static
from user import views

urlpatterns = [
    path('profile/', views.profile, name='profile'),
    path('login/', views.login, name='login'),
    path('register/', views.register, name='register'),
    path('logout/', views.logout, name='logout'),
    path('upload_avatar', views.upload_avatar, name='upload_avatar'),
    path('change_password', views.change_password, name='change_password'),
    path('edit_profile/', views.edit_profile, name='edit_profile'),

    path('email_verify_code/', views.email_verify_code, name='email_verify_code'),
    path('email_verify_check/', views.email_verify_check, name='email_verify_check'),

    path('email_change/', views.email_change, name='email_change'),
    path('email_change_check/', views.email_change_check, name='email_change_check'),

    path("friends/", views.friends, name="friendsIndex"),
    path("friends/friendlist/", views.friendlist, name="friendList"),
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
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)