from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from channels.layers import get_channel_layer
import json
import asyncio

import pong.models as models
from pong.game import LocalGame, OnlineGame


class LocalGameCosumer(AsyncWebsocketConsumer):

    async def connect(self):
        self.game = LocalGame(self)
        await self.accept()

    async def disconnect(self, close_code):
        self.game.stop()

    def update_player_input(self, data):
        p1_direction = data['l']
        p2_direction = data['r']
        if p1_direction == 'null':
            self.game.info.p1_move = None
        else:
            self.game.info.p1_move = p1_direction
        if p2_direction == 'null':
            self.game.info.p2_move = None
        else:
            self.game.info.p2_move = p2_direction

    async def receive(self, text_data):
        data_json = json.loads(text_data)
        if 'start' in data_json:
            await self.game.start()
            return
        elif 'stop' in data_json and self.game.is_running():
            self.game.stop()
            return
        try:
            self.update_player_input(data_json)
        except KeyError:
            await self.send(text_data=json.dumps(
                {"status": "invalid", "message": "Invalid JSON received"}
            ))


async def testing_function(group_name):
    channel_layer = get_channel_layer()
    counter = 0
    while True:
        await asyncio.sleep(1)
        await channel_layer.group_send(
            group_name, {"type": "game.update", "counter": counter},
        )
        counter += 1


class OnlineGameCosumer(AsyncWebsocketConsumer):
    interval_tasks = {}

    async def connect(self):
        self.game_id = self.scope['url_route']['kwargs']['room_id']
        self.room_group_name = f'game_{self.game_id}'
        self.game = OnlineGame(self)
        await self.channel_layer.group_add(
            self.room_group_name, self.channel_name
        )
        await self.accept()

    async def disconnect(self, close_code):
        self.game.stop()
        await self.channel_layer.group_discard(
            self.room_group_name, self.channel_name
        )

    def update_player_input(self, data):
        pass

    async def receive(self, text_data):
        data_json = json.loads(text_data)
        if 'start' in data_json:
            await self.game.start()
            return
        elif 'stop' in data_json and self.game.is_running():
            self.game.stop()
            return
        try:
            self.update_player_input(data_json)
        except KeyError:
            await self.send(text_data=json.dumps(
                {"status": "invalid", "message": "Invalid JSON received"}
            ))

    async def game_update(self, event):
        await self.send(text_data=json.dumps(event["json"]))


# @ database_sync_to_async
# def get_game(id):
#     game = models.Game.objects.get(pk=id)
#     return game
