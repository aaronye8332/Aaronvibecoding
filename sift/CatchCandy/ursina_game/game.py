from __future__ import annotations

import random
import sys
from typing import List

from ursina import *


app = Ursina()

# ----------------------------
# Configuration
# ----------------------------
WINDOW_SIZE = (1200, 800)
GROUND_SIZE = 24
PLAYABLE_BOUNDS = 10
PLAYER_SPEED = 8.0
CLOUD_SPEED = 2.0
GRAVITY = -14.0

# ----------------------------
# Utility helpers
# ----------------------------

def make_heart(position=(0, 0), scale=0.08):
    heart = Entity(model='quad', texture='white_cube', color=color.red)
    heart.model = Mesh(vertices=[(0, 0.5, 0), (0.4, 0.8, 0), (0.8, 0.5, 0), (0.8, 0, 0), (0.4, -0.3, 0), (0, 0, 0)],
                      triangles=[(0, 1, 2), (0, 2, 3), (0, 3, 4), (0, 4, 5)])
    heart.scale = scale
    heart.position = position
    return heart


class Player(Entity):
    def __init__(self):
        super().__init__(
            model=None,
            collider='box',
            scale=(1.0, 2.0, 1.0),
            color=color.white,
            position=(0, 1.1, 0),
        )
        self.bucket = Entity(parent=self, position=(0, 1.35, 0), scale=(1.2, 0.8, 1.2), model='cube', color=color.brown)
        self.bucket_top = Entity(parent=self.bucket, position=(0, 0.45, 0), scale=(0.75, 0.25, 0.75), model='cube', color=color.violet)
        self.bucket_trigger = Entity(parent=self.bucket, position=(0, 0.35, 0), scale=(0.95, 0.15, 0.95), model='cube', color=color.clear)
        self.bucket_trigger.collider = 'box'
        self.bucket_trigger.visible = False

        self.body = Entity(parent=self, position=(0, 0, 0), scale=(1.0, 1.2, 0.6), model='cube', color=color.cyan)
        self.head = Entity(parent=self, position=(0, 1.7, 0), scale=(0.7, 0.7, 0.7), model='sphere', color=color.orange)
        self.left_leg = Entity(parent=self, position=(-0.3, -0.9, 0), scale=(0.25, 1.0, 0.25), model='cube', color=color.blue)
        self.right_leg = Entity(parent=self, position=(0.3, -0.9, 0), scale=(0.25, 1.0, 0.25), model='cube', color=color.blue)
        self.left_arm = Entity(parent=self, position=(-0.6, 0.4, 0), scale=(0.2, 0.9, 0.2), model='cube', color=color.orange)
        self.right_arm = Entity(parent=self, position=(0.6, 0.4, 0), scale=(0.2, 0.9, 0.2), model='cube', color=color.orange)

        self.speed = PLAYER_SPEED
        self.is_moving = False

    def update(self):
        move = Vec3(0, 0, 0)
        if held_keys['w']:
            move.z += 1
        if held_keys['s']:
            move.z -= 1
        if held_keys['a']:
            move.x -= 1
        if held_keys['d']:
            move.x += 1

        if move.length() > 0:
            move *= self.speed * time.dt
            self.position += move
            self.position.x = clamp(self.position.x, -PLAYABLE_BOUNDS, PLAYABLE_BOUNDS)
            self.position.z = clamp(self.position.z, -PLAYABLE_BOUNDS, PLAYABLE_BOUNDS)


class Cloud(Entity):
    def __init__(self):
        super().__init__(position=(0, 8, 12), scale=(3.2, 1.5, 2.4), model=None, color=color.pink)
        self.puffs = []
        for offset, scale in [(-1.2, 1.2), (0.0, 1.6), (1.1, 1.0), (-0.6, 0.8), (0.7, 0.9)]:
            puff = Entity(parent=self, position=(offset, 0, 0), model='sphere', color=color.pink)
            puff.scale = (scale, 0.8, scale)
            self.puffs.append(puff)
        self.speed = 2.8
        self.direction = 1
        self.height = 8.5

    def update(self):
        self.x += self.direction * self.speed * time.dt
        self.z += random.uniform(-0.3, 0.3) * time.dt
        if self.x > PLAYABLE_BOUNDS - 2 or self.x < -PLAYABLE_BOUNDS + 2:
            self.direction *= -1
        self.x = clamp(self.x, -PLAYABLE_BOUNDS + 2, PLAYABLE_BOUNDS - 2)
        self.z = clamp(self.z, -PLAYABLE_BOUNDS + 2, PLAYABLE_BOUNDS - 2)


