import core
from ecs.components import TransformComp, PlayerComp, TileComp, PhysicsComp, EnemyComp, EnemyType
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

        # Enemy physics:
        for enemy_id in self.entity_manager.get_entities_with(EnemyComp):
            enemy_cmp: EnemyComp | None = self.entity_manager.get_component(enemy_id, EnemyComp)
            enemy_trans_cmp: TransformComp | None = self.entity_manager.get_component(enemy_id, TransformComp)
            enemy_physics_cmp: PhysicsComp | None = self.entity_manager.get_component(enemy_id, PhysicsComp)
            if enemy_cmp.enemy_type == EnemyType.FOLLOWING:

                self.move_enemy_x(enemy_cmp, enemy_physics_cmp, enemy_trans_cmp, dt)

                for tile_id in self.entity_manager.get_entities_with(TileComp):
                    tile_trans_cmp: TransformComp | None = self.entity_manager.get_component(tile_id, TransformComp)
                    if self.check_collision(enemy_trans_cmp, tile_trans_cmp):
                        self.handle_enemy_collision_x(enemy_cmp, enemy_physics_cmp, enemy_trans_cmp, tile_trans_cmp)

                self.move_enemy_y(enemy_cmp, enemy_physics_cmp, enemy_trans_cmp, dt)

                for tile_id in self.entity_manager.get_entities_with(TileComp):
                    tile_trans_cmp: TransformComp | None = self.entity_manager.get_component(tile_id, TransformComp)
                    if self.check_collision(enemy_trans_cmp, tile_trans_cmp):
                        self.handle_enemy_collision_y(enemy_cmp, enemy_physics_cmp, enemy_trans_cmp, tile_trans_cmp)
                    elif self.check_collision_for_gravity(enemy_trans_cmp, tile_trans_cmp):
                        self.handle_enemy_gravity_collision(enemy_cmp, enemy_physics_cmp)


        # Player Physics:
        # === Initial Setup: ===
        player_id = self.entity_manager.get_entities_with(PlayerComp)[0]
        player_cmp: PlayerComp | None = self.entity_manager.get_component(player_id, PlayerComp)
        player_physics_cmp: PhysicsComp | None = self.entity_manager.get_component(player_id, PhysicsComp)
        player_trans_cmp: TransformComp | None = self.entity_manager.get_component(player_id, TransformComp)

        # === X-axis: ===
        self.move_player_x(player_cmp, player_physics_cmp, player_trans_cmp, dt)

        # player collision with tiles on x
        for tile_id in self.entity_manager.get_entities_with(TileComp):
            tile_trans_cmp: TransformComp | None = self.entity_manager.get_component(tile_id, TransformComp)
            if self.check_collision(player_trans_cmp, tile_trans_cmp):
                self.handle_player_collision_x(player_cmp, player_physics_cmp, player_trans_cmp, tile_trans_cmp)

        # === Y Axis ===
        self.move_player_y(player_cmp, player_physics_cmp, player_trans_cmp, dt)

        # player collision with tiles on y
        for tile_id in self.entity_manager.get_entities_with(TileComp):
            tile_trans_cmp: TransformComp | None = self.entity_manager.get_component(tile_id, TransformComp)
            if self.check_collision(player_trans_cmp, tile_trans_cmp):
                self.handle_player_collision_y(player_cmp, player_physics_cmp, player_trans_cmp, tile_trans_cmp)
            elif self.check_collision_for_gravity(player_trans_cmp, tile_trans_cmp):
                self.handle_player_gravity_collision(player_cmp, player_physics_cmp)


    def move_player_x(self, player_cmp, physics_cmp, transform_cmp, dt):
        # Apply forces
        if player_cmp.dashing:
            # allow for subtle steering during dash
            physics_cmp.velocity.x += player_cmp.input_x_dir * 10000 * dt
            # cap dash speed
            physics_cmp.velocity.x = max(-player_cmp.max_dash_speed,
                                        min(physics_cmp.velocity.x, player_cmp.max_dash_speed))
        else:
            physics_cmp.velocity.x += physics_cmp.acceleration.x * dt

            # Apply friction
            if player_cmp.input_x_dir == 0:
                physics_cmp.velocity.x *= core.FRICTION ** (dt * 60)
                if abs(physics_cmp.velocity.x) < 0.1:
                    physics_cmp.velocity.x = 0

            # Cap speed
            if abs(physics_cmp.velocity.x) > player_cmp.max_speed:
                if physics_cmp.velocity.x < 0:
                    physics_cmp.velocity.x = -player_cmp.max_speed
                else:
                    physics_cmp.velocity.x = player_cmp.max_speed

        # Update Position
        transform_cmp.position.x += physics_cmp.velocity.x * dt

    def move_player_y(self, player_cmp, physics_cmp, transform_cmp, dt):
        if not player_cmp.on_ground and not player_cmp.dashing:
            physics_cmp.velocity.y += player_cmp.gravity * dt

        # Apply forces
        physics_cmp.velocity.y += physics_cmp.acceleration.y * dt

        # Cap speed
        if abs(physics_cmp.velocity.y) > player_cmp.max_fall_speed:
            if physics_cmp.velocity.y < 0:
                physics_cmp.velocity.y = -player_cmp.max_fall_speed
            else:
                physics_cmp.velocity.y = player_cmp.max_fall_speed

        # Update Position
        transform_cmp.position.y += physics_cmp.velocity.y * dt

        player_cmp.on_ground = False

    def handle_player_collision_x(self, player_cmp: PlayerComp, physics_cmp: PhysicsComp, player_trans_cmp: TransformComp, tile_trans_cmp: TransformComp):
        if physics_cmp.velocity.x > 0:
            player_trans_cmp.position.x = tile_trans_cmp.position.x - player_trans_cmp.width
            physics_cmp.velocity.x = 0
            player_cmp.dashing = False
        elif physics_cmp.velocity.x < 0:
            player_trans_cmp.position.x = tile_trans_cmp.position.x + tile_trans_cmp.width
            physics_cmp.velocity.x = 0
            player_cmp.dashing = False

    def handle_player_collision_y(self, player_cmp: PlayerComp, physics_cmp: PhysicsComp, player_trans_cmp: TransformComp, tile_trans_cmp: TransformComp):
        if physics_cmp.velocity.y > 0:
            player_trans_cmp.position.y = tile_trans_cmp.position.y - player_trans_cmp.height
            player_cmp.jumping = False
            player_cmp.on_ground = True
            self.player_hit_the_floor(player_cmp, physics_cmp)
            physics_cmp.velocity.y = 0
            player_cmp.dashing = False
            player_cmp.dashes_left = player_cmp.max_dash_amount
        elif physics_cmp.velocity.y < 0:
            player_trans_cmp.position.y = tile_trans_cmp.position.y + tile_trans_cmp.height
            physics_cmp.velocity.y = 0
            player_cmp.dashing = False

    def handle_player_gravity_collision(self, player_cmp: PlayerComp, physics_cmp):
        if physics_cmp.velocity.y >= 0 and not player_cmp.jumping:
            player_cmp.on_ground = True

    def player_hit_the_floor(self, player_cmp, physics_cmp):
        core.event_manager.notify(ShakeCameraEvent((physics_cmp.velocity.y / player_cmp.max_fall_speed) * 3,
                          (physics_cmp.velocity.y / player_cmp.max_fall_speed) * 0.25))
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

    def move_enemy_x(self, enemy_cmp, physics_cmp, transform_cmp, dt):
        # Apply forces
        physics_cmp.velocity.x += physics_cmp.acceleration.x * dt

        # Cap speed
        if abs(physics_cmp.velocity.x) > enemy_cmp.max_speed:
            if physics_cmp.velocity.x < 0:
                physics_cmp.velocity.x = -enemy_cmp.max_speed
            else:
                physics_cmp.velocity.x = enemy_cmp.max_speed

        # Update Position
        transform_cmp.position.x += physics_cmp.velocity.x * dt

    def move_enemy_y(self, enemy_cmp, physics_cmp, transform_cmp, dt):
        if not enemy_cmp.on_ground:
            physics_cmp.velocity.y += enemy_cmp.gravity * dt

        # Apply forces
        physics_cmp.velocity.y += physics_cmp.acceleration.y * dt

        # Update Position
        transform_cmp.position.y += physics_cmp.velocity.y * dt

        enemy_cmp.on_ground = False

    def handle_enemy_collision_x(self, enemy_cmp: EnemyComp, physics_cmp: PhysicsComp, enemy_trans_cmp: TransformComp, tile_trans_cmp: TransformComp):
        if physics_cmp.velocity.x > 0:
            enemy_trans_cmp.position.x = tile_trans_cmp.position.x - enemy_trans_cmp.width
            physics_cmp.velocity.x = 0
        elif physics_cmp.velocity.x < 0:
            enemy_trans_cmp.position.x = tile_trans_cmp.position.x + tile_trans_cmp.width
            physics_cmp.velocity.x = 0

    def handle_enemy_collision_y(self, enemy_cmp: EnemyComp, physics_cmp: PhysicsComp, enemy_trans_cmp: TransformComp, tile_trans_cmp: TransformComp):
        if physics_cmp.velocity.y > 0:
            enemy_trans_cmp.position.y = tile_trans_cmp.position.y - enemy_trans_cmp.height
            enemy_cmp.jumping = False
            enemy_cmp.on_ground = True
            physics_cmp.velocity.y = 0
        elif physics_cmp.velocity.y < 0:
            enemy_trans_cmp.position.y = tile_trans_cmp.position.y + tile_trans_cmp.height
            physics_cmp.velocity.y = 0

    def handle_enemy_gravity_collision(self, enemy_cmp: EnemyComp, physics_cmp):
        if physics_cmp.velocity.y >= 0 and not enemy_cmp.jumping:
            enemy_cmp.on_ground = True