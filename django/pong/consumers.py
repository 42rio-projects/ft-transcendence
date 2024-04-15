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


class GameInfo:
    BAR_UPPERBOUND = GAME_HEIGHT - BAR_HEIGHT
    BAR_LOWERBOUND = 0
    BALL_UPPERBOUND = GAME_HEIGHT
    BALL_LOWERBOUND = 0
    BALL_RIGHTBOUND = GAME_WIDTH - 2
    BALL_LEFTBOUND = 2
    SCORE_LIMIT = 7

    def __init__(self):
        self.set_initial_values()
        pass

    def set_initial_values(self):
        self.set_initial_game_pos()
        self.p1_score = 0
        self.p2_score = 0

    def set_initial_game_pos(self):
        self.p1_pos = 40
        self.p2_pos = 40
        self.ball_x = 100
        self.ball_y = 50
        self.ball_x_speed = BALL_SPEED * -1
        self.ball_y_speed = 0
        self.p1_move = None
        self.p2_move = None
        self.speed_countdown = SPEED_COUNTER

    def info_to_json(self):
        return json.dumps(
            {
                "p1": self.p1_pos,
                "p2": self.p2_pos,
                "bx": self.ball_x,
                "by": self.ball_y
            }
        )

    def score_to_json(self):
        return json.dumps(
            {"status": "score", "p1": self.p1_score, "p2": self.p2_score}
        )

    def p1_can_move_down(self):
        return (self.p1_move == 'd' and self.p1_pos < self.BAR_UPPERBOUND)

    def p1_can_move_up(self):
        return (self.p1_move == 'u' and self.p1_pos > self.BAR_LOWERBOUND)

    def p2_can_move_down(self):
        return (self.p2_move == 'd' and self.p2_pos < self.BAR_UPPERBOUND)

    def p2_can_move_up(self):
        return (self.p2_move == 'u' and self.p2_pos > self.BAR_LOWERBOUND)

    def pos_is_out_of_vertical_bounds(self, y):
        return (y > self.BALL_UPPERBOUND or y < self.BALL_LOWERBOUND)

    def ball_hits_p1(self, y):
        return (y >= self.p1_pos and y <= self.p1_pos + BAR_HEIGHT)

    def ball_hits_p2(self, y):
        return (y >= self.p2_pos and y <= self.p2_pos + BAR_HEIGHT)

    def ball_should_speed_up(self):
        return (
            self.speed_countdown == 0 and
            abs(self.ball_x_speed) < X_SPEED_LIMIT
        )

    def finished(self):
        return (
            self.p1_score == self.SCORE_LIMIT or
            self.p2_score == self.SCORE_LIMIT
        )


class GameCosumer(AsyncWebsocketConsumer):

    async def update_game(self):
        while True:
            await asyncio.sleep(TICK_RATE)
            await self.move_players()
            await self.move_ball()
            if self.game.ball_should_speed_up():
                self.game.ball_x_speed *= 2
                self.game.speed_countdown = SPEED_COUNTER
            try:
                await self.send(text_data=self.game.info_to_json())
            except Exception:
                break

    async def move_players(self):
        if self.game.p1_move:
            if self.game.p1_can_move_down():
                self.game.p1_pos += BAR_SPEED
            elif self.game.p1_can_move_up():
                self.game.p1_pos -= BAR_SPEED
        if self.game.p2_move:
            if self.game.p2_can_move_down():
                self.game.p2_pos += BAR_SPEED
            elif self.game.p2_can_move_up():
                self.game.p2_pos -= BAR_SPEED

    async def move_ball(self):
        new_x = self.game.ball_x + self.game.ball_x_speed
        new_y = self.game.ball_y + self.game.ball_y_speed
        scored = await self.check_horizontal_collision(new_x, new_y)
        if scored:
            self.game.set_initial_game_pos()
            return
        if self.game.pos_is_out_of_vertical_bounds(new_y):
            self.game.ball_y_speed *= -1
            new_y = self.game.ball_y + self.game.ball_y_speed
        self.game.ball_y = new_y

    async def check_horizontal_collision(self, new_x, new_y):
        if new_x <= self.game.BALL_LEFTBOUND:
            if self.game.ball_hits_p1(new_y):
                await self.bounce_ball_off_player(1)
            else:
                await self.player_scored(2)
                return True
        elif new_x >= self.game.BALL_RIGHTBOUND:
            if self.game.ball_hits_p2(new_y):
                await self.bounce_ball_off_player(2)
            else:
                await self.player_scored(1)
                return True
        else:
            self.game.ball_x = new_x
            return False

    async def bounce_ball_off_player(self, player):
        self.game.ball_x_speed *= -1
        self.game.speed_countdown -= 1
        move = self.game.p1_move if player == 1 else self.game.p2_move
        if move:
            if move == 'd':
                new_speed = self.game.ball_y_speed + BALL_SPEED
            elif move == 'u':
                new_speed = self.game.ball_y_speed - BALL_SPEED
            if abs(new_speed) < Y_SPEED_LIMIT:
                self.game.ball_y_speed = new_speed


class LocalGameCosumer(GameCosumer):

    async def connect(self):
        self.interval_task = None
        self.game = GameInfo()
        self.game.set_initial_game_pos()
        await self.accept()

    async def disconnect(self, close_code):
        if self.interval_task:
            self.interval_task.cancel()
        pass

    async def receive(self, text_data):
        data_json = json.loads(text_data)
        if 'start' in data_json:
            await self.start_game()
            return
        elif 'stop' in data_json and self.interval_task:
            self.stop_game()
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
            self.game.p1_move = None
        else:
            self.game.p1_move = p1_direction
        if p2_direction == 'null':
            self.game.p2_move = None
        else:
            self.game.p2_move = p2_direction

    async def player_scored(self, player):
        if player == 1:
            self.game.p1_score += 1
        elif player == 2:
            self.game.p2_score += 1
        await self.send(text_data=self.game.score_to_json())
        if self.game.finished():
            self.stop_game()

    async def start_game(self):
        if (self.interval_task):
            return
        self.game.set_initial_values()
        await self.send(text_data=self.game.score_to_json())
        self.interval_task = asyncio.create_task(self.update_game())

    def stop_game(self):
        self.interval_task.cancel()
        self.interval_task = None
        self.game.set_initial_game_pos()


class OnlineGameCosumer(AsyncWebsocketConsumer):

    async def connect(self):
        # add to game group
        await self.accept()

    async def disconnect(self, close_code):
        pass

    async def receive(self, text_data):
        pass
