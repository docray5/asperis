import core
import factory
from ecs.components import TransformComp, PlayerComp, TileComp, PhysicsComp, EnemyComp, EnemyType
from ecs.system import System
from events import ShakeCameraEvent, HitEvent, EventListener, Event, AttackEvent


class PhysicsSystem(System, EventListener):
    """
    More like a Movement and collision system.
    Moves entities according to their force applied and Handles collisions of entities and emits events.
    """
    def __init__(self, entity_manager):
        super().__init__(entity_manager)

    def on_notify(self, event: Event):
        if isinstance(event, AttackEvent):
            self.attack(event.player_id)


    def update(self, dt: float) -> None:
        # === Initial Setup: ===
        player_id = self.entity_manager.get_entities_with(PlayerComp)[0]
        player_cmp: PlayerComp | None = self.entity_manager.get_component(player_id, PlayerComp)
        player_physics_cmp: PhysicsComp | None = self.entity_manager.get_component(player_id, PhysicsComp)
        player_trans_cmp: TransformComp | None = self.entity_manager.get_component(player_id, TransformComp)
        tiles = self.entity_manager.get_entities_with(TileComp)

        self.update_player_physics(player_cmp, player_physics_cmp, player_trans_cmp, tiles, dt, True)

        self.update_enemy_physics(tiles, dt, True)

        # Player-Enemy Collisions:
        for enemy_id in self.entity_manager.get_entities_with(EnemyComp):
            if player_cmp.dashing: break
            enemy_cmp: EnemyComp | None = self.entity_manager.get_component(enemy_id, EnemyComp)
            enemy_trans_cmp: TransformComp | None = self.entity_manager.get_component(enemy_id, TransformComp)
            enemy_physics_cmp: PhysicsComp | None = self.entity_manager.get_component(enemy_id, PhysicsComp)
            if enemy_cmp.enemy_type == EnemyType.FOLLOWING:

                if not self.check_collision(player_trans_cmp, enemy_trans_cmp):
                    continue

                core.event_manager.notify(HitEvent(player_id, enemy_cmp.damage))

                collision_direction = self.get_collision_direction(player_trans_cmp, enemy_trans_cmp)

                # Combat physics x-axis collision with player
                if collision_direction == "x":
                    if ((player_physics_cmp.velocity.x > 0 and enemy_physics_cmp.velocity.x < 0) or
                    (player_physics_cmp.velocity.x == 0 and enemy_physics_cmp.velocity.x < 0)):
                        self.handle_enemy_collision_x(enemy_cmp, enemy_physics_cmp, enemy_trans_cmp, player_trans_cmp)
                        self.knockback(player_physics_cmp, -1, 0, 1000)
                    elif ((player_physics_cmp.velocity.x < 0 and enemy_physics_cmp.velocity.x > 0) or
                    (player_physics_cmp.velocity.x == 0 and enemy_physics_cmp.velocity.x > 0)):
                        self.handle_enemy_collision_x(enemy_cmp, enemy_physics_cmp, enemy_trans_cmp, player_trans_cmp)
                        self.knockback(player_physics_cmp, 1, 0, 1000)
                    elif player_physics_cmp.velocity.x > 0 and enemy_physics_cmp.velocity.x > 0:
                        self.handle_enemy_collision_x(enemy_cmp, enemy_physics_cmp, enemy_trans_cmp, player_trans_cmp)
                        self.knockback(player_physics_cmp, -1, 0, 1000)
                    elif player_physics_cmp.velocity.x < 0 and enemy_physics_cmp.velocity.x < 0:
                        self.handle_enemy_collision_x(enemy_cmp, enemy_physics_cmp, enemy_trans_cmp, player_trans_cmp)
                        self.knockback(player_physics_cmp, 1, 0, 1000)

                # Combat physics y-axis collision with player
                elif collision_direction == "y":
                    if (player_physics_cmp.velocity.y > 0 and enemy_physics_cmp.velocity.y < 0) or \
                            (player_physics_cmp.velocity.y > 0 and enemy_physics_cmp.velocity.y == 0):
                        player_trans_cmp.position.y = enemy_trans_cmp.position.y - player_trans_cmp.height
                        player_physics_cmp.velocity.y = 0

                        self.knockback(player_physics_cmp, 0, -1, 400)
                        enemy_physics_cmp.velocity.y = 0
                        print("Player landed on enemy")
                    elif (enemy_physics_cmp.velocity.y > 0 and player_physics_cmp.velocity.y < 0) or \
                            (enemy_physics_cmp.velocity.y > 0 and player_physics_cmp.velocity.y == 0):
                        enemy_trans_cmp.position.y = player_trans_cmp.position.y - enemy_trans_cmp.height
                        enemy_physics_cmp.velocity.y = 0

                        self.knockback(enemy_physics_cmp, 0, -1, 400)
                        player_physics_cmp.velocity.y = 0
                        print("Enemy landed on player")
                    elif player_physics_cmp.velocity.y > 0 and enemy_physics_cmp.velocity.y > 0:
                        print("Collision while player and enemies where falling")
                        if player_trans_cmp.position.y < enemy_trans_cmp.position.y:
                            player_trans_cmp.position.y = enemy_trans_cmp.position.y - player_trans_cmp.height
                            player_physics_cmp.velocity.y = 0

                            self.knockback(player_physics_cmp, 0, -1, 400)
                            enemy_physics_cmp.velocity.y = 0
                        else:
                            enemy_trans_cmp.position.y = player_trans_cmp.position.y - enemy_trans_cmp.height
                            enemy_physics_cmp.velocity.y = 0

                            self.knockback(enemy_physics_cmp, 0, -1, 400)
                            player_physics_cmp.velocity.y = 0
                    elif player_physics_cmp.velocity.y < 0 and enemy_physics_cmp.velocity.y < 0:
                        print("Collision while player and enemies where jumping")
                        if player_trans_cmp.position.y < enemy_trans_cmp.position.y:
                            player_trans_cmp.position.y = enemy_trans_cmp.position.y - player_trans_cmp.height
                            player_physics_cmp.velocity.y = 0

                            self.knockback(player_physics_cmp, 0, -1, 400)
                            enemy_physics_cmp.velocity.y = 0
                        else:
                            enemy_trans_cmp.position.y = player_trans_cmp.position.y - enemy_trans_cmp.height
                            enemy_physics_cmp.velocity.y = 0

                            self.knockback(enemy_physics_cmp, 0, -1, 400)
                            player_physics_cmp.velocity.y = 0

        # === SECOND COLLISION PASS ===
        self.update_player_physics(player_cmp, player_physics_cmp, player_trans_cmp, tiles, dt, False)

        self.update_enemy_physics(tiles, dt, False)

    # === Player related methods:

    def update_player_physics(self, player_cmp, physics_cmp, transform_cmp, tiles, dt, move: bool):
        """Only move the player and check collisions with tiles"""

        if physics_cmp.is_knockback:
            physics_cmp.knockback_counter += dt
            if physics_cmp.knockback_counter >= physics_cmp.knockback_time:
                physics_cmp.is_knockback = False
                physics_cmp.knockback_counter = 0

        # === Y Axis ===
        if move:
            self.move_player_y(player_cmp, physics_cmp, transform_cmp, dt)

        # player collision with tiles on y
        for tile_id in tiles:
            tile_trans_cmp: TransformComp | None = self.entity_manager.get_component(tile_id, TransformComp)
            if self.check_collision(transform_cmp, tile_trans_cmp):
                self.handle_player_collision_y(player_cmp, physics_cmp, transform_cmp, tile_trans_cmp)
            elif self.check_collision_for_gravity(transform_cmp, tile_trans_cmp):
                self.handle_player_gravity_collision(player_cmp, physics_cmp)

        # === X-axis: ===
        if move:
            self.move_player_x(player_cmp, physics_cmp, transform_cmp, dt)

        # player collision with tiles on x
        for tile_id in tiles:
            tile_trans_cmp: TransformComp | None = self.entity_manager.get_component(tile_id, TransformComp)
            if self.check_collision(transform_cmp, tile_trans_cmp):
                self.handle_player_collision_x(player_cmp, physics_cmp, transform_cmp, tile_trans_cmp)

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

            max_speed = player_cmp.max_speed
            if physics_cmp.is_knockback:
                max_speed = physics_cmp.max_knockback_speed
            # Cap speed
            if abs(physics_cmp.velocity.x) > max_speed:
                if physics_cmp.velocity.x < 0:
                    physics_cmp.velocity.x = -max_speed
                else:
                    physics_cmp.velocity.x = max_speed

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

    # Enemy related methods:

    def update_enemy_physics(self, tiles, dt, move: bool):
        """Enemy physics and collisions with tiles only:"""
        for enemy_id in self.entity_manager.get_entities_with(EnemyComp):
            enemy_cmp: EnemyComp | None = self.entity_manager.get_component(enemy_id, EnemyComp)
            enemy_trans_cmp: TransformComp | None = self.entity_manager.get_component(enemy_id, TransformComp)
            enemy_physics_cmp: PhysicsComp | None = self.entity_manager.get_component(enemy_id, PhysicsComp)
            if enemy_cmp.enemy_type == EnemyType.FOLLOWING:

                if enemy_physics_cmp.is_knockback:
                    enemy_physics_cmp.knockback_counter += dt
                    if enemy_physics_cmp.knockback_counter >= enemy_physics_cmp.knockback_time:
                        enemy_physics_cmp.is_knockback = False
                        enemy_physics_cmp.knockback_counter = 0

                # === Y-Axis ===
                if move:
                    self.move_enemy_y(enemy_cmp, enemy_physics_cmp, enemy_trans_cmp, dt)

                for tile_id in tiles:
                    tile_trans_cmp: TransformComp | None = self.entity_manager.get_component(tile_id, TransformComp)
                    if self.check_collision(enemy_trans_cmp, tile_trans_cmp):
                        self.handle_enemy_collision_y(enemy_cmp, enemy_physics_cmp, enemy_trans_cmp, tile_trans_cmp)
                    elif self.check_collision_for_gravity(enemy_trans_cmp, tile_trans_cmp):
                        self.handle_enemy_gravity_collision(enemy_cmp, enemy_physics_cmp)

                # === X-Axis ===
                if move:
                    self.move_enemy_x(enemy_cmp, enemy_physics_cmp, enemy_trans_cmp, dt)

                for tile_id in tiles:
                    tile_trans_cmp: TransformComp | None = self.entity_manager.get_component(tile_id, TransformComp)
                    if self.check_collision(enemy_trans_cmp, tile_trans_cmp):
                        self.handle_enemy_collision_x(enemy_cmp, enemy_physics_cmp, enemy_trans_cmp, tile_trans_cmp)

    def move_enemy_x(self, enemy_cmp, physics_cmp, transform_cmp, dt):
        # Apply forces
        physics_cmp.velocity.x += physics_cmp.acceleration.x * dt


        max_speed = enemy_cmp.max_speed
        if physics_cmp.is_knockback:
            max_speed = physics_cmp.max_knockback_speed
        # Cap speed
        if abs(physics_cmp.velocity.x) > max_speed:
            if physics_cmp.velocity.x < 0:
                physics_cmp.velocity.x = -max_speed
            else:
                physics_cmp.velocity.x = max_speed

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

    # Attack:
    def attack(self, player_id):
        print("Attack!")
        # update the sword hit box to be on the correct side
        player_cmp: PlayerComp | None = self.entity_manager.get_component(player_id, PlayerComp)
        player_trans_cmp: TransformComp | None = self.entity_manager.get_component(player_id, TransformComp)
        player_physics_cmp: PhysicsComp | None = self.entity_manager.get_component(player_id, PhysicsComp)

        slash_drawing_x = 0
        orientation = True

        player_cmp.sword_hit_box.position.y = player_trans_cmp.position.y
        if player_cmp.last_x_dir > 0:
            player_cmp.sword_hit_box.position.x = player_trans_cmp.position.x + player_trans_cmp.width
            slash_drawing_x = player_trans_cmp.position.x + player_trans_cmp.width - 48
        else:
            player_cmp.sword_hit_box.position.x = player_trans_cmp.position.x - player_cmp.sword_hit_box.width
            slash_drawing_x = player_trans_cmp.position.x - core.asset_manager.get("slash_frame1.png").get_size()[0] + 48
            orientation = False

        factory.create_animated_slash_particle(self.entity_manager, slash_drawing_x, player_trans_cmp.position.y, orientation)

        # go through all the enemies and check for collision
        for enemy_id in self.entity_manager.get_entities_with(EnemyComp):
            enemy_cmp: EnemyComp | None = self.entity_manager.get_component(enemy_id, EnemyComp)
            enemy_trans_cmp: TransformComp | None = self.entity_manager.get_component(enemy_id, TransformComp)
            enemy_physics_cmp: PhysicsComp | None = self.entity_manager.get_component(enemy_id, PhysicsComp)

            print(self.check_collision(player_cmp.sword_hit_box, enemy_trans_cmp))
            print(player_cmp.sword_hit_box.position)
            print(enemy_trans_cmp.position)
            if self.check_collision(player_cmp.sword_hit_box, enemy_trans_cmp):
                core.event_manager.notify(HitEvent(enemy_id, player_cmp.damage))
                if player_cmp.last_x_dir > 0:
                    self.knockback(enemy_physics_cmp, 1, 0, 1000)
                else:
                    self.knockback(enemy_physics_cmp, -1, 0, 1000)

    # === Utils: ===

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

    def knockback(self, physics_cmp, dx, dy, force):
        physics_cmp.velocity.x += force * dx
        physics_cmp.velocity.y += force * dy
        physics_cmp.is_knockback = True

    def get_collision_direction(self, trans1: TransformComp, trans2: TransformComp) -> str:
        """Determine primary collision direction (x or y)"""
        overlap_x = min(
            trans1.position.x + trans1.width - trans2.position.x,
            trans2.position.x + trans2.width - trans1.position.x
        )
        overlap_y = min(
            trans1.position.y + trans1.height - trans2.position.y,
            trans2.position.y + trans2.height - trans1.position.y
        )

        return "x" if overlap_x < overlap_y else "y"