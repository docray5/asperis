from turtle import width
from typing import override

import pygame
import core
from ecs.components import RectToDrawComp, RenderableComp, TransformComp, AnimatedSpriteComp
from ecs.entity_manger import EntityManager
from ecs.system import System


class RenderSystem(System):
    def __init__(self, entity_manager: EntityManager, screen_surface: pygame.Surface):
        super().__init__(entity_manager)
        self.screen_surface: pygame.Surface = screen_surface
        self.world_surface = pygame.Surface((core.VIEWPORT_WIDTH, core.VIEWPORT_HEIGHT))
        self.scaled_surface = pygame.Surface((core.WINDOW_WIDTH, core.WINDOW_HEIGHT))

    @override
    def update(self, dt: float) -> None:
        self.screen_surface.fill(core.BLACK)
        self.world_surface.fill(core.BACKGROUND_COLOR)
        self.scaled_surface.fill(core.BACKGROUND_COLOR)

        for entity_id in self.entity_manager.get_entities_with(TransformComp, RenderableComp):
            transform_cmp: TransformComp = self.entity_manager.get_component(entity_id, TransformComp)
            renderable_cmp: RenderableComp = self.entity_manager.get_component(entity_id, RenderableComp)

            if not renderable_cmp.render:
                continue

            # apply camera position
            drawing_x = round(transform_cmp.position.x - core.camera.position.x)
            drawing_y = round(transform_cmp.position.y - core.camera.position.y)

            if self.entity_manager.has_components(entity_id, RectToDrawComp):
                rect_to_draw_cmp: RectToDrawComp = self.entity_manager.get_component(entity_id, RectToDrawComp)
                rect_to_draw_cmp.drawing_rect.update(drawing_x, drawing_y, transform_cmp.width, transform_cmp.height)
                pygame.draw.rect(self.world_surface, renderable_cmp.color, rect_to_draw_cmp.drawing_rect)
            if self.entity_manager.has_components(entity_id, AnimatedSpriteComp):
                animated_sprite_cmp: AnimatedSpriteComp | None = self.entity_manager.get_component(entity_id, AnimatedSpriteComp)
                if animated_sprite_cmp.orientation:
                    self.world_surface.blit(animated_sprite_cmp.frames[animated_sprite_cmp.current_frame], (drawing_x, drawing_y))
                else:
                    self.world_surface.blit(pygame.transform.flip(animated_sprite_cmp.frames[animated_sprite_cmp.current_frame], True, False),
                                            (drawing_x, drawing_y))

        # Update display and render scaled world
        pygame.transform.scale(self.world_surface, (core.WINDOW_WIDTH, core.WINDOW_HEIGHT), self.scaled_surface)
        self.screen_surface.blit(self.scaled_surface, (0, 0))
        pygame.display.flip()

