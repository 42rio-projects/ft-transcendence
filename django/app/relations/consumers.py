import json

from channels.generic.websocket import AsyncWebsocketConsumer


class statusConsumer(AsyncWebsocketConsumer):
    online_users = []

    async def connect(self):
        """Accept connection and broadcast new online list"""
        await self.channel_layer.group_add('status', self.channel_name)
        await self.accept()
        await self.send(text_data=json.dumps(
            {"online_users": self.online_users})
        )
        self.user = self.scope['user']
        self.online_users.append(self.user.username)
        await self.channel_layer.group_send(
            'status',
            {
                'type': 'user.connected',
                'username': self.user.username
            }
        )

    async def disconnect(self, close_code):
        self.online_users.remove(self.user.username)
        await self.channel_layer.group_send(
            'status',
            {
                'type': 'user.disconnected',
                'username': self.user.username
            }
        )
        await self.channel_layer.group_discard('satus', self.channel_name)

    async def receive(self, text_data):
        pass

    async def status_update(self, event):
        """Send updated online list to websocket"""
        await self.send(text_data=json.dumps(
            {"online_users": self.online_users})
        )

    async def user_connected(self, event):
        """Send updated online list to websocket"""
        username = event['username']
        if username == self.user.username:
            pass
        else:
            await self.send(text_data=json.dumps({"connected_user": username}))

    async def user_disconnected(self, event):
        """Send updated online list to websocket"""
        username = event['username']
        if username == self.user.username:
            pass
        else:
            await self.send(
                text_data=json.dumps({"disconnected_user": username})
            )