class Candy(Entity):
    def __init__(self, kind, spawn_pos):
        super().__init__(position=spawn_pos, model=None, collider='box', scale=(0.45, 0.45, 0.45), color=color.white)
        self.kind = kind
        self.points = 0
        self.dead = False
        self.velocity = Vec3(random.uniform(-3, 3), random.uniform(6, 10), random.uniform(-3, 3))
        self.gravity = GRAVITY

        if kind == 'candy_cane':
            self.points = 3
            self.body = Entity(parent=self, position=(0, 0, 0), model='cylinder', color=color.red)
            self.body.scale = (0.25, 0.6, 0.25)
            self.stripe = Entity(parent=self, position=(0, 0.08, 0), model='cylinder', color=color.white)
            self.stripe.scale = (0.28, 0.35, 0.28)
        elif kind == 'toffee':
            self.points = 10
            self.body = Entity(parent=self, position=(0, 0, 0), model='cube', color=color.gold)
            self.body.scale = (0.5, 0.45, 0.45)
        elif kind == 'sour_patch':
            self.points = 15
            self.body = Entity(parent=self, position=(0, 0, 0), model='sphere', color=color.green)
            self.body.scale = (0.35, 0.35, 0.35)
            self.eye_left = Entity(parent=self, position=(-0.1, 0.1, 0.2), model='sphere', color=color.white)
            self.eye_left.scale = (0.08, 0.08, 0.08)
            self.eye_right = Entity(parent=self, position=(0.1, 0.1, 0.2), model='sphere', color=color.white)
            self.eye_right.scale = (0.08, 0.08, 0.08)
        elif kind == 'chocolate':
            self.points = 20
            self.body = Entity(parent=self, position=(0, 0, 0), model='cube', color=color.brown)
            self.body.scale = (0.6, 0.25, 0.25)

    def update(self, player, game):
        self.position += self.velocity * time.dt
        self.velocity.y += self.gravity * time.dt
        self.velocity.x *= 0.995
        self.velocity.z *= 0.995

        if self.position.y < 0.2:
            self.dead = True
            game.lives -= 1
            game.heart_icons[-1].visible = False
            game.heart_icons.pop()
            game.remove_candy(self)
            return

        bucket_rect = player.bucket_trigger
        if bucket_rect.intersects(self).hit:
            self.dead = True
            game.score += self.points
            game.score_text.text = f'Score: {game.score}'
            game.remove_candy(self)


class CandyGame:
    def __init__(self):
        self.score = 0
        self.lives = 10
        self.paused = False
        self.game_over = False
        self.win = False
        self.candies: List[Candy] = []

        self.player = Player()
        self.cloud = Cloud()
        self.floor = Entity(model='plane', scale=(GROUND_SIZE, 1, GROUND_SIZE), color=color.lime, texture='white_cube')
        self.floor.collider = 'box'
        camera.position = (0, 10, -14)
        camera.look_at(self.player)
        camera.fov = 70

        self.score_text = Text(text='Score: 0', position=(-0.85, 0.45), scale=0.03, origin=(0, 0), color=color.white)
        self.heart_icons = []
        for i in range(self.lives):
            heart = make_heart(position=(-0.9 + i * 0.06, 0.42), scale=0.05)
            heart.set_scale((0.05, 0.05, 0.05))
            heart.parent = camera.ui
            self.heart_icons.append(heart)

        self.spawn_timer = 0.0
        self.spawn_interval = 1.1
        self.end_text = None

        self.set_up_camera()

    def set_up_camera(self):
        camera.position = (0, 8, -12)
        camera.look_at(self.player)

    def spawn_candy(self):
        kind = random.choice(['candy_cane', 'toffee', 'sour_patch', 'chocolate'])
        spawn_pos = (self.cloud.x + random.uniform(-1.5, 1.5), self.cloud.y, self.cloud.z + random.uniform(-1.5, 1.5))
        candy = Candy(kind, spawn_pos)
        self.candies.append(candy)

    def remove_candy(self, candy):
        if candy in self.candies:
            candy.disable()
            self.candies.remove(candy)

    def update(self):
        if self.paused or self.game_over or self.win:
            return

        self.player.update()
        self.cloud.update()

        self.spawn_timer += time.dt
        if self.spawn_timer >= self.spawn_interval:
            self.spawn_timer = 0
            self.spawn_candy()

        for candy in list(self.candies):
            candy.update(self.player, self)

        if self.score >= 100:
            self.win = True
            self.paused = True
            self.end_text = Text(text='You Win', position=(0, 0), scale=0.06, origin=(0, 0), color=color.gold)
            self.end_text.z = 0.1
            self.end_text.parent = camera.ui
        elif self.lives <= 0:
            self.game_over = True
            self.paused = True
            self.end_text = Text(text='You Lose', position=(0, 0), scale=0.06, origin=(0, 0), color=color.red)
            self.end_text.z = 0.1
            self.end_text.parent = camera.ui

    def run(self):
        pass


if __name__ == '__main__':
    game = CandyGame()
    app.on_update = game.update
    app.run()
