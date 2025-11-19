import pygame

import commands
import core

# === Keybinds ===
JUMP_KEY = pygame.K_SPACE
MOVE_LEFT_KEY = pygame.K_a
MOVE_RIGHT_KEY = pygame.K_d
QUIT_KEY = pygame.K_ESCAPE

class InputHandler:
    def __init__(self):
        pass

    def handle_input_event(self, event): # placed in the event loop
        if event.type == pygame.KEYDOWN:
            if event.key == JUMP_KEY:
                commands.jump_down_cmd.execute()
            if event.key == MOVE_LEFT_KEY:
                commands.move_left_down_cmd.execute()
            if event.key == MOVE_RIGHT_KEY:
                commands.move_right_down_cmd.execute()
        if event.type == pygame.KEYUP:
            if event.key == JUMP_KEY:
                commands.jump_up_cmd.execute()
            if event.key == MOVE_LEFT_KEY:
                commands.move_left_up_cmd.execute()
            if event.key == MOVE_RIGHT_KEY:
                commands.move_right_up_cmd.execute()