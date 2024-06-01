import chat.views as views
from django.urls import path


urlpatterns = [
    path("chat/room/<int:id>/", views.chatRoom, name="chatRoom"),
    path("notifications/", views.notifications, name="notifications"),
    path(
        "chat/room/<int:id>/send-message",
        views.sendMessage,
        name="sendMessage"
    ),
]
