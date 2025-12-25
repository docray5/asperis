from ecs.components import AnimatedSpriteComp
from ecs.entity_manger import EntityManager
from ecs.system import System


class ParticleSystem(System):
    def __init__(self, entity_manager: EntityManager):
        super().__init__(entity_manager)

    def update(self, dt: float) -> None:
        for entity_id in self.entity_manager.get_entities_with(AnimatedSpriteComp):
            animated_particle_cmp: AnimatedSpriteComp | None = self.entity_manager.get_component(entity_id, AnimatedSpriteComp)

            animated_particle_cmp.last_update += dt
            if animated_particle_cmp.last_update >= animated_particle_cmp.animation_speed:
                animated_particle_cmp.last_update = 0
                animated_particle_cmp.current_frame += 1
                print(animated_particle_cmp.current_frame)
                if animated_particle_cmp.current_frame >= len(animated_particle_cmp.frames):
                    animated_particle_cmp.current_frame = 0
                    if animated_particle_cmp.one_shot:
                        self.entity_manager.delete_entity(entity_id)