import json

from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async


@database_sync_to_async
def set_user_status(user, status):
    user.status = status
    user.save()


class statusConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        """Accept connection and broadcast user online status"""
        user = self.scope['user']

        if not user.is_authenticated:
            return

        await self.accept()
        await self.channel_layer.group_add('status', self.channel_name)

        await set_user_status(user, 'Online')
        await self.channel_layer.group_send('status', {
            'type': 'user.status',
            'user_status': 'Online',
            'user_pk': user.pk
        })

    async def disconnect(self, close_code):
        """Broadcast user offline status"""
        user = self.scope['user']

        await set_user_status(user, 'Offline')
        await self.channel_layer.group_send('status', {
            'type': 'user.status',
            'user_status': 'Offline',
            'user_pk': user.pk
        })

        await self.channel_layer.group_discard('status', self.channel_name)

    async def user_status(self, event):
        """Send user status to all users"""
        await self.send(text_data=json.dumps(event))
