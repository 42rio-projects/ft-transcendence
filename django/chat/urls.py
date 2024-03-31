import chat.views as views
from django.urls import path


urlpatterns = [
    path("chat/", views.chatIndex, name="chatIndex"),
    path("chat/list/", views.chatList, name="chatList"),
    path("chat/new-chat/", views.startChat, name="startChat"),
    path("chat/room/<int:id>/", views.chatRoom, name="chatRoom"),
    path("message/<int:id>/", views.message, name="message"),
]
