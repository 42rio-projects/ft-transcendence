from channels.generic.websocket import AsyncWebsocketConsumer
import json


class localGameCosumer(AsyncWebsocketConsumer):

    async def connect(self):
        await self.accept()

    async def disconnect(self, close_code):
        pass

    async def receive(self, text_data):
        data_json = json.loads(text_data)
        direction = data_json['move']
        await self.send(text_data=json.dumps(
            {"move": direction}
        ))


class onlineGameCosumer(AsyncWebsocketConsumer):

    async def connect(self):
        # add to game group
        await self.accept()

    async def disconnect(self, close_code):
        pass

    async def receive(self, text_data):
        pass
