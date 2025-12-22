import pygame
import core
import commands
import sys
from ecs.system import System


class InputSystem(System):
    def __init__(self, entity_manager):
        super().__init__(entity_manager)
        self.last_shift = False

    def update(self, dt: float) -> None:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                # Temporarily this is here because I can have only one event loop
                # Soon TM going to turn this into a command
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == core.JUMP_KEY:
                    commands.jump_down_cmd.execute()
                if event.key == core.MOVE_LEFT_KEY:
                    commands.move_left_down_cmd.execute()
                if event.key == core.MOVE_RIGHT_KEY:
                    commands.move_right_down_cmd.execute()
                if event.key == core.POINT_UP_KEY:
                    commands.point_up_key_down.execute()
                if event.key == core.POINT_DOWN_KEY:
                    commands.point_down_key_down.execute()
                if event.key == core.DASH_KEY:
                    commands.dash_k_down_cmd.execute()
            if event.type == pygame.KEYUP:
                if event.key == core.JUMP_KEY:
                    commands.jump_up_cmd.execute()
                if event.key == core.MOVE_LEFT_KEY:
                    commands.move_left_up_cmd.execute()
                if event.key == core.MOVE_RIGHT_KEY:
                    commands.move_right_up_cmd.execute()
                if event.key == core.POINT_UP_KEY:
                    commands.point_up_key_up.execute()
                if event.key == core.POINT_DOWN_KEY:
                    commands.point_down_key_up.execute()