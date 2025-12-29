import core
from ecs.components import HealthComp, PlayerComp
from ecs.entity_manger import EntityManager
from ecs.system import System
from events import EventListener, Event, HitEvent, ShakeCameraEvent


class HealthSystem(System, EventListener):

    def __init__(self, entity_manager: EntityManager):
        super().__init__(entity_manager)

    def update(self, dt: float) -> None:
        for entity_id in self.entity_manager.get_entities_with(HealthComp):
            health_cmp: HealthComp | None = self.entity_manager.get_component(entity_id, HealthComp)
            if health_cmp.health <= 0:
                # do some event that the entity got killed, IDK particles or smth
                self.entity_manager.delete_entity(entity_id)

    def on_notify(self, event: Event):
        if isinstance(event, HitEvent):
            self.hit(event.entity_id, event.damage_dealt)

    def hit(self, entity_id, damage_dealt):
        health_cmp: HealthComp | None = self.entity_manager.get_component(entity_id, HealthComp)
        if self.entity_manager.has_components(entity_id, PlayerComp):
            player_cmp: PlayerComp | None = self.entity_manager.get_component(entity_id, PlayerComp)
            if player_cmp.invincibility:
                return
            core.event_manager.notify(ShakeCameraEvent(2, 0.4))
        health_cmp.health -= damage_dealt
        print(entity_id, health_cmp.health)