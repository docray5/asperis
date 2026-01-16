from typing import override

import pygame
import core
from ecs.components import RectToDrawComp, RenderableComp, TransformComp, AnimatedSpriteComp, PlayerComp, \
    CircleToDrawComp, BossComp
from ecs.entity_manger import EntityManager
from ecs.system import System


class RenderSystem(System):
    def __init__(self, entity_manager: EntityManager, screen_surface: pygame.Surface):
        super().__init__(entity_manager)
        self.screen_surface: pygame.Surface = screen_surface
        self.world_surface = pygame.Surface((core.VIEWPORT_WIDTH, core.VIEWPORT_HEIGHT), pygame.SRCALPHA)
        self.scaled_surface = pygame.Surface((core.WINDOW_WIDTH, core.WINDOW_HEIGHT), pygame.SRCALPHA)

    @override
    def update(self, dt: float) -> None:
        self.screen_surface.fill(core.BACKGROUND_COLOR)
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
                anim_spr_cmp: AnimatedSpriteComp | None = self.entity_manager.get_component(entity_id, AnimatedSpriteComp)
                new_size = (anim_spr_cmp.frames[anim_spr_cmp.current_frame].get_size()[0]*transform_cmp.scale, anim_spr_cmp.frames[anim_spr_cmp.current_frame].get_size()[1]*transform_cmp.scale)
                sprite_to_draw = pygame.Surface(new_size).convert_alpha()
                pygame.transform.scale(anim_spr_cmp.frames[anim_spr_cmp.current_frame], new_size, sprite_to_draw)
                sprite_to_draw = pygame.transform.rotate(sprite_to_draw, transform_cmp.rotation)
                sprite_to_draw = pygame.transform.flip(sprite_to_draw, not renderable_cmp.flip_x, not renderable_cmp.flip_y)
                self.world_surface.blit(sprite_to_draw, (drawing_x, drawing_y))
            if core.DRAW_HITBOXES:
                if self.entity_manager.has_components(entity_id, PlayerComp):
                    player_cmp: PlayerComp | None = self.entity_manager.get_component(entity_id, PlayerComp)
                    hitbox_drawing_x = round(player_cmp.sword_hit_box.position.x - core.camera.position.x)
                    hitbox_drawing_y = round(player_cmp.sword_hit_box.position.y - core.camera.position.y)
                    pygame.draw.rect(self.world_surface, (255, 192, 203),
                                     pygame.Rect(hitbox_drawing_x, hitbox_drawing_y, player_cmp.sword_hit_box.width, player_cmp.sword_hit_box.height), 2)
                if self.entity_manager.has_components(entity_id, BossComp):
                    boss_cmp: BossComp | None = self.entity_manager.get_component(entity_id, BossComp)
                    hitbox_drawing_x = round(boss_cmp.sword_hit_box.position.x - core.camera.position.x)
                    hitbox_drawing_y = round(boss_cmp.sword_hit_box.position.y - core.camera.position.y)
                    pygame.draw.rect(self.world_surface, (255, 192, 203),
                                     pygame.Rect(hitbox_drawing_x, hitbox_drawing_y, boss_cmp.sword_hit_box.width,
                                                 boss_cmp.sword_hit_box.height), 2)
                    # add one for the boss
            if self.entity_manager.has_components(entity_id, CircleToDrawComp):
                circle_cmp: CircleToDrawComp | None = self.entity_manager.get_component(entity_id, CircleToDrawComp)
                circle_cmp.surface.set_alpha(renderable_cmp.color.a)
                self.world_surface.blit(circle_cmp.surface, (drawing_x, drawing_y))

        # Update display and render scaled world
        pygame.transform.scale(self.world_surface, (core.WINDOW_WIDTH, core.WINDOW_HEIGHT), self.scaled_surface)
        self.screen_surface.blit(self.scaled_surface, (0, 0))
        pygame.display.flip()

