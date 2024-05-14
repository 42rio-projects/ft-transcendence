import json
import random
import asyncio
from channels.layers import get_channel_layer
from django.template.loader import render_to_string
from channels.db import database_sync_to_async

# from pong.models import Tournament, UPPER_PLAYER_LIMIT, LOWER_PLAYER_LIMIT
import pong.models as models


class LocalTournament():
    def __init__(self, socket):
        self.socket = socket
        self.players = set()
        self.games = []
        self.currentGame = None
        self.losers = set()
        self.winner = None

    async def send_message(self, data):
        await self.socket.send(text_data=json.dumps(data))

    async def add_player(self, player):
        previous_size = len(self.players)
        if previous_size >= models.UPPER_PLAYER_LIMIT:
            await self.send_message(
                {"status": "warning", "content": "Player limit reached"}
            )
            return
        self.players.add(player)
        html = render_to_string('pong/local_player.html', {'alias': player})
        if previous_size < len(self.players):
            await self.send_message({"status": "new_player", "html": html})

    async def remove_player(self, player):
        try:
            self.players.discard(player)
            await self.send_message(
                {"status": "removed_player", "alias": player}
            )
        except Exception:
            return

    def get_game_html(self):
        final = True if len(self.players) == 2 else False
        self.currentGame = self.games.pop()
        html = render_to_string(
            'pong/local_game.html',
            {
                'player1': self.currentGame[0],
                'player2': self.currentGame[1],
                'tournament': True,
                'final': final
            }
        )
        return html

    def get_result_html(self):
        html = render_to_string(
            'pong/tournament_result.html', {'winner': self.winner}
        )
        return html

    def form_round(self):
        self.players -= self.losers
        self.losers.clear()
        if len(self.players) == 1:
            self.winner = self.players.pop()
            return
        players = list(self.players)
        random.shuffle(players)
        self.games = list(zip(players[::2], players[1::2]))

    async def render_next_game(self, winner=None):
        if winner:
            if winner == self.currentGame[0]:
                self.losers.add(self.currentGame[1])
            elif winner == self.currentGame[1]:
                self.losers.add(self.currentGame[0])
        if len(self.games) == 0:
            self.form_round()
        if self.winner is not None:
            html = self.get_result_html()
        else:
            html = self.get_game_html()
        await self.send_message({"status": "next_game", "html": html})

    async def start(self):
        if len(self.players) < models.LOWER_PLAYER_LIMIT:
            await self.send_message(
                {"status": "warning", "content": "Not enough players to start"}
            )
        else:
            await self.send_message({"status": "started"})
            await self.render_next_game()


class OnlineTournament():
    channel_layer = get_channel_layer()

    def __init__(self, socket):
        self.socket = socket
        self.tournament_id = socket.tournament_id
        self.room_group_name = socket.room_group_name

    @database_sync_to_async
    def cancel_tournament(self):
        self.tournament.cancel()

    @database_sync_to_async
    def refresh_tournament(self):
        self.tournament.refresh()

    @database_sync_to_async
    def save_tournament(self):
        self.tournament.save()

    @database_sync_to_async
    def start_tournament(self):
        self.tournament.start()

    @database_sync_to_async
    def get_tournament(self):
        self.tournament = models.Tournament.objects.prefetch_related(
            'admin', 'players').get(pk=self.tournament_id)

    async def send_message(self, json):
        await self.channel_layer.group_send(
            self.room_group_name, {"type": "tournament.update", "json": json}
        )

    def get_result_html(self):
        pass

    def form_round(self):
        pass

    async def start(self):
        await self.start_tournament()
        html = render_to_string(
            'pong/online_tournament.html', {"tournament": self.tournament}
        )
        await self.send_message({"status": "started", "html": html})

    async def timeout(self):
        await asyncio.sleep(models.TOURNAMENT_START_LIMIT)
        await self.refresh_tournament()
        if self.tournament.started is False:
            await self.cancel_tournament()

    def set_timer(self):
        if self.tournament.started is False:
            asyncio.create_task(self.timeout())

    def is_admin(self, user):
        if self.tournament.admin == user:
            return True
        return False
