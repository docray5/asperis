import pygame
import core
import factory
from ecs.components import TransformComp, PlayerComp, TileComp, PhysicsComp, EnemyComp, EnemyType, RenderableComp, \
    BossComp
from ecs.system import System
from events import ShakeCameraEvent, HitEvent, EventListener, Event, PlayerAttackEvent, CreateParticlesEvent, \
    BossAttackEvent


class PhysicsSystem(System, EventListener):
    """
    More like a Movement and collision system.
    Moves entities according to their force applied and Handles collisions of entities and emits events.
    """
    def __init__(self, entity_manager):
        super().__init__(entity_manager)

    def on_notify(self, event: Event):
        if isinstance(event, PlayerAttackEvent):
            self.player_attack(event.player_id)
        elif isinstance(event, BossAttackEvent):
            self.boss_attack(event.boss_id, event.player_id)


    def update(self, dt: float) -> None:
        # === Initial Setup: === (Move these to be class attributes
        player_id = self.entity_manager.get_entities_with(PlayerComp)[0]
        player_cmp: PlayerComp | None = self.entity_manager.get_component(player_id, PlayerComp)
        player_physics_cmp: PhysicsComp | None = self.entity_manager.get_component(player_id, PhysicsComp)
        player_trans_cmp: TransformComp | None = self.entity_manager.get_component(player_id, TransformComp)
        player_render_cmp: RenderableComp | None = self.entity_manager.get_component(player_id, RenderableComp)
        tiles = self.entity_manager.get_entities_with(TileComp)

        self.update_player_physics(player_cmp, player_physics_cmp, player_trans_cmp, tiles, dt, True)

        self.update_enemy_physics(tiles, dt, True)

        # === ENEMY-TO-ENEMY COLLISIONS (unfortunately O=n^2) ===
        self.handle_enemy_to_enemy_collisions()

        # Player-Enemy Collisions:
        for enemy_id in self.entity_manager.get_entities_with(EnemyComp):
            if player_cmp.dashing or player_cmp.invincibility: break
            enemy_cmp: EnemyComp | None = self.entity_manager.get_component(enemy_id, EnemyComp)
            enemy_trans_cmp: TransformComp | None = self.entity_manager.get_component(enemy_id, TransformComp)

            if not self.check_collision(player_trans_cmp, enemy_trans_cmp):
                continue

            attack_dir_x = self.get_collision_dir_x_e1_e2(enemy_trans_cmp, player_trans_cmp)
            attack_dir_y = self.get_collision_dir_y_e1_e2(enemy_trans_cmp, player_trans_cmp)
            self.hit_the_player(player_id, player_cmp, player_trans_cmp, player_render_cmp, enemy_cmp, player_physics_cmp, attack_dir_x, attack_dir_y)

    # === Some methods: ===

    def update_player_physics(self, player_cmp, physics_cmp, transform_cmp, tiles, dt, move: bool):
        self.update_entity_physics(player_cmp, physics_cmp, transform_cmp, tiles, dt, move)

    def update_enemy_physics(self, tiles, dt, move: bool):
        """Enemy physics and collisions with tiles only:"""
        for enemy_id in self.entity_manager.get_entities_with(EnemyComp):
            enemy_cmp: EnemyComp | None = self.entity_manager.get_component(enemy_id, EnemyComp)
            enemy_trans_cmp: TransformComp | None = self.entity_manager.get_component(enemy_id, TransformComp)
            enemy_physics_cmp: PhysicsComp | None = self.entity_manager.get_component(enemy_id, PhysicsComp)

            if enemy_cmp.enemy_type == EnemyType.FOLLOWING or enemy_cmp.enemy_type == EnemyType.PATROLLING or enemy_cmp.enemy_type == EnemyType.BOSS:
                self.update_entity_physics(enemy_cmp, enemy_physics_cmp, enemy_trans_cmp, tiles, dt, move, enemy_cmp.enemy_type)

    def update_entity_physics(self, entity_cmp, physics_cmp, transform_cmp, tiles, dt, move: bool, enemy_type=None):
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
            elif self.check_collision_for_gravity(transform_cmp, tile_trans_cmp):
                self.handle_entity_gravity_collision(entity_cmp, physics_cmp)

        # additional edge detection check for patrolling enemy
        if enemy_type == EnemyType.PATROLLING and entity_cmp.on_ground and not physics_cmp.is_knockback:
            self.edge_detection_for_patrol_enemy(entity_cmp, physics_cmp, transform_cmp, tiles)

        # === X-axis: ===
        if move:
            self.move_entity_x(entity_cmp, physics_cmp, transform_cmp, dt)

        # entity collision with tiles on x
        for tile_id in tiles:
            tile_trans_cmp: TransformComp | None = self.entity_manager.get_component(tile_id, TransformComp)
            if self.check_collision(transform_cmp, tile_trans_cmp):
                self.handle_entity_collision_with_tile_x(entity_cmp, physics_cmp, transform_cmp, tile_trans_cmp)

                if enemy_type == EnemyType.PATROLLING and abs(physics_cmp.velocity.x) < 0.001:
                    physics_cmp.velocity.x = -physics_cmp.velocity.x
                    entity_cmp.patrol_direction = -entity_cmp.patrol_direction

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
            if not physics_cmp.is_knockback:  # TODO this does nothing so remove it
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

    def edge_detection_for_patrol_enemy(self, entity_cmp, physics_cmp, transform_cmp, tiles):
        # Check point ahead in movement direction
        if physics_cmp.velocity.x < 0:  # moving left
            lookahead_x = transform_cmp.position.x - core.EDGE_DETECTION_LOOKAHEAD_DIST
        else:  # moving right
            lookahead_x = transform_cmp.position.x + transform_cmp.width + core.EDGE_DETECTION_LOOKAHEAD_DIST

        check_y = transform_cmp.position.y + transform_cmp.height + 1

        # If NO ground ahead, flip direction
        found_ground = False
        for tile_check_id in tiles:
            tile_check_cmp: TransformComp | None = self.entity_manager.get_component(tile_check_id, TransformComp)
            if self.check_collision_with_point(tile_check_cmp, lookahead_x, check_y):
                found_ground = True
                break

        if not found_ground:  # No ground ahead!
            physics_cmp.velocity.x = -physics_cmp.velocity.x
            entity_cmp.patrol_direction = -entity_cmp.patrol_direction

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
                self.player_hit_the_floor(entity_cmp, physics_cmp, entity_trans_cmp)
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

    # === Enemy-to-Enemy Collision Handling ===
    def handle_enemy_to_enemy_collisions(self):
        """Check collisions between all pairs of enemies and separate them"""
        enemy_ids = self.entity_manager.get_entities_with(EnemyComp)

        # Check all pairs of enemies
        for i in range(len(enemy_ids)):
            for j in range(len(enemy_ids)):
                enemy1_id = enemy_ids[i]
                enemy2_id = enemy_ids[j]
                if enemy1_id == enemy2_id:
                    continue

                enemy1_cmp: EnemyComp | None = self.entity_manager.get_component(enemy1_id, EnemyComp)
                enemy1_trans_cmp: TransformComp | None = self.entity_manager.get_component(enemy1_id, TransformComp)

                enemy2_cmp: EnemyComp | None = self.entity_manager.get_component(enemy2_id, EnemyComp)
                enemy2_trans_cmp: TransformComp | None = self.entity_manager.get_component(enemy2_id, TransformComp)
                enemy2_physics_cmp: PhysicsComp | None = self.entity_manager.get_component(enemy2_id, PhysicsComp)

                # we don't want the boss and the patrolling enemy to collide with other enemies
                if (enemy1_cmp.enemy_type == EnemyType.BOSS or enemy2_cmp.enemy_type == EnemyType.BOSS or
                    enemy1_cmp.enemy_type == EnemyType.PATROLLING or enemy2_cmp.enemy_type == EnemyType.PATROLLING
                    or (enemy1_cmp.collision_invincibility and enemy2_cmp.collision_invincibility)):
                    continue

                # Check for collision
                if self.check_collision(enemy1_trans_cmp, enemy2_trans_cmp):
                    # apply knockback
                    attack_dir_x = self.get_collision_dir_x_e1_e2(enemy1_trans_cmp, enemy2_trans_cmp)
                    attack_dir_y = self.get_collision_dir_y_e1_e2(enemy1_trans_cmp, enemy2_trans_cmp)
                    self.knockback_set_vel_x(enemy2_physics_cmp, attack_dir_x, enemy1_cmp.knockback_force_x*0.55)
                    self.knockback_set_vel_y(enemy2_physics_cmp, attack_dir_y, enemy1_cmp.knockback_force_y*0.55)
                    enemy2_cmp.collision_invincibility = True

    @staticmethod
    def get_collision_dir_x_e1_e2(e1_trans_cmp: TransformComp, e2_trans_cmp: TransformComp) -> int:
        e1_center_x = e1_trans_cmp.position.x - e1_trans_cmp.width / 2
        e2_center_x = e2_trans_cmp.position.x - e2_trans_cmp.width / 2
        return 1 if e1_center_x < e2_center_x else -1

    @staticmethod
    def get_collision_dir_y_e1_e2(e1_trans_cmp: TransformComp, e2_trans_cmp: TransformComp) -> int:
        e1_center_y = e1_trans_cmp.position.y - e1_trans_cmp.height / 2
        e2_center_y = e2_trans_cmp.position.y - e2_trans_cmp.height / 2
        return 1 if e1_center_y < e2_center_y else -1

    # Player specific methods:
    def player_hit_the_floor(self, player_cmp, physics_cmp, trans_cmp):
        vel = physics_cmp.velocity.y / player_cmp.max_fall_speed

        core.event_manager.notify(ShakeCameraEvent(vel * 3,
                          vel * 0.25))

        core.event_manager.notify(
            CreateParticlesEvent(int(vel*20), trans_cmp.position.x + trans_cmp.width / 2,
                                 trans_cmp.position.y + trans_cmp.height,
                                 int(trans_cmp.width / 2), 4, 2, pygame.Color(230, 230, 230, 200),
                                 -30, 180+30, int(vel*100), int(vel*100), 0.4, 0.1, 0.1))

    # Attack:
    def player_attack(self, player_id):
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
            player_cmp.sword_hit_box.width = core.PLAYER_SWORD_HIT_BOX_WIDTH
            player_cmp.sword_hit_box.height = core.PLAYER_SWORD_HIT_BOX_HEIGHT
            player_cmp.sword_hit_box.position.y = player_trans_cmp.position.y - abs(player_trans_cmp.height-player_cmp.sword_hit_box.height) / 2
            if player_cmp.last_x_dir > 0:
                player_cmp.sword_hit_box.position.x = player_trans_cmp.position.x + player_trans_cmp.width
                slash_drawing_x = player_trans_cmp.position.x + player_trans_cmp.width - 48
            else:
                player_cmp.sword_hit_box.position.x = player_trans_cmp.position.x - player_cmp.sword_hit_box.width
                slash_drawing_x = player_trans_cmp.position.x - core.asset_manager.get("p_slash_frame1.png").get_size()[0] + 48
                orientation_x = False
        else:  # prioritize y axis
            rotation = 90
            player_cmp.sword_hit_box.width = core.PLAYER_SWORD_HIT_BOX_WIDTH
            player_cmp.sword_hit_box.height = core.PLAYER_SWORD_HIT_BOX_HEIGHT
            player_cmp.sword_hit_box.position.x = player_trans_cmp.position.x - abs(player_trans_cmp.width - player_cmp.sword_hit_box.width) / 2
            if player_cmp.input_y_dir < 0:
                player_cmp.sword_hit_box.width = core.PLAYER_SWORD_HIT_BOX_HEIGHT * 0.8
                player_cmp.sword_hit_box.height = core.PLAYER_SWORD_HIT_BOX_WIDTH * 1.1
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
            enemy_render_cmp: RenderableComp | None = self.entity_manager.get_component(enemy_id, RenderableComp)

            print(self.check_collision(player_cmp.sword_hit_box, enemy_trans_cmp))
            print(player_cmp.sword_hit_box.position)
            print(enemy_trans_cmp.position)
            if self.check_collision(player_cmp.sword_hit_box, enemy_trans_cmp):
                core.event_manager.notify(HitEvent(enemy_id, player_cmp.damage))
                if player_cmp.input_y_dir == 0:
                    if player_cmp.last_x_dir > 0:
                        self.knockback_set_vel_x(enemy_physics_cmp, 1, 1000)
                        self.knockback(player_physics_cmp, -1, 0, 100)
                        self.create_blood_particles(enemy_trans_cmp, enemy_render_cmp.color, -90, 90)
                    else:
                        self.knockback_set_vel_x(enemy_physics_cmp, -1, 1000)
                        self.knockback(player_physics_cmp, 1, 0, 100)
                        self.create_blood_particles(enemy_trans_cmp, enemy_render_cmp.color, 90, 270)
                else:
                    if player_cmp.input_y_dir < 0:
                        self.knockback_set_vel_y(enemy_physics_cmp, -1, 600)
                        self.create_blood_particles(enemy_trans_cmp, enemy_render_cmp.color, -180, 0)
                    else:
                        self.knockback(enemy_physics_cmp, 0, 1, 600)
                        self.knockback_set_vel_y(player_physics_cmp, -1, 600)
                        self.create_blood_particles(enemy_trans_cmp, enemy_render_cmp.color, 0, 180)

    def boss_attack(self, boss_id, player_id):
        print("Boss attack")
        # update the sword hit box to be on the correct side
        player_cmp: PlayerComp | None = self.entity_manager.get_component(player_id, PlayerComp)
        player_trans_cmp: TransformComp | None = self.entity_manager.get_component(player_id, TransformComp)
        player_physics_cmp: PhysicsComp | None = self.entity_manager.get_component(player_id, PhysicsComp)
        player_render_cmp: RenderableComp | None = self.entity_manager.get_component(player_id, RenderableComp)

        boss_cmp: BossComp | None = self.entity_manager.get_component(boss_id, BossComp)
        boss_trans_cmp: TransformComp | None = self.entity_manager.get_component(boss_id, TransformComp)
        enemy_cmp: EnemyComp | None = self.entity_manager.get_component(boss_id, EnemyComp)

        slash_drawing_x = boss_trans_cmp.position.x - boss_trans_cmp.width / 2 - boss_cmp.sword_hit_box.width / 2
        slash_drawing_y = boss_trans_cmp.position.y - 64
        orientation_x = True

        boss_cmp.sword_hit_box.width = core.BOSS_SWORD_HIT_BOX[0]
        boss_cmp.sword_hit_box.height = core.BOSS_SWORD_HIT_BOX[1]
        boss_cmp.sword_hit_box.position.y = boss_trans_cmp.position.y - abs(boss_trans_cmp.height - boss_cmp.sword_hit_box.height)
        if boss_cmp.attack_dir_x > 0:
            boss_cmp.sword_hit_box.position.x = boss_trans_cmp.position.x
            slash_drawing_x = boss_trans_cmp.position.x - 128-32
        else:
            boss_cmp.sword_hit_box.position.x = boss_trans_cmp.position.x + boss_trans_cmp.width - boss_cmp.sword_hit_box.width
            slash_drawing_x = boss_trans_cmp.position.x - boss_trans_cmp.width - core.asset_manager.get("b_slash_frame1.png").get_size()[0] + 128+32
            orientation_x = False

        factory.create_animated_slash_particle2(self.entity_manager, slash_drawing_x, slash_drawing_y, orientation_x, 3)

        print(self.check_collision(boss_cmp.sword_hit_box, player_trans_cmp))
        print(boss_cmp.sword_hit_box.position)
        print(player_trans_cmp.position)

        if self.check_collision(boss_cmp.sword_hit_box, player_trans_cmp):
            self.hit_the_player(player_id, player_cmp, player_trans_cmp, player_render_cmp, enemy_cmp, player_physics_cmp, boss_cmp.attack_dir_x, -1)

    def hit_the_player(self, player_id, player_cmp, player_trans_cmp, player_render_cmp, enemy_cmp, player_physics_cmp, attack_dir_x, attack_dir_y):
        """
        this applies the knockback and all the special events related to hitting the player (THE ONLY METHOD)
        it also runs only when the player isn't invincible or dashing.
        """
        if player_cmp.invincibility or player_cmp.dashing:
            return
        core.event_manager.notify(ShakeCameraEvent(2, 0.4))
        core.event_manager.notify(HitEvent(player_id, enemy_cmp.damage))
        player_cmp.invincibility = True
        player_cmp.invincibility_counter = 0
        self.create_player_blood_particles(player_trans_cmp)
        self.knockback_set_vel_x(player_physics_cmp, attack_dir_x, enemy_cmp.knockback_force_x)
        self.knockback_set_vel_y(player_physics_cmp, attack_dir_y, enemy_cmp.knockback_force_y)

    def create_blood_particles(self, entity_trans_cmp: TransformComp, color: pygame.Color, angle_from, angle_to):
        core.event_manager.notify(
            CreateParticlesEvent(75, entity_trans_cmp.position.x + entity_trans_cmp.width / 2,
                                 entity_trans_cmp.position.y + entity_trans_cmp.height / 2,
                                 16, 3, 2, pygame.Color(254, 104, 15),
                                 angle_from, angle_to, 200, 200, 0.4, 0.3, 0.1))

    def create_player_blood_particles(self, entity_trans_cmp: TransformComp):
        core.event_manager.notify(
            CreateParticlesEvent(50, entity_trans_cmp.position.x + entity_trans_cmp.width / 2,
                                 entity_trans_cmp.position.y + entity_trans_cmp.height / 2,
                                 int(entity_trans_cmp.width / 2), 3, 2, pygame.Color(10, 10, 10),
                                 0, 360, 200, 10, 0.4, 0, 0.1))
    # === Utils: ===

    def check_collision(self, e1_trans_cmp: TransformComp, e2_trans_cmp: TransformComp) -> bool:
        return (e1_trans_cmp.position.x + e1_trans_cmp.width > e2_trans_cmp.position.x and
                e1_trans_cmp.position.x < e2_trans_cmp.position.x + e2_trans_cmp.width and
                e1_trans_cmp.position.y + e1_trans_cmp.height > e2_trans_cmp.position.y and
                e1_trans_cmp.position.y < e2_trans_cmp.position.y + e2_trans_cmp.height)

    def check_collision_with_point(self, entity_trans_cmp: TransformComp, point_x, point_y):
        return (point_x >= entity_trans_cmp.position.x and
                point_x <= entity_trans_cmp.position.x + entity_trans_cmp.width and
                point_y >= entity_trans_cmp.position.y and
                point_y <= entity_trans_cmp.position.y + entity_trans_cmp.height)

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
        if physics_cmp.knockback_resistance == 0:
            return
        physics_cmp.velocity.x += force * dx * physics_cmp.knockback_resistance
        physics_cmp.velocity.y += force * dy * physics_cmp.knockback_resistance
        physics_cmp.is_knockback = True
        if duration != 0:
            physics_cmp.knockback_counter = duration
        else:
            physics_cmp.knockback_counter = physics_cmp.knockback_time

    def knockback_set_vel_x(self, physics_cmp, dx, force, duration=0.0):
        if physics_cmp.knockback_resistance == 0:
            return
        physics_cmp.velocity.x = force * dx * physics_cmp.knockback_resistance
        physics_cmp.is_knockback = True
        if duration != 0:
            physics_cmp.knockback_counter = duration
        else:
            physics_cmp.knockback_counter = physics_cmp.knockback_time

    def knockback_set_vel_y(self, physics_cmp, dy, force, duration=0.0):
        if physics_cmp.knockback_resistance == 0:
            return
        physics_cmp.velocity.y = force * dy * physics_cmp.knockback_resistance
        physics_cmp.is_knockback = True
        if duration != 0:
            physics_cmp.knockback_counter = duration
        else:
            physics_cmp.knockback_counter = physics_cmp.knockback_time

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
