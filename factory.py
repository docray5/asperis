import pygame

import core
from ecs.components import TransformComp, RenderableComp, TileComp, RectToDrawComp, PlayerComp, PhysicsComp, EnemyComp, \
    EnemyType, HealthComp, AnimatedSpriteComp, ParticleComp, CircleToDrawComp, BossComp


def create_tile(entity_manager, x, y, width, height):
    tile_entity_id = entity_manager.create_entity()
    transform_cmp = TransformComp(pygame.math.Vector2(x, y), width, height)
    # physics_cmp = PhysicsComp()
    render_cmp = RenderableComp(pygame.Color(200, 200, 200))
    entity_manager.add_components(
        tile_entity_id,
        transform_cmp,
        render_cmp,
        TileComp(),
        RectToDrawComp())

    return tile_entity_id

def create_player(entity_manager, x, y, width, height):
    player_entity_id = entity_manager.create_entity()
    player_comp = PlayerComp()
    transform_cmp = TransformComp(pygame.math.Vector2(x, y), width, height)
    render_cmp = RenderableComp(pygame.color.Color(255, 255, 255))
    physics_cmp = PhysicsComp()
    entity_manager.add_components(
        player_entity_id,
        player_comp,
        transform_cmp,
        render_cmp,
        physics_cmp,
        HealthComp(),
        RectToDrawComp())

    return player_entity_id

def create_enemy(entity_manager, x, y, width, height, max_speed=100, enemy_type=EnemyType.FOLLOWING):
    enemy_id = entity_manager.create_entity()
    transform_cmp = TransformComp(pygame.math.Vector2(x, y), width, height)
    render_cmp = RenderableComp(pygame.color.Color(255, 30, 30))
    physics_cmp = PhysicsComp()
    enemy_cmp = EnemyComp(enemy_type=enemy_type, max_speed=max_speed)
    entity_manager.add_components(
        enemy_id, transform_cmp, render_cmp, physics_cmp, enemy_cmp, HealthComp(), RectToDrawComp()
    )

    return enemy_id

def create_animated_slash_particle(entity_manager, x, y, flip_x, flip_y, rotation):
    particle_id = entity_manager.create_entity()
    img1 = core.asset_manager.get("p_slash_frame1.png")
    img2 = core.asset_manager.get("p_slash_frame2.png")
    img3 = core.asset_manager.get("p_slash_frame3.png")
    img4 = core.asset_manager.get("p_slash_frame4.png")
    entity_manager.add_components(
        particle_id,
        TransformComp(pygame.math.Vector2(x, y - img1.get_size()[1]/2), img1.get_size()[0], img1.get_size()[0], rotation=rotation),
        RenderableComp(color=pygame.color.Color(255, 255, 255), flip_x=flip_x, flip_y=flip_y),
        AnimatedSpriteComp(frames=[img1, img2, img3, img4], animation_speed=0.05)
    )

def create_animated_slash_particle2(entity_manager, x, y, flip_x, scale):
    particle_id = entity_manager.create_entity()
    img1 = core.asset_manager.get("b_slash_frame1.png")
    img2 = core.asset_manager.get("b_slash_frame2.png")
    img3 = core.asset_manager.get("b_slash_frame3.png")
    img4 = core.asset_manager.get("b_slash_frame4.png")
    img5 = core.asset_manager.get("b_slash_frame5.png")
    img6 = core.asset_manager.get("b_slash_frame6.png")
    img7 = core.asset_manager.get("b_slash_frame7.png")
    img8 = core.asset_manager.get("b_slash_frame8.png")
    img9 = core.asset_manager.get("b_slash_frame9.png")
    entity_manager.add_components(
        particle_id,
        TransformComp(pygame.math.Vector2(x, y - img1.get_size()[1] / 2), img1.get_size()[0], img1.get_size()[0],
                      rotation=0, scale=scale),
        RenderableComp(color=pygame.color.Color(255, 255, 255), flip_x=flip_x, flip_y=True),
        AnimatedSpriteComp(frames=[img1, img2, img3, img4, img5, img6, img7, img8, img9], animation_speed=0.025)
    )

def create_circle_particle(entity_manager, x, y, radius: int, color: pygame.Color, angle_direction, speed, life_duration, time_to_change_opacity):
    particle_id = entity_manager.create_entity()
    circle_to_draw_cmp = CircleToDrawComp(pygame.Surface((radius * 2, radius * 2), pygame.SRCALPHA))
    entity_manager.add_components(
        particle_id,
        TransformComp(pygame.math.Vector2(x, y), radius, radius),
        ParticleComp(life_duration=life_duration, direction=angle_direction, speed=speed, time_to_change_opacity=time_to_change_opacity),
        circle_to_draw_cmp,
        RenderableComp(color)
    )

    prep_circle_surf(circle_to_draw_cmp.surface, color, radius)

# TODO this one could be poolable
def prep_circle_surf(surface: pygame.Surface, color: pygame.Color, radius: int):
    pygame.draw.circle(surface, color, (radius, radius), radius)

def create_boss(entity_manager, x, y):
    enemy_id = entity_manager.create_entity()
    transform_cmp = TransformComp(pygame.math.Vector2(x, y), core.BOSS_SIZE[0], core.BOSS_SIZE[1])
    render_cmp = RenderableComp(pygame.color.Color(200, 20, 20))
    physics_cmp = PhysicsComp(knockback_resistance=0.15)
    enemy_cmp = EnemyComp(enemy_type=EnemyType.BOSS, max_speed=110, damage=2)
    entity_manager.add_components(
        enemy_id, transform_cmp, render_cmp, physics_cmp, enemy_cmp, BossComp(), HealthComp(health=20), RectToDrawComp(),

    )

    return enemy_id