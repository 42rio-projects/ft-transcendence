import json
import chat.models as models
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from django.template.loader import render_to_string
from asgiref.sync import sync_to_async


class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        """Function called when websocket is trying to connect"""
        self.chat_id = self.scope['url_route']['kwargs']['room_id']
        self.room_group_name = f'chat_{self.chat_id}'
        self.chat = await get_chat(self.chat_id)
        self.user = self.scope['user']
        in_chat = await is_in_chat(self.user, self.chat)
        if not in_chat:
            self.close()
            return
        await self.channel_layer.group_add(
            self.room_group_name, self.channel_name
        )
        await self.accept()

    async def disconnect(self, close_code):
        """Function called when websocket is disconnected"""
        await self.channel_layer.group_discard(
            self.room_group_name, self.channel_name
        )

    async def receive(self, text_data):
        """Function called when websocket receives message from user"""
        data_json = json.loads(text_data)
        message_id = data_json['id']
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'chat.message',
                'id': message_id
            }
        )

    async def chat_message(self, data):
        """Function called when websocket receives message from group"""
        message_id = data['id']
        try:
            message = await get_message(message_id)
        except Exception:
            return
        context = {"message": message, "user": self.user}
        html = render_to_string('chat/message.html', context)
        await self.send(text_data=json.dumps({"html": html}))


@database_sync_to_async
def get_message(id):
    message = models.Message.objects.get(pk=id)
    return message


@database_sync_to_async
def get_chat(id):
    chat = models.Chat.objects.get(pk=id)
    return chat


@sync_to_async
def is_in_chat(user, chat):
    if user != chat.starter and user != chat.receiver:
        return False
    return True
