from typing import override
import core
from ecs.components import PlayerComp, TransformComp
from ecs.entity_manger import EntityManager
from ecs.system import System
from events import EventListener, Event, ShakeCameraEvent


class CameraSystem(System, EventListener):
    def __init__(self, entity_manager: EntityManager):
        super().__init__(entity_manager)

    @override
    def update(self, dt: float) -> None:
        player_id = self.entity_manager.get_entities_with(PlayerComp)[0]
        player_cmp = self.entity_manager.get_component(player_id, TransformComp)
        core.camera.update(dt, player_cmp)

    @override
    def on_notify(self, event: Event):
        if isinstance(event, ShakeCameraEvent):
            core.camera.shake(event.strength, event.duration)
