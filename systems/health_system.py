from threading import Timer

import pygame

import commands
import core
from ecs.components import HealthComp, TransformComp, RenderableComp, PlayerComp, EnemyComp, AnimatedCharacterComp, \
    AnimationType
from ecs.entity_manger import EntityManager
from ecs.system import System
from events import EventListener, Event, HitEvent, CreateParticlesEvent, SwitchAnimationForEntity


class HealthSystem(System, EventListener):

    def __init__(self, entity_manager: EntityManager, health_bar_id):
        super().__init__(entity_manager)
        self.entities_id_to_delete = []
        self.health_bar_id = health_bar_id

    def update(self, dt: float) -> None:
        for entity_id in self.entity_manager.get_entities_with(HealthComp):
            health_cmp: HealthComp | None = self.entity_manager.get_component(entity_id, HealthComp)
            if health_cmp.dead:
                continue

            if health_cmp.health <= 0:
                trans_cmp: TransformComp | None = self.entity_manager.get_component(entity_id, TransformComp)
                render_cmp: RenderableComp | None = self.entity_manager.get_component(entity_id, RenderableComp)
                health_cmp.dead = True
                # do some event that the entity got killed, IDK particles or smth
                if self.entity_manager.has_components(entity_id, PlayerComp):
                    commands.switch_to_game_over_cmd.execute()
                    # play player death animation
                    animated_character_cmp: AnimatedCharacterComp | None = self.entity_manager.get_component(entity_id,
                                                                                                             AnimatedCharacterComp)
                    if animated_character_cmp is not None:
                        core.event_manager.notify(SwitchAnimationForEntity(entity_id, AnimationType.DEATH))
                    core.event_manager.notify(
                        CreateParticlesEvent(150, trans_cmp.position.x + trans_cmp.width / 2,
                                             trans_cmp.position.y + trans_cmp.height / 2,
                                             16, 6, 4, pygame.Color(0, 0, 0),
                                             0, 360, 100, 100, 0.4, 0, 0.2))
                elif len(self.entity_manager.get_entities_with(EnemyComp)) <= 1:
                    core.won = True
                    commands.switch_to_game_over_cmd.execute()
                else:
                    animated_character_cmp: AnimatedCharacterComp | None = self.entity_manager.get_component(entity_id, AnimatedCharacterComp)
                    if animated_character_cmp is not None:
                        self.entities_id_to_delete.append(entity_id)
                        core.event_manager.notify(SwitchAnimationForEntity(entity_id, AnimationType.DEATH))
                        t = Timer((len(animated_character_cmp.death_animated_sprite.frames)-1)*
                                  animated_character_cmp.death_animated_sprite.animation_speed, self.delete_entity)
                        t.start()
                    else:
                        self.entity_manager.delete_entity(entity_id)

                    core.event_manager.notify(
                        CreateParticlesEvent(10, trans_cmp.position.x + trans_cmp.width / 2,
                                             trans_cmp.position.y + trans_cmp.height / 2,
                                             16, 6, 4, pygame.Color(render_cmp.color),
                                             0, 360, 100, 100, 0.4, 0, 0.2))

    def on_notify(self, event: Event):
        if isinstance(event, HitEvent):
            self.hit(event.entity_id, event.damage_dealt)

    def hit(self, entity_id, damage_dealt):
        health_cmp: HealthComp | None = self.entity_manager.get_component(entity_id, HealthComp)
        health_cmp.health -= damage_dealt
        if core.DEBUG:
            print(entity_id, health_cmp.health)

        if self.entity_manager.get_component(entity_id, PlayerComp):
            transform_cmp: TransformComp | None = self.entity_manager.get_component(self.health_bar_id, TransformComp)
            transform_cmp.width = core.HEALTH_BAR_WIDTH * health_cmp.health

    def delete_entity(self):
        for e_id in self.entities_id_to_delete:
            self.entity_manager.delete_entity(e_id)
        self.entities_id_to_delete.clear()