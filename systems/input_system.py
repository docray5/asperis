import pygame
import core
import commands
import sys
from ecs.system import System
from events import CreateParticlesEvent


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
            if event.type == pygame.MOUSEMOTION:
                core.mouse_pos.x = pygame.mouse.get_pos()[0] / core.WINDOW_SCALE
                core.mouse_pos.y = pygame.mouse.get_pos()[1] / core.WINDOW_SCALE
                commands.mouse_motion_cmd.execute()
            if event.type == pygame.MOUSEBUTTONDOWN:
                core.mouse_pos.x = pygame.mouse.get_pos()[0] / core.WINDOW_SCALE
                core.mouse_pos.y = pygame.mouse.get_pos()[1] / core.WINDOW_SCALE
                commands.mouse_btn_down_cmd.execute()
                commands.attack_key_down_cmd.execute()
            if event.type == pygame.KEYDOWN:
                if event.key == core.JUMP_KEY:
                    commands.jump_down_cmd.execute()
                if event.key == core.MOVE_LEFT_KEY:
                    commands.move_left_down_cmd.execute()
                if event.key == core.MOVE_RIGHT_KEY:
                    commands.move_right_down_cmd.execute()
                if event.key == core.POINT_UP_KEY:
                    commands.point_up_key_down_cmd.execute()
                if event.key == core.POINT_DOWN_KEY:
                    commands.point_down_key_down_cmd.execute()
                if event.key == core.DASH_KEY:
                    commands.dash_k_down_cmd.execute()
                if event.key == core.ATTACK_KEY:
                    commands.attack_key_down_cmd.execute()
                if event.key == pygame.K_x:
                    core.event_manager.notify(CreateParticlesEvent(30, 0, core.VIEWPORT_HEIGHT/2, 10, 4, 2, pygame.Color(255, 255, 255, 255), 45, 90, 150, 50, 0.8, 0.1, 0.3))
                if event.key == pygame.K_ESCAPE:
                    commands.pause_game_cmd.execute()
            if event.type == pygame.KEYUP:
                if event.key == core.JUMP_KEY:
                    commands.jump_up_cmd.execute()
                if event.key == core.MOVE_LEFT_KEY:
                    commands.move_left_up_cmd.execute()
                if event.key == core.MOVE_RIGHT_KEY:
                    commands.move_right_up_cmd.execute()
                if event.key == core.POINT_UP_KEY:
                    commands.point_up_key_up_cmd.execute()
                if event.key == core.POINT_DOWN_KEY:
                    commands.point_down_key_up_cmd.execute()