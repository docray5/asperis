import pygame
import sys
import ctypes
import commands
import core
import factory
from ecs.components import PlayerComp
from ecs.entity_manger import EntityManager
from ecs.system_manager import SystemManager
from systems.camera_system import CameraSystem
from systems.input_system import InputSystem
from systems.physics_system import PhysicsSystem
from systems.player_system import PlayerSystem
from systems.render_system import RenderSystem


def main():
    # Additional line because windows scaling is broken and affects my game
    # thanks to this the window displays independently to scaling
    ctypes.windll.user32.SetProcessDPIAware()

    # init
    pygame.init()
    # , pygame.FULLSCREEN | pygame.SCALED
    screen = pygame.display.set_mode((core.WINDOW_WIDTH, core.WINDOW_HEIGHT), vsync=core.VSYNC)
    # screen = pygame.display.set_mode((pygame.display.get_desktop_sizes()[0][0], pygame.display.get_desktop_sizes()[0][1]), vsync=VSYNC)
    # print(pygame.display.get_desktop_sizes()[0][0], pygame.display.get_desktop_sizes()[0][1])
    # SCREEN_WIDTH = pygame.display.get_desktop_sizes()[0][0]
    # SCREEN_HEIGHT = pygame.display.get_desktop_sizes()[0][1]
    pygame.display.set_caption(core.TITLE)
    clock = pygame.time.Clock()
    running = True

    core.initialize()

    # New Structure:
    entity_manager = EntityManager()
    system_manager = SystemManager()

    player_id = factory.create_player(entity_manager, 0, 0, 32, 48)

    factory.create_tile(entity_manager, 64, core.VIEWPORT_HEIGHT - 72, 128, 16)
    factory.create_tile(entity_manager, core.VIEWPORT_WIDTH / 2, core.VIEWPORT_HEIGHT / 2 + 32, 128, 16)
    factory.create_tile(entity_manager, 0, core.VIEWPORT_HEIGHT, core.VIEWPORT_WIDTH, 32)

    player_system = PlayerSystem(entity_manager, entity_manager.get_component(player_id, PlayerComp))
    camera_system = CameraSystem(entity_manager)

    # Set up the engine's systems
    system_manager.add_system(InputSystem(entity_manager))
    system_manager.add_system(player_system)
    system_manager.add_system(PhysicsSystem(entity_manager))
    system_manager.add_system(camera_system)
    system_manager.add_system(RenderSystem(entity_manager, screen))

    commands.initialize(player_system)

    core.event_manager.subscribe(camera_system)

    while running:
        dt = clock.tick(core.FPS) / 1000.0
        min(dt, 0.2)

        entity_manager.purge_dead_entities()

        system_manager.update(dt)

    pygame.quit()
    sys.exit()

if __name__ == '__main__':
    main()
