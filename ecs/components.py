from abc import ABC
from dataclasses import dataclass, field
import pygame


class Component(ABC):
    """Base class for all components"""
    pass


@dataclass
class TransformComp(Component):
    position: pygame.math.Vector2
    width: float
    height: float


@dataclass
class TileComp(Component):
    pass


@dataclass
class RenderableComp(Component):
    color: pygame.Color
    render: bool = True


@dataclass
class RectToDrawComp(Component):
    # before each drawing is going to be set to Transform's comp data:
    drawing_rect: pygame.Rect = field(default_factory=lambda: pygame.Rect(0, 0, 0, 0))


@dataclass
class PhysicsComp(Component):
    pass


@dataclass
class PlayerComp(Component):
    """
    Component only related to handling of player input
    """
    # TODO MOVE THESE to PhysicsComp
    velocity: pygame.math.Vector2 = field(default_factory=lambda: pygame.math.Vector2(0, 0))
    acceleration: pygame.math.Vector2 = field(default_factory=lambda: pygame.math.Vector2(0, 0))
    jumping: bool = False
    on_ground: bool = False

    # THESE STAY
    coyote_counter: float = 0
    jump_buffer_counter: float = 0
    input_x_dir: float = 0
    right_held: bool = False
    left_held: bool = False
    jump_held: bool = False
    last_jump_counter: float = 0

    # config (REMOVE THESE AND PUT INTO CORE)
    coyote_time: float = 0.05
    jump_buffer_time: float = 0.02
    ground_accel_rate: float = 2100
    max_speed: float = 250
    jump_force: float = -550
    air_accel_rate: float = 1050
    max_fall_speed: float = 1000
    gravity: float = 1400
    jump_release_time: float = 0.02
