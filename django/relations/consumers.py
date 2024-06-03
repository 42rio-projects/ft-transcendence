import json

from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from user.models import User


@database_sync_to_async
def get_user(pk):
    return User.objects.get(pk=pk)


@database_sync_to_async
def set_user_status(user, status):
    user.status = status
    user.save()


class statusConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        """Accept connection and broadcast user online status"""
        await self.accept()
        if not self.scope['user'].is_authenticated:
            await self.send(text_data=json.dumps({'type': 'no.login'}))
            self.close(True)
            return

        await self.channel_layer.group_add('status', self.channel_name)

        user = await get_user(self.scope['session'].get('_auth_user_id'))

        await set_user_status(user, 'Online')
        await self.channel_layer.group_send('status', {
            'type': 'user.status',
            'user_status': 'Online',
            'user_pk': user.pk
        })

    async def disconnect(self, simple_disconnect=False):
        """Broadcast user offline status"""
        if simple_disconnect:
            await self.channel_layer.group_discard('status', self.channel_name)
            return
        user = await get_user(self.scope['session'].get('_auth_user_id'))

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
