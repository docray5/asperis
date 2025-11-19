import pygame
import core
import random

class Camera:
    def __init__(self):
        self.position = pygame.math.Vector2(0, 0)
        self.offset = pygame.math.Vector2(0, 0)
        self.width = core.VIEWPORT_WIDTH
        self.height = core.VIEWPORT_HEIGHT
        self.shake_amount = pygame.math.Vector2(0, 0)
        self.shake_counter = 0
        self.shake_duration = 0

        self.follow_speed = 10
        self.dead_zone = 2

    def shake(self, strength, duration):
        self.shake_amount.x = strength
        self.shake_amount.y = strength
        self.shake_duration = duration
        self.shake_counter = 0

    def update(self, player):
        target_x = player.position.x + player.width / 2 - self.width / 2
        target_y = player.position.y + player.height / 2 - self.height / 2

        # factor = 1 - math.pow(0.5, dt * self.follow_speed)
        factor = min(self.follow_speed * core.dt, 1.0)

        # if you don't want the dead zone, just remove the ifs and leave the other two lines
        if abs(target_x - self.position.x) > self.dead_zone:
            self.position.x += (target_x - self.position.x) * factor
        if abs(target_y - self.position.y) > self.dead_zone:
            self.position.y += (target_y - self.position.y) * factor

        # TODO bounds

        # Apply screen shake:
        if self.shake_counter < self.shake_duration:
            self.shake_counter += core.dt
            self.position.x += self.shake_amount.x * (random.randint(0, 1) * 2 - 1)
            self.position.y += self.shake_amount.y * (random.randint(0, 1) * 2 - 1)