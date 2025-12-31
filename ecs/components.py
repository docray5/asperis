from abc import ABC
from dataclasses import dataclass, field
from enum import Enum

import pygame

import core


class Component(ABC):
    """Base class for all components"""
    pass


@dataclass
class TransformComp(Component):
    position: pygame.math.Vector2
    width: float
    height: float
    rotation: int = 0


@dataclass
class TileComp(Component):
    pass


@dataclass
class RenderableComp(Component):
    color: pygame.Color
    render: bool = True
    flip_x: bool = True
    flip_y: bool = True


@dataclass
class RectToDrawComp(Component):
    # before each drawing is going to be set to Transform's comp data:
    drawing_rect: pygame.Rect = field(default_factory=lambda: pygame.Rect(0, 0, 0, 0))


@dataclass
class CircleToDrawComp(Component):
    surface: pygame.Surface


@dataclass
class PhysicsComp(Component):
    velocity: pygame.math.Vector2 = field(default_factory=lambda: pygame.math.Vector2(0, 0))
    acceleration: pygame.math.Vector2 = field(default_factory=lambda: pygame.math.Vector2(0, 0))
    knockback_counter: float = 0

    knockback_time = 0.12
    is_knockback: bool = False
    max_knockback_speed: float = 1000


@dataclass
class AnimatedSpriteComp(Component):
    frames: list  # TODO add type list[pygame.image] or smth
    current_frame: int = 0
    animation_speed: float = 0.1
    last_update: float = 0
    one_shot: bool = True


@dataclass
class ParticleComp(Component):
    life_duration: float = 1
    time_alive: float = 0
    direction: int = 0  # angle
    speed: float = 300
    time_to_change_opacity: float = 0


@dataclass
class HealthComp(Component):
    health: int = 50


class EnemyType(Enum):
    PATROLLING = 1
    FOLLOWING = 2


@dataclass
class EnemyComp(Component):
    enemy_type: EnemyType = EnemyType.PATROLLING
    jumping: bool = False
    on_ground: bool = False
    last_jump_counter: float = 0
    damage: int = 1
    patrol_direction = -1

    max_speed: float = 100  # slower than player
    max_fall_speed: float = 1000
    jump_force: float = -550  # same as player
    accel_rate: float = 500
    gravity: float = 1400
    jump_cool_down = 1


@dataclass
class PlayerComp(Component):
    """
    Component only related to handling of player input
    """
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
    input_y_dir: float = 0
    dash_time: float = 0
    dashing: bool = False
    last_dashed: float = 0
    dashes_left: int = 0
    last_x_dir: float = 0
    invincibility_counter = 0
    invincibility = False

    # Sword:
    damage: int = 1
    sword_hit_box: TransformComp = field(
        default_factory=lambda: TransformComp(
            pygame.math.Vector2(), core.SWORD_HIT_BOX_WIDTH, core.SWORD_HIT_BOX_HEIGHT))
    last_attack_time: float = 0

    # config (REMOVE THESE AND PUT INTO CORE)
    coyote_time: float = 0.05
    jump_buffer_time: float = 0.02
    ground_accel_rate: float = 2100
    max_speed: float = 250
    max_dash_speed: float = 1000
    jump_force: float = -550
    air_accel_rate: float = 2100
    max_fall_speed: float = 1000
    gravity: float = 1400
    jump_release_time: float = 0.02
    dash_duration: float = 0.15
    dash_cool_down: float = 0.4
    max_dash_amount = 1
    attack_cool_down: float = 0.5
    invincibility_time = 0.5  # after getting hit
