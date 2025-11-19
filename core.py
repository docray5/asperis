from camera import Camera

# Note: Keybinds are in input_handler

# === Config ===
VIEWPORT_WIDTH = 1280 // 2 # size of the surface to which everything is drawn
VIEWPORT_HEIGHT = 720 // 2
WINDOW_WIDTH = VIEWPORT_WIDTH * 2 # size of the upscaled window
WINDOW_HEIGHT = VIEWPORT_HEIGHT * 2
FPS = 60
VSYNC = 1
TITLE = "asperis"

# === Global variables (Singletons) ===
dt = 0
camera = None
commands = None

# Custom Colors:
BLACK = (0, 0, 0)
BACKGROUND_COLOR = (33, 33, 33)


def initialize(): # Initialize global Objects
    global camera
    camera = Camera()