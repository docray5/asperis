import pygame

from ecs.components import TransformComp, RenderableComp, TileComp, RectToDrawComp, PlayerComp
from ecs.entity_manger import EntityManager


class Factory:
    def __init__(self, entity_manager: EntityManager):
        self.entity_manager = entity_manager

    def create_tile(self, x, y, width, height):
        tile_entity_id = self.entity_manager.create_entity()
        transform_cmp = TransformComp(pygame.math.Vector2(x, y), width, height)
        # physics_cmp = PhysicsComp()
        render_cmp = RenderableComp(pygame.Color(200, 200, 200))
        self.entity_manager.add_components(
            tile_entity_id,
            transform_cmp,
            render_cmp,
            TileComp(),
            RectToDrawComp())

        return tile_entity_id

    def create_player(self, x, y, width, height):
        player_entity_id = self.entity_manager.create_entity()
        player_comp = PlayerComp()
        transform_cmp = TransformComp(pygame.math.Vector2(x, y), width, height)
        render_cmp = RenderableComp(pygame.color.Color(255, 255, 255))
        self.entity_manager.add_components(
            player_entity_id,
            player_comp,
            transform_cmp,
            render_cmp,
            RectToDrawComp())

        return player_entity_id