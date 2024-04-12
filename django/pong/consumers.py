from channels.generic.websocket import AsyncWebsocketConsumer
import json
import asyncio

X_SPEED_LIMIT = 4
Y_SPEED_LIMIT = 2
SPEED_COUNTER = 5
TICK_RATE = 1 / 60
BALL_SPEED = 1
BAR_SPEED = 1
BAR_HEIGHT = 20
GAME_HEIGHT = 100
GAME_WIDTH = 200


class GameCosumer(AsyncWebsocketConsumer):
    BAR_UPPERBOUND = GAME_HEIGHT - BAR_HEIGHT
    BAR_LOWERBOUND = 0
    BALL_UPPERBOUND = GAME_HEIGHT
    BALL_LOWERBOUND = 0
    BALL_RIGHTBOUND = GAME_WIDTH
    BALL_LEFTBOUND = 0

    async def update_game(self):
        while True:
            await asyncio.sleep(TICK_RATE)
            await self.move_players()
            await self.move_ball()
            if (self.speed_countdown == 0 and
                    abs(self.ball_x_speed) < X_SPEED_LIMIT):
                self.ball_x_speed *= 2
                self.speed_countdown = SPEED_COUNTER
            try:
                await self.send(text_data=json.dumps(
                    {
                        "p1": self.p1_pos,
                        "p2": self.p2_pos,
                        "bx": self.ball_x,
                        "by": self.ball_y
                    }
                ))
            except Exception:
                break

    async def move_players(self):
        if self.p1_move:
            if self.p1_move == 'd' and self.p1_pos < self.BAR_UPPERBOUND:
                self.p1_pos += BAR_SPEED
            elif self.p1_move == 'u' and self.p1_pos > self.BAR_LOWERBOUND:
                self.p1_pos -= BAR_SPEED
        if self.p2_move:
            if self.p2_move == 'd' and self.p2_pos < self.BAR_UPPERBOUND:
                self.p2_pos += BAR_SPEED
            elif self.p2_move == 'u' and self.p2_pos > self.BAR_LOWERBOUND:
                self.p2_pos -= BAR_SPEED

    async def move_ball(self):
        new_x = self.ball_x + self.ball_x_speed
        new_y = self.ball_y + self.ball_y_speed
        scored = await self.check_horizontal_collision(new_x, new_y)
        if scored:
            await self.set_initial_values()
            return
        if new_y > self.BALL_UPPERBOUND or new_y < self.BALL_LOWERBOUND:
            self.ball_y_speed = self.ball_y_speed * -1
            new_y = self.ball_y + self.ball_y_speed
        self.ball_y = new_y

    async def check_horizontal_collision(self, new_x, new_y):
        if new_x <= self.BALL_LEFTBOUND + 2:
            if new_y >= self.p1_pos and new_y <= self.p1_pos + BAR_HEIGHT:
                self.ball_x_speed *= -1
                self.speed_countdown -= 1
                new_x = self.ball_x + self.ball_x_speed
                if self.p1_move:
                    if self.p1_move == 'd':
                        new_speed = self.ball_y_speed + BALL_SPEED
                    elif self.p1_move == 'u':
                        new_speed = self.ball_y_speed - BALL_SPEED
                    if abs(new_speed) < Y_SPEED_LIMIT:
                        self.ball_y_speed = new_speed
            else:
                # P2 Scores
                return True
        elif new_x >= self.BALL_RIGHTBOUND - 2:
            if new_y >= self.p2_pos and new_y <= self.p2_pos + BAR_HEIGHT:
                self.ball_x_speed *= -1
                self.speed_countdown -= 1
                new_x = self.ball_x + self.ball_x_speed
                if self.p2_move:
                    if self.p2_move == 'd':
                        new_speed = self.ball_y_speed + BALL_SPEED
                    elif self.p2_move == 'u':
                        new_speed = self.ball_y_speed - BALL_SPEED
                    if abs(new_speed) < Y_SPEED_LIMIT:
                        self.ball_y_speed = new_speed
            else:
                # P1 Scores
                return True
        else:
            self.ball_x = new_x
            return False

    async def set_initial_values(self):
        self.p1_pos = 40
        self.p2_pos = 40
        self.ball_x = 100
        self.ball_y = 50
        self.ball_x_speed = BALL_SPEED * -1
        self.ball_y_speed = 0
        self.p1_move = None
        self.p2_move = None
        self.speed_countdown = SPEED_COUNTER
        self.interval_task = None


class LocalGameCosumer(GameCosumer):

    async def connect(self):
        await self.set_initial_values()
        await self.accept()

    async def disconnect(self, close_code):
        if self.interval_task:
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
        if p1_direction == 'null':
            self.p1_move = None
        else:
            self.p1_move = p1_direction
        if p2_direction == 'null':
            self.p2_move = None
        else:
            self.p2_move = p2_direction


class OnlineGameCosumer(AsyncWebsocketConsumer):

    async def connect(self):
        # add to game group
        await self.accept()

    async def disconnect(self, close_code):
        pass

    async def receive(self, text_data):
        pass
