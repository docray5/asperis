import core
from ecs.components import HealthComp
from ecs.entity_manger import EntityManager
from ecs.system import System
from events import EventListener, Event, HitEvent, ShakeCameraEvent


class HealthSystem(System, EventListener):

    def __init__(self, entity_manager: EntityManager):
        super().__init__(entity_manager)

    def update(self, dt: float) -> None:
        pass

    def on_notify(self, event: Event):
        if isinstance(event, HitEvent):
            self.hit(event.entity_id, event.damage_dealt)

    def hit(self, entity_id, damage_dealt):
        health_cmp: HealthComp | None = self.entity_manager.get_component(entity_id, HealthComp)
        health_cmp.health -= damage_dealt
        print(entity_id, health_cmp.health)
        core.event_manager.notify(ShakeCameraEvent(1, 1))