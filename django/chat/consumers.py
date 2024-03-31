import json
import chat.models as models
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
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

    async def chat_message(self, event):
        """Function called when websocket receives message from group"""
        await self.send(text_data=json.dumps(event))


@database_sync_to_async
def get_chat(id):
    chat = models.Chat.objects.get(pk=id)
    return chat


@sync_to_async
def is_in_chat(user, chat):
    if user != chat.starter and user != chat.receiver:
        return False
    return True
