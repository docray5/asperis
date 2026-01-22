import pygame

import commands
import core
from ecs.components import HealthComp, TransformComp, RenderableComp, PlayerComp, EnemyComp
from ecs.entity_manger import EntityManager
from ecs.system import System
from events import EventListener, Event, HitEvent, CreateParticlesEvent


class HealthSystem(System, EventListener):

    def __init__(self, entity_manager: EntityManager):
        super().__init__(entity_manager)

    def update(self, dt: float) -> None:
        for entity_id in self.entity_manager.get_entities_with(HealthComp):
            health_cmp: HealthComp | None = self.entity_manager.get_component(entity_id, HealthComp)
            if health_cmp.health <= 0:
                trans_cmp: TransformComp | None = self.entity_manager.get_component(entity_id, TransformComp)
                render_cmp: RenderableComp | None = self.entity_manager.get_component(entity_id, RenderableComp)
                # do some event that the entity got killed, IDK particles or smth
                if self.entity_manager.has_components(entity_id, PlayerComp):
                    commands.switch_to_game_over_cmd.execute()
                    # play player death animation
                    core.event_manager.notify(
                        CreateParticlesEvent(150, trans_cmp.position.x + trans_cmp.width / 2,
                                             trans_cmp.position.y + trans_cmp.height / 2,
                                             16, 6, 4, pygame.Color(0, 0, 0),
                                             0, 360, 100, 100, 0.4, 0, 0.2))
                elif len(self.entity_manager.get_entities_with(EnemyComp)) <= 1:
                    core.won = True
                    commands.switch_to_game_over_cmd.execute()
                else:
                    self.entity_manager.delete_entity(entity_id)
                    core.event_manager.notify(
                        CreateParticlesEvent(70, trans_cmp.position.x + trans_cmp.width / 2,
                                             trans_cmp.position.y + trans_cmp.height / 2,
                                             16, 6, 4, pygame.Color(render_cmp.color),
                                             0, 360, 100, 100, 0.4, 0, 0.2))

    def on_notify(self, event: Event):
        if isinstance(event, HitEvent):
            self.hit(event.entity_id, event.damage_dealt)

    def hit(self, entity_id, damage_dealt):
        health_cmp: HealthComp | None = self.entity_manager.get_component(entity_id, HealthComp)
        health_cmp.health -= damage_dealt
        print(entity_id, health_cmp.health)