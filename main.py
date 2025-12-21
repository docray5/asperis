import pygame
import sys
import ctypes

import commands
import core
from ecs import entity_manger
from ecs.components import PhysicsComp, RectToDrawComp, RenderableComp, TileComp, TransformComp, PlayerComp
from ecs.entity_manger import EntityManager
from ecs.system_manager import SystemManager
from systems.camera_system import CameraSystem
from systems.input_system import InputSystem
from systems.physics_system import PhysicsSystem
from systems.player_system import PlayerSystem
from systems.render_system import RenderSystem

# Additional line because windows scaling is broken and affects my game
# thanks to this the window displays independently to scaling
ctypes.windll.user32.SetProcessDPIAware()


class Entity: # actually it's a drawable entity
    def __init__(self, x, y, width, height, color):
        self.drawing_rect = pygame.Rect(x, y, width, height)  # purely for drawing purpose
        self.color = color
        self.position = pygame.math.Vector2(x, y)
        self.width = width
        self.height = height

    def update(self, dt):
        pass

    def render(self, surface):
        self.drawing_rect.x = round(self.position.x - core.camera.position.x)
        self.drawing_rect.y = round(self.position.y - core.camera.position.y)
        pygame.draw.rect(surface, self.color, self.drawing_rect)


class Tile(Entity):
    def __init__(self, x, y, width, height):
        super().__init__(x, y, width, height, pygame.Color(200, 200, 200))


# TODO: Physics Entity


class Player(Entity): # TODO make this inherit the physics entity
    def __init__(self, x, y, width, height, tiles):
        super().__init__(x, y, width, height, pygame.Color("white"))
        self.velocity = pygame.math.Vector2(0, 0) # To be moved to Physics entity
        self.acceleration = pygame.math.Vector2(0, 0)
        self.jumping = False
        self.on_ground = False
        self.coyote_counter = 0
        self.jump_buffer_counter = 0
        self.input_x_dir = 0
        self.right_held = False
        self.left_held = False
        self.jump_held = False
        self.last_jump_counter = 0
        self.tiles = tiles

        # config
        self.coyote_time = 0.125
        self.jump_buffer_time = 0.05
        self.ground_accel_rate = 2100
        self.max_speed = 250
        self.jump_force = -550
        self.air_accel_rate = 1050
        self.max_fall_speed = 1000
        self.gravity = 1400
        self.jump_release_time = 0.2

    def jump_key_down(self):
        self.jump_held = True
        if not self.on_ground and self.coyote_counter < self.coyote_time:
            self.jump()


    def jump_key_up(self):
        self.jump_held = False
        self.jumping = False
        if self.last_jump_counter > self.jump_release_time:
            self.velocity.y *= 0.5

    def left_key_down(self):
        self.left_held = True

    def right_key_down(self):
        self.right_held = True

    def left_key_up(self):
        self.left_held = False

    def right_key_up(self):
        self.right_held = False

    def jump(self):
        self.velocity.y = self.jump_force
        self.jumping = True
        self.on_ground = False
        print("nig")

    def collision_check(self, physics_entity):
        return (self.position.x + self.width > physics_entity.position.x and
                self.position.x < physics_entity.position.x + physics_entity.width and
                self.position.y + self.height > physics_entity.position.y and
                self.position.y < physics_entity.position.y + physics_entity.height)

    def gravity_collision_check(self, physics_entity):
        """
        Check the collision with :param physics_entity: but one pixel below the player
        :return: bool if collided
        """
        return (self.position.x + self.width > physics_entity.position.x and
                self.position.x < physics_entity.position.x + physics_entity.width and
                self.position.y + self.height+1 > physics_entity.position.y and
                self.position.y < physics_entity.position.y + physics_entity.height)

    def update(self, dt):
        # Why do I split the two axis'? It helps with determining from which side did the player
        # hit an obstacle and at the same time does not affect physics accuracy.

        # handle input
        self.input_x_dir = 0
        if self.right_held and not self.left_held:
            self.input_x_dir = 1

        if self.left_held and not self.right_held:
            self.input_x_dir = -1

        if self.jump_held:
            self.jump_buffer_counter = self.jump_buffer_time
            if self.on_ground:
                self.jump()

        # === X-axis: ===

        # reduce penalty for changing direction and apply proper accel rates
        if self.input_x_dir != 0 and (self.velocity.x * self.input_x_dir) < 0:
            if self.on_ground:
                self.acceleration.x = self.ground_accel_rate * 2 * self.input_x_dir
            else:
                self.acceleration.x = self.air_accel_rate * 2 * self.input_x_dir
        else:
            if self.on_ground:
                self.acceleration.x = self.ground_accel_rate * self.input_x_dir
            else:
                self.acceleration.x = self.air_accel_rate * self.input_x_dir

        # Apply forces
        self.velocity.x += self.acceleration.x * dt

        # Apply friction
        if self.input_x_dir == 0:
            self.velocity.x *= 0.8 ** (dt * 60)
            if abs(self.velocity.x) < 0.1:
                self.velocity.x = 0

        # Cap speed
        if abs(self.velocity.x) > self.max_speed:
            if self.velocity.x < 0: self.velocity.x = -self.max_speed
            else: self.velocity.x = self.max_speed

        # Update Position
        self.position.x += self.velocity.x * dt

        # Temporary Collision check for X-Axis
        for tile in self.tiles:
            if self.collision_check(tile):
                if self.velocity.x > 0:
                    self.position.x = tile.position.x - self.width
                    self.velocity.x = 0
                elif self.velocity.x < 0:
                    self.position.x = tile.position.x + tile.width
                    self.velocity.x = 0

        # === Y-axis: ===
        # Apply gravity and all the forces to velocity
        # I skip mass so it's just F = a
        if not self.on_ground:
            self.velocity.y += self.gravity * dt
            self.jump_buffer_counter -= dt
            self.coyote_counter += dt

        if self.on_ground:
            self.coyote_counter = 0

        if self.last_jump_counter <= self.jump_release_time:
            self.last_jump_counter += dt

        if self.on_ground and self.jump_buffer_counter > 0:
            self.jump()
            self.jump_buffer_counter = 0

        # Apply forces
        self.velocity.y += self.acceleration.y * dt

        # Cap speed
        if self.velocity.y > self.max_fall_speed:
            self.velocity.y = self.max_fall_speed

        # Update Position
        self.position.y += self.velocity.y * dt

        self.on_ground = False
        # Temporary Collision check
        if self.position.y > core.VIEWPORT_HEIGHT-48:
            self.position.y = core.VIEWPORT_HEIGHT - 48
            # if abs(self.velocity.y) < 0.1: self.velocity.y = 0
            # else: self.velocity.y = -self.velocity.y *0.3
            self.on_ground = True
            self.hit_the_floor()
            self.velocity.y = 0
        if self.position.y+1 > core.VIEWPORT_HEIGHT-48:
            self.on_ground = True

        # Temporary Collision check for Y-Axis
        for tile in self.tiles:
            if self.collision_check(tile):
                if self.velocity.y > 0:
                    self.position.y = tile.position.y - self.height
                    self.on_ground = True
                    self.hit_the_floor()
                    self.velocity.y = 0
                elif self.velocity.y < 0:
                    self.position.y = tile.position.y + tile.height
                    self.velocity.y = 0
            if self.gravity_collision_check(tile):
                if self.velocity.y >= 0 and not self.jumping:
                    self.on_ground = True

    def hit_the_floor(self):
        print("Hit the floor")
        core.camera.shake((self.velocity.y / self.max_fall_speed) * 3, (self.velocity.y / self.max_fall_speed) * 0.25)
        # do some particle effects
        # or call some event


