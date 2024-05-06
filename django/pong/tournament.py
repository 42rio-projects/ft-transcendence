import json
from django.template.loader import render_to_string

import logging
logging.basicConfig(level='INFO')
# logging.info('Example')

UPPER_PLAYER_LIMIT = 16
LOWER_PLAYER_LIMIT = 4


class LocalTournament():
    def __init__(self, socket):
        super().__init__()
        self.socket = socket
        self.players = set()

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

    async def start(self):
        if len(self.players) < LOWER_PLAYER_LIMIT:
            await self.send_message(
                {"status": "warning", "content": "Not enough players to start"}
            )
        else:
            await self.send_message({"status": "started"})
