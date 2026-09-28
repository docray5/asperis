from pygame.math import Vector2

from camera import Camera
import pygame

from events import EventManager
from main import AssetManager

# === Config ===
VIEWPORT_WIDTH = 1280 // 2  # size of the surface to which everything is drawn
VIEWPORT_HEIGHT = 720 // 2
WINDOW_WIDTH = VIEWPORT_WIDTH * 2  # size of the upscaled window
WINDOW_HEIGHT = VIEWPORT_HEIGHT * 2
WINDOW_SCALE = 2
FPS = 120
VSYNC = 1
TITLE = "asperis"
DEBUG = False
DRAW_HITBOXES = False
FLOATING_POINT_ERROR_FIX_THRESHOLD = 0.01
EDGE_DETECTION_LOOKAHEAD_DIST = 5
FONT_FAMILY = "Tahoma"

# === Keybinds ===
JUMP_KEY = pygame.K_SPACE
MOVE_LEFT_KEY = pygame.K_a
MOVE_RIGHT_KEY = pygame.K_d
QUIT_KEY = pygame.K_ESCAPE
POINT_UP_KEY = pygame.K_w
POINT_DOWN_KEY = pygame.K_s
DASH_KEY = pygame.K_LCTRL
ATTACK_KEY = pygame.K_RCTRL

# === Player controller config ===
FRICTION = 0.8
DASH_SPEED = 1000  # pixels per frame
SEPARATION_BUFFER = 1
PLAYER_SWORD_HIT_BOX_WIDTH = 64
PLAYER_SWORD_HIT_BOX_HEIGHT = 64
MAX_PLAYER_HEALTH = 10
HEALTH_BAR_WIDTH = 16

# === Enemy config ===
BOSS_SIZE = (88, 128)
BOSS_SWORD_HIT_BOX = (BOSS_SIZE[0] + 90, BOSS_SIZE[1] + 64)
BOSS_DAMAGE = 2
ATTACK_SIGHT_RANGE = BOSS_SWORD_HIT_BOX[0] / 2 + 54
SIGHT_RANGE = 768

ENEMY_SIZE = (36, 32)

# === Global variables ===
camera = None  # it's global only because it has to be accessed by render and camera systems. So
# It's only accessed there
event_manager = None
asset_manager: AssetManager | None = None
mouse_pos: Vector2 = Vector2(0, 0)
paused: bool = True
won = False

# Custom Colors:
BLACK = (0, 0, 0)
BACKGROUND_COLOR = (33, 33, 33, 1)
PLAYER_COLOR = (255, 255, 255)
PLAYER_INVINCIBLE_COLOR = (143, 143, 143)
CLEAR_COLOR = (0, 0, 0, 0)

BUTTON_COLOR = (237, 242, 244)
BUTTON_ON_HOVER_COLOR = (141, 153, 174)
BUTTON_FONT_COLOR = (43, 45, 66)

WIN_COLOR = (255, 215, 0)
LOSE_COLOR = (255, 10, 10)


def initialize():  # Initialize global Objects
    global camera, event_manager, asset_manager
    camera = Camera()
    event_manager = EventManager()
    asset_manager = AssetManager()


def reinitialize():
    global event_manager
    event_manager = EventManager()
