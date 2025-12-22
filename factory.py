import pygame

from ecs.components import TransformComp, RenderableComp, TileComp, RectToDrawComp, PlayerComp
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
    entity_manager.add_components(
        player_entity_id,
        player_comp,
        transform_cmp,
        render_cmp,
        RectToDrawComp())

    return player_entity_id