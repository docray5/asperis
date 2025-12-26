import pygame

import core
from ecs.components import TransformComp, RenderableComp, TileComp, RectToDrawComp, PlayerComp, PhysicsComp, EnemyComp, \
    EnemyType, HealthComp, AnimatedSpriteComp
from ecs.entity_manger import EntityManager


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

def create_enemy(entity_manager, x, y, width, height):
    enemy_id = entity_manager.create_entity()
    transform_cmp = TransformComp(pygame.math.Vector2(x, y), width, height)
    render_cmp = RenderableComp(pygame.color.Color(255, 30, 30))
    physics_cmp = PhysicsComp()
    enemy_cmp = EnemyComp(EnemyType.FOLLOWING)
    entity_manager.add_components(
        enemy_id, transform_cmp, render_cmp, physics_cmp, enemy_cmp, HealthComp(), RectToDrawComp()
    )

    return enemy_id

def create_animated_slash_particle(entity_manager, x, y, flip_x, flip_y, rotation):
    particle_id = entity_manager.create_entity()
    img1 = core.asset_manager.get("slash_frame1.png")
    img2 = core.asset_manager.get("slash_frame2.png")
    img3 = core.asset_manager.get("slash_frame3.png")
    img4 = core.asset_manager.get("slash_frame4.png")
    entity_manager.add_components(
        particle_id,
        TransformComp(pygame.math.Vector2(x, y - img1.get_size()[1]/2), img1.get_size()[0], img1.get_size()[0], rotation=rotation),
        RenderableComp(color=pygame.color.Color(255, 255, 255), flip_x=flip_x, flip_y=flip_y),
        AnimatedSpriteComp(frames=[img1, img2, img3, img4], animation_speed=0.05)
    )