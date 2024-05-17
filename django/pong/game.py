import json
import asyncio
from channels.layers import get_channel_layer
from channels.db import database_sync_to_async
from django.template.loader import render_to_string

from pong.models import Game as GameModel


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
    SCORE_LIMIT = 2

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

    def pos_to_json(self):
        return (
            {
                "p1": self.p1_pos,
                "p2": self.p2_pos,
                "bx": self.ball_x,
                "by": self.ball_y
            }
        )

    def score_to_json(self, nbr=None):
        if nbr is None:
            return (
                {"status": "score", "p1": self.p1_score, "p2": self.p2_score}
            )
        else:
            return ({"status": "score", "p1": nbr, "p2": nbr})

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
            self.p1_score >= self.SCORE_LIMIT or
            self.p2_score >= self.SCORE_LIMIT
        )


class Game:
    def __init__(self):
        self.info = GameInfo()
        self.interval_task = None

    async def send_message(self, data):
        pass

    async def player_scored(self, player):
        pass

    async def send_pos(self):
        data = self.info.pos_to_json()
        await self.send_message(data)

    async def send_score(self):
        data = self.info.score_to_json()
        await self.send_message(data)

    def is_running(self):
        return (self.interval_task is not None)

    async def countdown(self, secs):
        while secs > 0:
            await self.send_message(self.info.score_to_json(secs))
            secs -= 1
            await asyncio.sleep(1)

    async def countdown_and_update(self):
        await self.send_pos()
        await self.countdown(5)
        await self.send_score()
        await self.update_game()

    def start(self):
        if (self.is_running()):
            return
        self.info.set_initial_values()
        self.interval_task = asyncio.create_task(self.countdown_and_update())

    async def stop(self):
        if not self.is_running():
            return
        self.interval_task.cancel()
        self.interval_task = None
        await self.send_message({"status": "finished"})

    async def update_game(self):
        while self.info.finished() is False:
            await asyncio.sleep(TICK_RATE)
            await self.move_players()
            await self.move_ball()
            if self.info.ball_should_speed_up():
                self.info.ball_x_speed *= 2
                self.info.speed_countdown = SPEED_COUNTER
            try:
                await self.send_pos()
            except Exception:
                break

    async def move_players(self):
        if self.info.p1_move:
            if self.info.p1_can_move_down():
                self.info.p1_pos += BAR_SPEED
            elif self.info.p1_can_move_up():
                self.info.p1_pos -= BAR_SPEED
        if self.info.p2_move:
            if self.info.p2_can_move_down():
                self.info.p2_pos += BAR_SPEED
            elif self.info.p2_can_move_up():
                self.info.p2_pos -= BAR_SPEED

    async def move_ball(self):
        new_x = self.info.ball_x + self.info.ball_x_speed
        new_y = self.info.ball_y + self.info.ball_y_speed
        scored = await self.check_horizontal_collision(new_x, new_y)
        if scored:
            self.info.set_initial_game_pos()
            return
        if self.info.pos_is_out_of_vertical_bounds(new_y):
            self.info.ball_y_speed *= -1
            new_y = self.info.ball_y + self.info.ball_y_speed
        self.info.ball_y = new_y

    async def check_horizontal_collision(self, new_x, new_y):
        if new_x <= self.info.BALL_LEFTBOUND:
            if self.info.ball_hits_p1(new_y):
                await self.bounce_ball_off_player(1)
            else:
                await self.player_scored(2)
                return True
        elif new_x >= self.info.BALL_RIGHTBOUND:
            if self.info.ball_hits_p2(new_y):
                await self.bounce_ball_off_player(2)
            else:
                await self.player_scored(1)
                return True
        else:
            self.info.ball_x = new_x
            return False

    async def bounce_ball_off_player(self, player):
        self.info.ball_x_speed *= -1
        self.info.speed_countdown -= 1
        move = self.info.p1_move if player == 1 else self.info.p2_move
        if move:
            if move == 'd':
                new_speed = self.info.ball_y_speed + BALL_SPEED
            elif move == 'u':
                new_speed = self.info.ball_y_speed - BALL_SPEED
            if abs(new_speed) < Y_SPEED_LIMIT:
                self.info.ball_y_speed = new_speed


class LocalGame(Game):
    def __init__(self, socket):
        super().__init__()
        self.socket = socket

    async def send_message(self, data):
        await self.socket.send(text_data=json.dumps(data))

    async def player_scored(self, player):
        if player == 1:
            self.info.p1_score += 1
        elif player == 2:
            self.info.p2_score += 1
        await self.send_score()
        if self.info.finished():
            await self.stop()

    async def render_result(self, player1, player2, tournament):
        winner = (
            player1 if self.info.p1_score > self.info.p2_score else player2
        )
        html = render_to_string(
            'pong/game/local/result.html',
            {
                'player1': player1,
                'player2': player2,
                'player1_points': self.info.p1_score,
                'player2_points': self.info.p2_score,
                'winner': winner,
                'tournament': tournament
            }
        )
        await self.send_message({"status": "result", "html": html})


class OnlineGame(Game):
    channel_layer = get_channel_layer()

    def __init__(self, socket):
        super().__init__()
        self.game_id = socket.game_id
        self.room_group_name = socket.room_group_name
        self.p1_connected = False
        self.p2_connected = False

    async def send_message(self, json):
        await self.channel_layer.group_send(
            self.room_group_name, {"type": "game.update", "json": json}
        )

    async def send_start_message(self):
        await self.send_message({"status": "started"})

    async def stop(self):
        super().stop()
        if self.game_model.round:
            await self.game_model.round.try_advance()

    async def player_scored(self, player):
        if player == 1:
            self.info.p1_score += 1
        elif player == 2:
            self.info.p2_score += 1
        await self.send_score()
        await self.update_score()
        if self.info.finished():
            await self.stop()
            await self.channel_layer.group_send(
                self.room_group_name, {"type": "game.stopped"}
            )

    def second_player_has_not_connected(self):
        return (
            self.game_model.player2 is None and
            self.game_model.finished is False
        )

    async def player_disconnected(self, player):
        if self.second_player_has_not_connected():
            await self.delete_game()
            return
        if player == 1:
            self.game_model.winner = self.game_model.player2
        elif player == 2:
            self.game_model.winner = self.game_model.player1
        self.game_model.finished = True
        await self.save_game()
        await self.stop()

    @database_sync_to_async
    def delete_game(self):
        self.game_model.delete()

    @database_sync_to_async
    def save_game(self):
        self.game_model.save()

    @database_sync_to_async
    def get_game(self):
        self.game_model = GameModel.objects.prefetch_related(
            'player1', 'player2', 'round').get(pk=self.game_id)

    async def update_score(self):
        self.game_model.player1_points = self.info.p1_score
        self.game_model.player2_points = self.info.p2_score
        if self.info.p1_score == self.info.SCORE_LIMIT:
            self.game_model.winner = self.game_model.player1
            self.game_model.finished = True
        elif self.info.p2_score == self.info.SCORE_LIMIT:
            self.game_model.winner = self.game_model.player2
            self.game_model.finished = True
        await self.save_game()

    def get_player(self, player):
        if player == self.game_model.player1:
            p = 1
            self.p1_connected = True
        elif player == self.game_model.player2:
            p = 2
            self.p2_connected = True
        else:
            raise Exception("Unauthorized")
        if (self.p1_connected and self.p2_connected):
            asyncio.create_task(self.send_start_message())
            self.start()
        return p
