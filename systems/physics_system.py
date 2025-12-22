import core
from ecs.components import TransformComp, PlayerComp, TileComp
from ecs.system import System
from events import ShakeCameraEvent


class PhysicsSystem(System):
    """
    More like a Movement and collision system.
    Moves entities according to their force applied and Handles collisions of entities and emits events.
    """
    def __init__(self, entity_manager):
        super().__init__(entity_manager)

    def update(self, dt: float) -> None:

        # SoonTM the PlayerComp will be replaced with Physics Comp
        # but as of now I don't have any other physics based entities
        # I don't think the enemies will be even like that
        # for entity_id in self.entity_manager.get_entities_with(PhysicsComp, TransformComp):
        #     handle x
        #     Handle y

        # === Initial Setup: ===
        player_id = self.entity_manager.get_entities_with(PlayerComp)[0]
        player_cmp: PlayerComp | None = self.entity_manager.get_component(player_id, PlayerComp)
        player_trans_cmp: TransformComp | None = self.entity_manager.get_component(player_id, TransformComp)

        # === X-axis: ===
        self.move_player_x(player_cmp, player_trans_cmp, dt)

        for tile_id in self.entity_manager.get_entities_with(TileComp):
            tile_trans_cmp: TransformComp | None = self.entity_manager.get_component(tile_id, TransformComp)
            if self.check_collision(player_trans_cmp, tile_trans_cmp):
                self.handle_player_collision_x(player_cmp, player_trans_cmp, tile_trans_cmp)

        # === Y Axis ===
        self.move_player_y(player_cmp, player_trans_cmp, dt)

        for tile_id in self.entity_manager.get_entities_with(TileComp):
            tile_trans_cmp: TransformComp | None = self.entity_manager.get_component(tile_id, TransformComp)
            if self.check_collision(player_trans_cmp, tile_trans_cmp):
                self.handle_player_collision_y(player_cmp, player_trans_cmp, tile_trans_cmp)
            elif self.check_collision_for_gravity(player_trans_cmp, tile_trans_cmp):
                self.handle_player_gravity_collision(player_cmp)


    def move_player_x(self, player_cmp, transform_cmp, dt):
        # Apply forces
        if player_cmp.dashing:
            # allow for subtle steering during dash
            player_cmp.velocity.x += player_cmp.input_x_dir * 10000 * dt
            # cap dash speed
            player_cmp.velocity.x = max(-player_cmp.max_dash_speed,
                                        min(player_cmp.velocity.x, player_cmp.max_dash_speed))
        else:
            player_cmp.velocity.x += player_cmp.acceleration.x * dt

            # Apply friction
            if player_cmp.input_x_dir == 0:
                player_cmp.velocity.x *= core.FRICTION ** (dt * 60)
                if abs(player_cmp.velocity.x) < 0.1:
                    player_cmp.velocity.x = 0

            # Cap speed
            if abs(player_cmp.velocity.x) > player_cmp.max_speed:
                if player_cmp.velocity.x < 0:
                    player_cmp.velocity.x = -player_cmp.max_speed
                else:
                    player_cmp.velocity.x = player_cmp.max_speed

        # Update Position
        transform_cmp.position.x += player_cmp.velocity.x * dt

    def move_player_y(self, player_cmp, transform_cmp, dt):
        if not player_cmp.on_ground and not player_cmp.dashing:
            player_cmp.velocity.y += player_cmp.gravity * dt

        # Apply forces
        player_cmp.velocity.y += player_cmp.acceleration.y * dt

        # Cap speed
        if abs(player_cmp.velocity.y) > player_cmp.max_fall_speed:
            if player_cmp.velocity.y < 0:
                player_cmp.velocity.y = -player_cmp.max_fall_speed
            else:
                player_cmp.velocity.y = player_cmp.max_fall_speed

        # Update Position
        transform_cmp.position.y += player_cmp.velocity.y * dt

        player_cmp.on_ground = False

    def handle_player_collision_x(self, player_cmp: PlayerComp, player_trans_cmp: TransformComp, tile_trans_cmp: TransformComp):
        if player_cmp.velocity.x > 0:
            player_trans_cmp.position.x = tile_trans_cmp.position.x - player_trans_cmp.width
            player_cmp.velocity.x = 0
            player_cmp.dashing = False
        elif player_cmp.velocity.x < 0:
            player_trans_cmp.position.x = tile_trans_cmp.position.x + tile_trans_cmp.width
            player_cmp.velocity.x = 0
            player_cmp.dashing = False

    def handle_player_collision_y(self, player_cmp: PlayerComp, player_trans_cmp: TransformComp, tile_trans_cmp: TransformComp):
        if player_cmp.velocity.y > 0:
            player_trans_cmp.position.y = tile_trans_cmp.position.y - player_trans_cmp.height
            player_cmp.jumping = False
            player_cmp.on_ground = True
            self.player_hit_the_floor(player_cmp)
            player_cmp.velocity.y = 0
            player_cmp.dashing = False
            player_cmp.dashes_left = player_cmp.max_dash_amount
        elif player_cmp.velocity.y < 0:
            player_trans_cmp.position.y = tile_trans_cmp.position.y + tile_trans_cmp.height
            player_cmp.velocity.y = 0
            player_cmp.dashing = False

    def handle_player_gravity_collision(self, player_cmp: PlayerComp):
        if player_cmp.velocity.y >= 0 and not player_cmp.jumping:
            player_cmp.on_ground = True

    def player_hit_the_floor(self, player_cmp):
        core.event_manager.notify(ShakeCameraEvent((player_cmp.velocity.y / player_cmp.max_fall_speed) * 3,
                          (player_cmp.velocity.y / player_cmp.max_fall_speed) * 0.25))
        # do some particle effects
        # or call some event

    def check_collision(self, e1_trans_cmp: TransformComp, e2_trans_cmp: TransformComp) -> bool:
        return (e1_trans_cmp.position.x + e1_trans_cmp.width > e2_trans_cmp.position.x and
                e1_trans_cmp.position.x < e2_trans_cmp.position.x + e2_trans_cmp.width and
                e1_trans_cmp.position.y + e1_trans_cmp.height > e2_trans_cmp.position.y and
                e1_trans_cmp.position.y < e2_trans_cmp.position.y + e2_trans_cmp.height)

    def check_collision_for_gravity(self, e1_trans_cmp: TransformComp, e2_trans_cmp: TransformComp) -> bool:
        """
        Check the collision of first entity with second entity but one pixel below the first entity
        :return: bool if collided
        """
        return (e1_trans_cmp.position.x + e1_trans_cmp.width > e2_trans_cmp.position.x and
                e1_trans_cmp.position.x < e2_trans_cmp.position.x + e2_trans_cmp.width and
                e1_trans_cmp.position.y + e1_trans_cmp.height+1 > e2_trans_cmp.position.y and
                e1_trans_cmp.position.y < e2_trans_cmp.position.y + e2_trans_cmp.height)
