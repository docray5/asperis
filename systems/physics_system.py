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

        # === ENEMY-TO-ENEMY COLLISIONS ===
        self.handle_enemy_to_enemy_collisions()

        # Player-Enemy Collisions:
        for enemy_id in self.entity_manager.get_entities_with(EnemyComp):
            if player_cmp.dashing: break
            enemy_cmp: EnemyComp | None = self.entity_manager.get_component(enemy_id, EnemyComp)
            enemy_trans_cmp: TransformComp | None = self.entity_manager.get_component(enemy_id, TransformComp)
            enemy_physics_cmp: PhysicsComp | None = self.entity_manager.get_component(enemy_id, PhysicsComp)
            if enemy_cmp.enemy_type == EnemyType.FOLLOWING:

                if not self.check_collision(player_trans_cmp, enemy_trans_cmp):
                    continue

                self.attack_player(player_id, player_cmp, enemy_cmp)

                collision_direction = self.get_collision_direction(player_trans_cmp, enemy_trans_cmp)

                # Combat physics x-axis collision with player
                if collision_direction == "x":
                    relative_vel_x = player_physics_cmp.velocity.x - enemy_physics_cmp.velocity.x
                    self.handle_entity_collision_with_tile_x(enemy_cmp, enemy_physics_cmp, enemy_trans_cmp, player_trans_cmp)
                    if relative_vel_x > 0:  # Player moving right relative to enemy
                        # test without the line below
                        self.knockback(player_physics_cmp, -1, 0, 1000)
                    elif relative_vel_x < 0:  # Player moving left relative to enemy
                        self.knockback(player_physics_cmp, 1, 0, 1000)
                    else:
                        print("Alone-x: Wtf bro, this is not supposed to happen. WHAT DID YOU DO N...")

                # Combat physics y-axis collision with player
                elif collision_direction == "y":
                    self.fix_float_velocity_y(player_physics_cmp.velocity)
                    self.fix_float_velocity_y(enemy_physics_cmp.velocity)

                    if player_physics_cmp.velocity.y > 0 and enemy_physics_cmp.velocity.y <= 0:
                        print("Player landed on enemy")
                        self.handle_player_landed_on_enemy(player_trans_cmp, player_physics_cmp, enemy_trans_cmp, enemy_physics_cmp)
                    elif enemy_physics_cmp.velocity.y > 0 and player_physics_cmp.velocity.y <= 0:
                        print("Enemy landed on player")
                        self.handle_enemy_landed_on_player(enemy_trans_cmp, enemy_physics_cmp, player_trans_cmp, player_physics_cmp)
                    elif player_physics_cmp.velocity.y > 0 and enemy_physics_cmp.velocity.y > 0:
                        print("Collision while player and enemies where falling")
                        if player_trans_cmp.position.y == enemy_trans_cmp.position.y:
                            print("- Wtf bro, this is not supposed to happen. WHAT DID YOU DO N...",
                                  "Player pos equals enemy pos during ^")
                        if player_trans_cmp.position.y < enemy_trans_cmp.position.y:
                            self.handle_player_landed_on_enemy(player_trans_cmp, player_physics_cmp, enemy_trans_cmp, enemy_physics_cmp)
                        else:
                            self.handle_enemy_landed_on_player(enemy_trans_cmp, enemy_physics_cmp, player_trans_cmp, player_physics_cmp)
                    elif player_physics_cmp.velocity.y < 0 and enemy_physics_cmp.velocity.y < 0:
                        print("Collision while player and enemies where jumping")
                        if player_trans_cmp.position.y == enemy_trans_cmp.position.y:
                            print("- Wtf bro, this is not supposed to happen. WHAT DID YOU DO N...",
                                  "Player pos equals enemy pos during ^")
                        if player_trans_cmp.position.y < enemy_trans_cmp.position.y:
                            self.handle_player_landed_on_enemy(player_trans_cmp, player_physics_cmp, enemy_trans_cmp, enemy_physics_cmp)
                        else:
                            self.handle_enemy_landed_on_player(enemy_trans_cmp, enemy_physics_cmp, player_trans_cmp, player_physics_cmp)
                    else:
                        print("Alone-y: Wtf bro, this is not supposed to happen. WHAT DID YOU DO N...")

        # === SECOND COLLISION PASS ===
        # It's here because it cleans up whatever got messed up during the player-enemy collision,
        # does not cause too much of a performance loss, but thanks to this it prevents some edge cases.
        self.update_player_physics(player_cmp, player_physics_cmp, player_trans_cmp, tiles, dt, False)

        self.update_enemy_physics(tiles, dt, False)

    # === Some methods:

    def update_player_physics(self, player_cmp, physics_cmp, transform_cmp, tiles, dt, move: bool):
        self.update_entity_physics(player_cmp, physics_cmp, transform_cmp, tiles, dt, move)

    def update_enemy_physics(self, tiles, dt, move: bool):
        """Enemy physics and collisions with tiles only:"""
        for enemy_id in self.entity_manager.get_entities_with(EnemyComp):
            enemy_cmp: EnemyComp | None = self.entity_manager.get_component(enemy_id, EnemyComp)
            enemy_trans_cmp: TransformComp | None = self.entity_manager.get_component(enemy_id, TransformComp)
            enemy_physics_cmp: PhysicsComp | None = self.entity_manager.get_component(enemy_id, PhysicsComp)
            if enemy_cmp.enemy_type == EnemyType.FOLLOWING:
                self.update_entity_physics(enemy_cmp, enemy_physics_cmp, enemy_trans_cmp, tiles, dt, move)

    def update_entity_physics(self, entity_cmp, physics_cmp, transform_cmp, tiles, dt, move: bool):
        """Only move the entity and check collisions with tiles"""

        if physics_cmp.is_knockback:
            physics_cmp.knockback_counter -= dt
            if physics_cmp.knockback_counter <= 0:
                physics_cmp.is_knockback = False
                physics_cmp.knockback_counter = physics_cmp.knockback_time

        # === Y Axis ===
        if move:
            self.move_entity_y(entity_cmp, physics_cmp, transform_cmp, dt)

        # entity collision with tiles on y
        for tile_id in tiles:
            tile_trans_cmp: TransformComp | None = self.entity_manager.get_component(tile_id, TransformComp)
            if self.check_collision(transform_cmp, tile_trans_cmp):
                self.handle_entity_collision_with_tile_y(entity_cmp, physics_cmp, transform_cmp, tile_trans_cmp)
                # break
            elif self.check_collision_for_gravity(transform_cmp, tile_trans_cmp):
                self.handle_entity_gravity_collision(entity_cmp, physics_cmp)
                # break

        # === X-axis: ===
        if move:
            self.move_entity_x(entity_cmp, physics_cmp, transform_cmp, dt)

        # entity collision with tiles on x
        for tile_id in tiles:
            tile_trans_cmp: TransformComp | None = self.entity_manager.get_component(tile_id, TransformComp)
            if self.check_collision(transform_cmp, tile_trans_cmp):
                self.handle_entity_collision_with_tile_x(entity_cmp, physics_cmp, transform_cmp, tile_trans_cmp)
                # break  # TODO check if this actually helps, Only helps when you have sorted tile list by distance

    def move_entity_x(self, entity_cmp, physics_cmp, transform_cmp, dt):
        max_speed = entity_cmp.max_speed

        if isinstance(entity_cmp, PlayerComp):  # we know we are dealing with the player
            if entity_cmp.dashing:
                # allow for subtle steering during dash
                physics_cmp.velocity.x += entity_cmp.input_x_dir * 1000 * dt
                max_speed = entity_cmp.max_dash_speed
            else:
                physics_cmp.velocity.x += physics_cmp.acceleration.x * dt

                # Apply friction
                if entity_cmp.input_x_dir == 0 and not physics_cmp.is_knockback:
                    physics_cmp.velocity.x *= core.FRICTION ** (dt * 60)
                    if abs(physics_cmp.velocity.x) < 0.1:
                        physics_cmp.velocity.x = 0

                if physics_cmp.is_knockback:
                    max_speed = physics_cmp.max_knockback_speed
        elif isinstance(entity_cmp, EnemyComp):  # handle things specific for the enemy
            physics_cmp.velocity.x += physics_cmp.acceleration.x * dt

            if entity_cmp.enemy_type == EnemyType.FOLLOWING and not entity_cmp.on_ground:
                max_speed /= 2

            if physics_cmp.is_knockback:
                max_speed = physics_cmp.max_knockback_speed

        # Cap speed
        self.clamp_velocity_x(physics_cmp.velocity, max_speed)

        # Update Position
        transform_cmp.position.x += physics_cmp.velocity.x * dt

    def move_entity_y(self, entity_cmp, physics_cmp, transform_cmp, dt):
        if isinstance(entity_cmp, PlayerComp):
            if not entity_cmp.on_ground and not entity_cmp.dashing:
                physics_cmp.velocity.y += entity_cmp.gravity * dt
        elif isinstance(entity_cmp, EnemyComp):
            if not entity_cmp.on_ground:
                physics_cmp.velocity.y += entity_cmp.gravity * dt

        # Apply forces
        physics_cmp.velocity.y += physics_cmp.acceleration.y * dt

        # Cap speed
        self.clamp_velocity_y(physics_cmp.velocity, entity_cmp.max_fall_speed)

        # Update Position
        transform_cmp.position.y += physics_cmp.velocity.y * dt

        entity_cmp.on_ground = False

    def handle_entity_collision_with_tile_x(self, entity_cmp, physics_cmp: PhysicsComp,
                                          entity_trans_cmp: TransformComp, tile_trans_cmp: TransformComp):
        if physics_cmp.velocity.x > 0:
            entity_trans_cmp.position.x = tile_trans_cmp.position.x - entity_trans_cmp.width
            physics_cmp.velocity.x = 0
            if isinstance(entity_cmp, PlayerComp):
                entity_cmp.dashing = False
        elif physics_cmp.velocity.x < 0:
            entity_trans_cmp.position.x = tile_trans_cmp.position.x + tile_trans_cmp.width
            physics_cmp.velocity.x = 0
            if isinstance(entity_cmp, PlayerComp):
                entity_cmp.dashing = False

    def handle_entity_collision_with_tile_y(self, entity_cmp, physics_cmp: PhysicsComp,
                                            entity_trans_cmp: TransformComp, tile_trans_cmp: TransformComp):
        if physics_cmp.velocity.y > 0:
            entity_trans_cmp.position.y = tile_trans_cmp.position.y - entity_trans_cmp.height
            entity_cmp.jumping = False
            entity_cmp.on_ground = True

            if isinstance(entity_cmp, PlayerComp):
                self.player_hit_the_floor(entity_cmp, physics_cmp)
                entity_cmp.dashing = False
                entity_cmp.dashes_left = entity_cmp.max_dash_amount

            physics_cmp.velocity.y = 0
        elif physics_cmp.velocity.y < 0:
            entity_trans_cmp.position.y = tile_trans_cmp.position.y + tile_trans_cmp.height
            physics_cmp.velocity.y = 0
            if isinstance(entity_cmp, PlayerComp):
                entity_cmp.dashing = False

    def handle_entity_gravity_collision(self, entity_cmp, physics_cmp):
        if physics_cmp.velocity.y >= 0 and not entity_cmp.jumping:
            entity_cmp.on_ground = True

    def handle_player_landed_on_enemy(self, player_trans_cmp, player_physics_cmp, enemy_trans_cmp, enemy_physics_cmp):
        self.handle_e1_landed_on_e2(player_trans_cmp, player_physics_cmp, enemy_trans_cmp, enemy_physics_cmp)

    def handle_enemy_landed_on_player(self, enemy_trans_cmp, enemy_physics_cmp, player_trans_cmp, player_physics_cmp):
        self.handle_e1_landed_on_e2(enemy_trans_cmp, enemy_physics_cmp, player_trans_cmp, player_physics_cmp)

    def handle_e1_landed_on_e2(self, e1_trans_cmp, e1_physics_cmp, e2_trans_cmp, e2_physics_cmp):
        e1_trans_cmp.position.y = e2_trans_cmp.position.y - e1_trans_cmp.height
        e1_physics_cmp.velocity.y = 0

        self.knockback_set_vel_y(e1_physics_cmp, -1, 400)
        e2_physics_cmp.velocity.y = 0

    # === Enemy-to-Enemy Collision Handling ===
    def handle_enemy_to_enemy_collisions(self):
        """Check collisions between all pairs of enemies and separate them"""
        enemy_ids = self.entity_manager.get_entities_with(EnemyComp)

        # Check all pairs of enemies
        for i in range(len(enemy_ids)):
            for j in range(i + 1, len(enemy_ids)):
                enemy1_id = enemy_ids[i]
                enemy2_id = enemy_ids[j]

                enemy1_cmp: EnemyComp | None = self.entity_manager.get_component(enemy1_id, EnemyComp)
                enemy1_trans_cmp: TransformComp | None = self.entity_manager.get_component(enemy1_id, TransformComp)
                enemy1_physics_cmp: PhysicsComp | None = self.entity_manager.get_component(enemy1_id, PhysicsComp)

                enemy2_cmp: EnemyComp | None = self.entity_manager.get_component(enemy2_id, EnemyComp)
                enemy2_trans_cmp: TransformComp | None = self.entity_manager.get_component(enemy2_id, TransformComp)
                enemy2_physics_cmp: PhysicsComp | None = self.entity_manager.get_component(enemy2_id, PhysicsComp)

                # Check for collision
                if self.check_collision(enemy1_trans_cmp, enemy2_trans_cmp):
                    # Determine collision direction
                    collision_direction = self.get_collision_direction(enemy1_trans_cmp, enemy2_trans_cmp)

                    if collision_direction == "x":
                        self.separate_enemies_x(enemy1_trans_cmp, enemy1_physics_cmp,
                                                enemy2_trans_cmp, enemy2_physics_cmp)
                    else:
                        self.separate_enemies_y(enemy1_trans_cmp, enemy1_physics_cmp,
                                                enemy2_trans_cmp, enemy2_physics_cmp)

    def separate_enemies_x(self, e1_trans_cmp: TransformComp, e1_physics_cmp: PhysicsComp,
                           e2_trans_cmp: TransformComp, e2_physics_cmp: PhysicsComp):
        """Separate two enemies horizontally"""
        # Calculate overlap
        left_edge_e1 = e1_trans_cmp.position.x
        right_edge_e1 = e1_trans_cmp.position.x + e1_trans_cmp.width
        left_edge_e2 = e2_trans_cmp.position.x
        right_edge_e2 = e2_trans_cmp.position.x + e2_trans_cmp.width

        # Determine which enemy is on the left
        if left_edge_e1 < left_edge_e2:
            # E1 is on the left, push it left and E2 right
            overlap = right_edge_e1 - left_edge_e2
            e1_trans_cmp.position.x -= overlap / 2
            e2_trans_cmp.position.x += overlap / 2

            # Push apart with velocity
            e1_physics_cmp.velocity.x = -150
            e2_physics_cmp.velocity.x = 150
        else:
            # E2 is on the left, push it left and E1 right
            overlap = right_edge_e2 - left_edge_e1
            e2_trans_cmp.position.x -= overlap / 2
            e1_trans_cmp.position.x += overlap / 2

            # Push apart with velocity
            self.knockback(e2_physics_cmp, -1, 0, 700)
            self.knockback(e1_physics_cmp, 1, 0, 150)

    def separate_enemies_y(self, e1_trans_cmp: TransformComp, e1_physics_cmp: PhysicsComp,
                           e2_trans_cmp: TransformComp, e2_physics_cmp: PhysicsComp):
        """Separate two enemies vertically"""
        # Calculate overlap
        top_edge_e1 = e1_trans_cmp.position.y
        bottom_edge_e1 = e1_trans_cmp.position.y + e1_trans_cmp.height
        top_edge_e2 = e2_trans_cmp.position.y
        bottom_edge_e2 = e2_trans_cmp.position.y + e2_trans_cmp.height

        # Determine which enemy is on top
        if top_edge_e1 < top_edge_e2:
            # E1 is on top, push it up and E2 down
            overlap = bottom_edge_e1 - top_edge_e2
            e1_trans_cmp.position.y -= overlap / 2
            e2_trans_cmp.position.y += overlap / 2

            # Give upward velocity to the top one
            e1_physics_cmp.velocity.y = -200
            e2_physics_cmp.velocity.y = 100
        else:
            # E2 is on top, push it up and E1 down
            overlap = bottom_edge_e2 - top_edge_e1
            e2_trans_cmp.position.y -= overlap / 2
            e1_trans_cmp.position.y += overlap / 2

            # Give upward velocity to the top one
            self.knockback_set_vel_y(e2_physics_cmp, -1, 300)
            self.knockback_set_vel_y(e1_physics_cmp, 1, 100)

    # Player specific methods:
    def player_hit_the_floor(self, player_cmp, physics_cmp):
        core.event_manager.notify(ShakeCameraEvent((physics_cmp.velocity.y / player_cmp.max_fall_speed) * 3,
                          (physics_cmp.velocity.y / player_cmp.max_fall_speed) * 0.25))
        # do some particle effects
        # or call some event

    # Attack:
    def attack(self, player_id):
        print("Attack!")
        # update the sword hit box to be on the correct side
        player_cmp: PlayerComp | None = self.entity_manager.get_component(player_id, PlayerComp)
        player_trans_cmp: TransformComp | None = self.entity_manager.get_component(player_id, TransformComp)
        player_physics_cmp: PhysicsComp | None = self.entity_manager.get_component(player_id, PhysicsComp)

        slash_drawing_x = player_trans_cmp.position.x - player_trans_cmp.width / 2 - player_cmp.sword_hit_box.width / 2
        slash_drawing_y = player_trans_cmp.position.y
        rotation = 0
        orientation_x = True
        orientation_y = True

        if player_cmp.input_y_dir == 0:
            player_cmp.sword_hit_box.width = core.SWORD_HIT_BOX_WIDTH
            player_cmp.sword_hit_box.height = core.SWORD_HIT_BOX_HEIGHT
            player_cmp.sword_hit_box.position.y = player_trans_cmp.position.y - abs(player_trans_cmp.height-player_cmp.sword_hit_box.height) / 2
            if player_cmp.last_x_dir > 0:
                player_cmp.sword_hit_box.position.x = player_trans_cmp.position.x + player_trans_cmp.width
                slash_drawing_x = player_trans_cmp.position.x + player_trans_cmp.width - 48
            else:
                player_cmp.sword_hit_box.position.x = player_trans_cmp.position.x - player_cmp.sword_hit_box.width
                slash_drawing_x = player_trans_cmp.position.x - core.asset_manager.get("slash_frame1.png").get_size()[0] + 48
                orientation_x = False
        else:  # prioritize y axis
            rotation = 90
            player_cmp.sword_hit_box.width = core.SWORD_HIT_BOX_WIDTH
            player_cmp.sword_hit_box.height = core.SWORD_HIT_BOX_HEIGHT
            player_cmp.sword_hit_box.position.x = player_trans_cmp.position.x - abs(player_trans_cmp.width - player_cmp.sword_hit_box.width) / 2
            if player_cmp.input_y_dir < 0:
                player_cmp.sword_hit_box.width = core.SWORD_HIT_BOX_HEIGHT * 1.5
                player_cmp.sword_hit_box.height = core.SWORD_HIT_BOX_WIDTH
                player_cmp.sword_hit_box.position.x = player_trans_cmp.position.x - abs(
                    player_trans_cmp.width - player_cmp.sword_hit_box.width) / 2
                player_cmp.sword_hit_box.position.y = player_trans_cmp.position.y - player_cmp.sword_hit_box.height
                slash_drawing_y = player_trans_cmp.position.y
            else:
                player_cmp.sword_hit_box.position.y = player_trans_cmp.position.y + player_trans_cmp.height
                slash_drawing_y = player_trans_cmp.position.y + player_trans_cmp.height
                orientation_y = False

        if player_cmp.input_y_dir > 0 and player_cmp.on_ground:
            return

        factory.create_animated_slash_particle(self.entity_manager,slash_drawing_x, slash_drawing_y, orientation_x, orientation_y, rotation)

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
                if player_cmp.input_y_dir == 0:
                    if player_cmp.last_x_dir > 0:
                        self.knockback_set_vel_x(enemy_physics_cmp, 1, 1000)
                        self.knockback(player_physics_cmp, -1, 0, 100)
                    else:
                        self.knockback_set_vel_x(enemy_physics_cmp, -1, 1000)
                        self.knockback(player_physics_cmp, 1, 0, 100)
                else:
                    if player_cmp.input_y_dir < 0:
                        self.knockback_set_vel_y(enemy_physics_cmp, -1, 600)
                    else:
                        self.knockback(enemy_physics_cmp, 0, 1, 600)
                        self.knockback_set_vel_y(player_physics_cmp, -1, 600)

    def attack_player(self, player_id, player_cmp, enemy_cmp):
        core.event_manager.notify(HitEvent(player_id, enemy_cmp.damage))
        player_cmp.invincibility = True

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
                e1_trans_cmp.position.y + e1_trans_cmp.height + 1 > e2_trans_cmp.position.y and
                e1_trans_cmp.position.y < e2_trans_cmp.position.y + e2_trans_cmp.height)

    def knockback(self, physics_cmp, dx, dy, force, duration=0.0):
        physics_cmp.velocity.x += force * dx
        physics_cmp.velocity.y += force * dy
        physics_cmp.is_knockback = True
        if duration != 0:
            physics_cmp.knockback_counter = duration

    def knockback_set_vel_x(self, physics_cmp, dx, force):
        physics_cmp.velocity.x = force * dx
        physics_cmp.is_knockback = True

    def knockback_set_vel_y(self, physics_cmp, dy, force):
        physics_cmp.velocity.y = force * dy
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

    def clamp_velocity_x(self, velocity, max_speed):
        if abs(velocity.x) > max_speed:
            if velocity.x < 0:
                velocity.x = -max_speed
            else:
                velocity.x = max_speed

    def clamp_velocity_y(self, velocity, max_speed):
        if abs(velocity.y) > max_speed:
            if velocity.y < 0:
                velocity.y = -max_speed
            else:
                velocity.y = max_speed

    def fix_float_velocity_y(self, velocity):
        if abs(velocity.y) < core.FLOATING_POINT_ERROR_FIX_THRESHOLD:
            velocity.y = 0
