import json
import random
from django.template.loader import render_to_string

UPPER_PLAYER_LIMIT = 16
LOWER_PLAYER_LIMIT = 4


class LocalTournament():
    def __init__(self, socket):
        super().__init__()
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
        if previous_size >= UPPER_PLAYER_LIMIT:
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

    async def render_next_game(self, loser=None):
        if loser:
            if loser == "player1":
                self.losers.add(self.currentGame[0])
            elif loser == "player2":
                self.losers.add(self.currentGame[1])
        if len(self.games) == 0:
            self.form_round()
        if self.winner is not None:
            html = self.get_result_html()
        else:
            html = self.get_game_html()
        await self.send_message({"status": "next_game", "html": html})

    async def start(self):
        if len(self.players) < LOWER_PLAYER_LIMIT:
            await self.send_message(
                {"status": "warning", "content": "Not enough players to start"}
            )
        else:
            await self.send_message({"status": "started"})
            await self.render_next_game()