def create_tile(x, y, width, height, entity_mgr: EntityManager):
    tile_entity_id = entity_mgr.create_entity()
    transform_cmp = TransformComp(pygame.math.Vector2(x, y), width, height)
    # physics_cmp = PhysicsComp()
    render_cmp = RenderableComp(pygame.Color(200, 200, 200))
    entity_mgr.add_components(
        tile_entity_id, 
        transform_cmp, 
        render_cmp,
        TileComp(),
        RectToDrawComp())


def main():
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

    # world_surface = pygame.Surface((core.VIEWPORT_WIDTH, core.VIEWPORT_HEIGHT))
    # scaled_surface = pygame.Surface((core.WINDOW_WIDTH, core.WINDOW_HEIGHT))

    # tiles = [Tile(64, core.VIEWPORT_HEIGHT - 72, 128, 16),
    #          Tile(core.VIEWPORT_WIDTH / 2, core.VIEWPORT_HEIGHT / 2, 128, 16)]

    # player = Player(0, 0, 32, 48, tiles)

    core.initialize()

    # New Structure:
    entity_manager = EntityManager()
    system_manager = SystemManager()

    # Temporary Factory:

    player_entity_id = entity_manager.create_entity()
    player_comp = PlayerComp()
    transform_cmp = TransformComp(pygame.math.Vector2(0, 0), 32, 48)
    render_cmp = RenderableComp(pygame.color.Color(255, 255, 255))
    entity_manager.add_components(
        player_entity_id, 
        player_comp, 
        transform_cmp, 
        render_cmp,
        RectToDrawComp())

    create_tile(64, core.VIEWPORT_HEIGHT - 72, 128, 16, entity_manager)
    create_tile(core.VIEWPORT_WIDTH / 2, core.VIEWPORT_HEIGHT / 2 + 32, 128, 16, entity_manager)
    create_tile(0, core.VIEWPORT_HEIGHT, core.VIEWPORT_WIDTH, 32, entity_manager)

    player_system = PlayerSystem(entity_manager, player_comp)

    # Setup the engine's systems
    system_manager.add_system(InputSystem(entity_manager))
    system_manager.add_system(player_system)
    system_manager.add_system(PhysicsSystem(entity_manager))
    system_manager.add_system(CameraSystem(entity_manager))
    system_manager.add_system(RenderSystem(entity_manager, screen))

    commands.initialize(player_system)

    while running:
        dt = clock.tick(core.FPS) / 1000.0
        min(dt, 0.2)

        # for event in pygame.event.get():
        #     if event.type == pygame.QUIT:
        #         running = False
        #     input_handler.handle_input_event(event)

        entity_manager.purge_dead_entities()

        system_manager.update(dt)

        # OLD:

        # player.update(dt)

        # core.camera.update(dt, player)

        # draw everything to the main surface
        # screen.fill(core.BLACK)
        # world_surface.fill(core.BACKGROUND_COLOR)
        # scaled_surface.fill(core.BACKGROUND_COLOR)

        # player.render(world_surface)

        # for tile in tiles:
        #     tile.render(world_surface)

        # Update display and render scaled world
        # pygame.transform.scale(world_surface, (core.WINDOW_WIDTH, core.WINDOW_HEIGHT), scaled_surface)
        # screen.blit(scaled_surface, (0, 0))
        # pygame.display.flip()

    pygame.quit()
    sys.exit()

if __name__ == '__main__':
    main()
