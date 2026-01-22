from pathlib import Path

import pygame
import sys
import ctypes
import core
from scenes import SceneManager, MenuScene


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

    # Scenes:
    scene_manager = SceneManager(MenuScene(), screen)

    while running:
        dt = clock.tick(core.FPS) / 1000.0
        min(dt, 0.2)

        scene_manager.update(dt)

    pygame.quit()
    sys.exit()

if __name__ == '__main__':
    main()
