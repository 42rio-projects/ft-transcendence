from channels.generic.websocket import AsyncWebsocketConsumer
import json

from pong.game import LocalGame, OnlineGame
from pong.tournament import LocalTournament, OnlineTournament


class LocalGameCosumer(AsyncWebsocketConsumer):

    async def connect(self):
        self.game = LocalGame(self)
        await self.accept()

    async def disconnect(self, close_code):
        await self.game.stop()

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
        data = json.loads(text_data)
        if 'start' in data:
            self.game.start()
            return
        elif 'stop' in data:
            await self.game.stop()
            return
        elif 'render' in data:
            await self.game.render_result(
                data["player1"], data["player2"], data["tournament"]
            )
            return
        try:
            self.update_player_input(data)
        except KeyError:
            await self.send(text_data=json.dumps(
                {"status": "invalid", "message": data}
            ))


class OnlineGameCosumer(AsyncWebsocketConsumer):
    online_games = {}

    async def connect(self):
        self.game_id = self.scope['url_route']['kwargs']['room_id']
        self.room_group_name = f'game_{self.game_id}'
        if self.game_id in self.online_games:
            self.game = self.online_games[self.game_id]
        else:
            self.online_games[self.game_id] = OnlineGame(self)
            self.game = self.online_games[self.game_id]
        await self.game.get_game()
        if self.game.game_model.finished:
            del self.online_games[self.game_id]
            return
        self.player = self.game.get_player(self.scope['user'])
        await self.channel_layer.group_add(
            self.room_group_name, self.channel_name
        )
        await self.accept()

    async def disconnect(self, close_code):
        if self.game_id in self.online_games:
            await self.game.player_disconnected(self.player)
            del self.online_games[self.game_id]
        await self.channel_layer.group_discard(
            self.room_group_name, self.channel_name
        )

    def update_player_input(self, data):
        direction = data['d']
        if direction == 'null':
            if self.player == 1:
                self.game.info.p1_move = None
            elif self.player == 2:
                self.game.info.p2_move = None
        else:
            if self.player == 1:
                self.game.info.p1_move = direction
            elif self.player == 2:
                self.game.info.p2_move = direction

    async def receive(self, text_data):
        data_json = json.loads(text_data)
        try:
            self.update_player_input(data_json)
        except KeyError:
            await self.send(text_data=json.dumps(
                {"status": "invalid", "message": "Invalid JSON received"}
            ))

    async def game_update(self, event):
        await self.send(text_data=json.dumps(event["json"]))

    async def game_stopped(self, event):
        if self.game_id in self.online_games:
            del self.online_games[self.game_id]


class LocalTournamentCosumer(AsyncWebsocketConsumer):

    async def connect(self):
        await self.accept()
        self.tournament = LocalTournament(self)

    async def disconnect(self, close_code):
        pass

    async def receive(self, text_data):
        data = json.loads(text_data)
        try:
            action = data['action']
            if action == 'add_player':
                await self.tournament.add_player(data['alias'])
            elif action == 'remove_player':
                await self.tournament.remove_player(data['alias'])
            elif action == 'start_tournament':
                await self.tournament.start()
            elif action == 'next_game':
                await self.tournament.render_next_game(data['winner'])
        except Exception:
            await self.send(text_data=json.dumps(
                {"status": "excepted", "data_received": data}
            ))


class OnlineTournamentCosumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.tournament_id = self.scope['url_route']['kwargs']['room_id']
        self.room_group_name = f'tournament_{self.tournament_id}'
        self.tournament = OnlineTournament(self)
        await self.tournament.get_tournament()
        self.admin = self.tournament.is_admin(self.scope['user'])
        await self.channel_layer.group_add(
            self.room_group_name, self.channel_name
        )
        await self.accept()

    async def disconnect(self, close_code):
        pass

    async def receive(self, text_data):
        data = json.loads(text_data)
        try:
            action = data['action']
            if action == 'get_status':
                await self.send(text_data=json.dumps({"is admin": self.admin}))
            else:
                raise Exception()
        except Exception:
            await self.send(text_data=json.dumps(
                {"status": "excepted", "data_received": data}
            ))

    async def tournament_update(self, event):
        await self.send(text_data=json.dumps(event["json"]))
