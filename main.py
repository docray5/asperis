from pathlib import Path

import pygame
import sys
import ctypes
import commands
import core
import factory
from ecs.components import PlayerComp, PhysicsComp
from ecs.entity_manger import EntityManager
from ecs.system_manager import SystemManager
from systems.camera_system import CameraSystem
from systems.enemy_system import EnemySystem
from systems.health_system import HealthSystem
from systems.input_system import InputSystem
from systems.particle_system import ParticleSystem
from systems.physics_system import PhysicsSystem
from systems.player_system import PlayerSystem
from systems.render_system import RenderSystem


class AssetManager:
    def __init__(self, assets_path: str = "assets"):
        """Scans assets folder recursively, loads/caches all PNG/JPG/GIF images."""
        self.assets_path = Path(assets_path).resolve()
        self.cache: dict[str, pygame.Surface] = {}
        self._preload_all_images()

    def _preload_all_images(self):
        """Load all images from assets/ and subfolders into cache."""
        if not self.assets_path.exists():
            print(f"Warning: {self.assets_path} not found")
            return

        supported_exts = {'.png', '.jpg', '.jpeg', '.gif', '.bmp', '.tga'}
        for file_path in self.assets_path.rglob('*'):
            if file_path.is_file() and file_path.suffix.lower() in supported_exts:
                key = str(file_path.relative_to(self.assets_path))
                try:
                    surf = pygame.image.load(file_path).convert_alpha()
                    self.cache[key] = surf
                    print(f"Loaded: {key}")
                except pygame.error as e:
                    print(f"Failed to load {key}: {e}")

    def get(self, key: str):
        """Get cached image by relative filename (e.g. 'player.png' or 'sprites/enemy.png')."""
        return self.cache.get(key)

    def has(self, key: str) -> bool:
        """Check if asset exists in cache."""
        return key in self.cache

    def keys(self) -> list:
        """List all cached asset keys."""
        return list(self.cache.keys())

    def clear(self):
        """Clear all cached surfaces (frees memory)."""
        self.cache.clear()


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

    factory.create_enemy(entity_manager, 100, 0, 32, 32)

    factory.create_animated_slash_particle(entity_manager, 0, 0, True)

    player_system = PlayerSystem(entity_manager, entity_manager.get_component(player_id, PlayerComp),
                                 entity_manager.get_component(player_id, PhysicsComp))
    camera_system = CameraSystem(entity_manager)
    health_system = HealthSystem(entity_manager)
    physics_system = PhysicsSystem(entity_manager)

    # Set up the engine's systems
    system_manager.add_system(InputSystem(entity_manager))
    system_manager.add_system(player_system)
    system_manager.add_system(EnemySystem(entity_manager, player_id))
    system_manager.add_system(physics_system)
    system_manager.add_system(health_system)
    system_manager.add_system(ParticleSystem(entity_manager))
    system_manager.add_system(camera_system)
    system_manager.add_system(RenderSystem(entity_manager, screen))

    commands.initialize(player_system)

    core.event_manager.subscribe(camera_system)
    core.event_manager.subscribe(health_system)
    core.event_manager.subscribe(physics_system)

    while running:
        dt = clock.tick(core.FPS) / 1000.0
        min(dt, 0.2)

        entity_manager.purge_dead_entities()

        system_manager.update(dt)

    pygame.quit()
    sys.exit()

if __name__ == '__main__':
    main()
