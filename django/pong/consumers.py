from channels.generic.websocket import AsyncWebsocketConsumer
import json
import asyncio


class localGameCosumer(AsyncWebsocketConsumer):
    BAR_UNIT = 1
    BAR_UPPERBOUND = 80
    BAR_LOWERBOUND = 0

    async def connect(self):
        await self.set_initial_values()
        await self.accept()

    async def disconnect(self, close_code):
        self.interval_task.cancel()
        pass

    async def receive(self, text_data):
        data_json = json.loads(text_data)
        if 'start' in data_json:
            self.interval_task = asyncio.create_task(self.update_game())
            return
        elif 'stop' in data_json and self.interval_task:
            self.interval_task.cancel()
            await self.set_initial_values()
            return
        try:
            p1_direction = data_json['l']
            p2_direction = data_json['r']
        except KeyError:
            await self.send(text_data=json.dumps(
                {"status": "invalid", "message": "Invalid JSON received"}
            ))
            return
        self.p1_move = p1_direction
        self.p2_move = p2_direction
        await self.send(text_data=json.dumps(
            {"status": "received"}
        ))

    async def update_game(self):
        while True:
            await asyncio.sleep(0.016)
            if self.p1_move:
                if self.p1_move == 'd' and self.p1_pos < self.BAR_UPPERBOUND:
                    self.p1_pos += self.BAR_UNIT
                elif self.p1_move == 'u' and self.p1_pos > self.BAR_LOWERBOUND:
                    self.p1_pos -= self.BAR_UNIT
                self.p1_move = None
            if self.p2_move:
                if self.p2_move == 'd' and self.p2_pos < self.BAR_UPPERBOUND:
                    self.p2_pos += self.BAR_UNIT
                elif self.p2_move == 'u' and self.p2_pos > self.BAR_LOWERBOUND:
                    self.p2_pos -= self.BAR_UNIT
                self.p2_move = None
            try:
                await self.send(text_data=json.dumps(
                    {
                        "p1": self.p1_pos,
                        "p2": self.p2_pos
                    }
                ))
            except Exception:
                break

    async def set_initial_values(self):
        self.p1_pos = 50
        self.p2_pos = 50
        self.p1_move = None
        self.p2_move = None
        self.interval_task = None


class onlineGameCosumer(AsyncWebsocketConsumer):

    async def connect(self):
        # add to game group
        await self.accept()

    async def disconnect(self, close_code):
        pass

    async def receive(self, text_data):
        pass
