import core
from ecs.components import EnemyComp, EnemyType, TransformComp, PhysicsComp, BossComp, RenderableComp
from ecs.entity_manger import EntityManager
from ecs.system import System
from events import BossAttackEvent


class EnemySystem(System):
    """
    Input manager for enemies
    """

    def __init__(self, entity_manager: EntityManager, player_id):
        super().__init__(entity_manager)
        self.player_id = player_id
        self.player_transform_cmp: TransformComp | None = entity_manager.get_component(player_id, TransformComp)

    def update(self, dt: float) -> None:
        for enemy_id in self.entity_manager.get_entities_with(EnemyComp):
            enemy_cmp: EnemyComp | None = self.entity_manager.get_component(enemy_id, EnemyComp)
            enemy_transform_cmp: TransformComp | None = self.entity_manager.get_component(enemy_id, TransformComp)
            enemy_physics_cmp: PhysicsComp | None = self.entity_manager.get_component(enemy_id, PhysicsComp)
            render_cmp: RenderableComp | None = self.entity_manager.get_component(enemy_id, RenderableComp)
            if enemy_cmp.enemy_type == EnemyType.FOLLOWING:
                dist_x = enemy_transform_cmp.position.x - self.player_transform_cmp.position.x
                dist_y = enemy_transform_cmp.position.y - self.player_transform_cmp.position.y

                if dist_x > 0:
                    enemy_physics_cmp.acceleration.x = -enemy_cmp.accel_rate
                    render_cmp.flip_x = False
                else:
                    enemy_physics_cmp.acceleration.x = enemy_cmp.accel_rate
                    render_cmp.flip_x = True

                enemy_cmp.last_jump_counter += dt

                if enemy_cmp.on_ground and dist_y > self.player_transform_cmp.height*1.5 and abs(dist_x) < 200 and enemy_cmp.last_jump_counter >= enemy_cmp.jump_cool_down:
                    self.jump(enemy_cmp, enemy_physics_cmp)

                if enemy_physics_cmp.is_knockback:
                    enemy_physics_cmp.acceleration.x = 0

                # handle counters:
                if enemy_cmp.collision_invincibility:
                    enemy_cmp.collision_invincibility_counter += dt
                    if enemy_cmp.collision_invincibility_counter >= enemy_cmp.collision_invincibility_time:
                        enemy_cmp.collision_invincibility_counter = 0
                        enemy_cmp.collision_invincibility = False
            elif enemy_cmp.enemy_type == EnemyType.PATROLLING:
                enemy_physics_cmp.acceleration.x = enemy_cmp.accel_rate * enemy_cmp.patrol_direction
                if enemy_cmp.patrol_direction > 0:
                    render_cmp.flip_x = False
                else:
                    render_cmp.flip_x = True
            elif enemy_cmp.enemy_type == EnemyType.BOSS:
                boss_cmp: BossComp | None = self.entity_manager.get_component(enemy_id, BossComp)

                boss_cmp.attack_dir_x = 0

                boss_cmp.last_attack_time += dt

                dist_x = enemy_transform_cmp.position.x + enemy_transform_cmp.width/2 - (self.player_transform_cmp.position.x + self.player_transform_cmp.width/2)
                dist_y = enemy_transform_cmp.position.y + enemy_transform_cmp.height/2 - (self.player_transform_cmp.position.y + self.player_transform_cmp.height/2)

                if abs(dist_x) > core.SIGHT_RANGE or abs(dist_y) > core.SIGHT_RANGE:
                    continue

                if dist_x > 0:
                    enemy_physics_cmp.acceleration.x = -enemy_cmp.accel_rate
                    boss_cmp.attack_dir_x = -1
                    render_cmp.flip_x = False
                else:
                    enemy_physics_cmp.acceleration.x = enemy_cmp.accel_rate
                    boss_cmp.attack_dir_x = 1
                    render_cmp.flip_x = True

                if boss_cmp.last_attack_time < boss_cmp.start_moving_delay:
                    enemy_physics_cmp.acceleration.x = 0
                    enemy_physics_cmp.velocity.x = 0

                if abs(dist_x) > core.ATTACK_SIGHT_RANGE or abs(dist_y) > core.ATTACK_SIGHT_RANGE:
                    continue

                if boss_cmp.last_attack_time >= boss_cmp.attack_cool_down:
                    boss_cmp.last_attack_time = 0
                    core.event_manager.notify(BossAttackEvent(enemy_id, self.player_id))

    def jump(self, enemy_cmp, enemy_physics_cmp):
        if enemy_cmp.jumping or not enemy_cmp.on_ground:
            return

        enemy_physics_cmp.velocity.y = enemy_cmp.jump_force
        enemy_cmp.jumping = True
        enemy_cmp.on_ground = False
        enemy_cmp.last_jump_counter = 0
        print("--- Enemy Jumped ---")