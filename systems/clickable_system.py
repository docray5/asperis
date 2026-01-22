from typing import override

import core
from ecs.components import ClickableComp, TransformComp
from ecs.entity_manger import EntityManager
from ecs.system import System
from events import EventListener, Event


class ClickableSystem(System, EventListener):
    def __init__(self, entity_manager: EntityManager):
        super().__init__(entity_manager)

    @override
    def update(self, dt: float) -> None:
        pass

    @override
    def on_notify(self, event: Event):
        pass
        # if isinstance(event, ShakeCameraEvent):
        #     core.camera.shake(event.strength, event.duration)

    def mouse_btn_down(self):
        for entity_id in self.entity_manager.get_entities_with(ClickableComp, TransformComp):
            transform_cmp: TransformComp | None = self.entity_manager.get_component(entity_id, TransformComp)
            clickable_cmp: ClickableComp | None = self.entity_manager.get_component(entity_id, ClickableComp)

            if clickable_cmp.clickable and self.check_collision_with_point(transform_cmp, core.mouse_pos.x, core.mouse_pos.y):
                clickable_cmp.on_click_cmd.execute()

    def mouse_motion(self):
        for entity_id in self.entity_manager.get_entities_with(ClickableComp, TransformComp):
            transform_cmp: TransformComp | None = self.entity_manager.get_component(entity_id, TransformComp)
            clickable_cmp: ClickableComp | None = self.entity_manager.get_component(entity_id, ClickableComp)

            if clickable_cmp.clickable and self.check_collision_with_point(transform_cmp, core.mouse_pos.x, core.mouse_pos.y):
                clickable_cmp.on_hover_cmd.execute()
            else:
                clickable_cmp.off_hover_cmd.execute()

    def check_collision_with_point(self, entity_trans_cmp: TransformComp, point_x, point_y):
        return (point_x >= entity_trans_cmp.position.x and
                point_x <= entity_trans_cmp.position.x + entity_trans_cmp.width and
                point_y >= entity_trans_cmp.position.y and
                point_y <= entity_trans_cmp.position.y + entity_trans_cmp.height)