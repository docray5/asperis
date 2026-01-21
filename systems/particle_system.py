import math
import random

import factory
from ecs.components import AnimatedSpriteComp, ParticleComp, RenderableComp, TransformComp, AnimatedCharacterComp, \
    PhysicsComp, AnimationType
from ecs.entity_manger import EntityManager
from ecs.system import System
from events import EventListener, Event, CreateParticlesEvent, SwitchAnimationForEntity


class ParticleSystem(System, EventListener):
    def __init__(self, entity_manager: EntityManager):
        super().__init__(entity_manager)

    def on_notify(self, event: Event):
        if isinstance(event, CreateParticlesEvent):
            self.create_particles(event.particle_count, event.x, event.y, event.position_offset, event.radius, event.radius_offset, event.color, event.angle_from, event.angle_to, event.speed, event.speed_offset, event.life_duration, event.life_duration_offset, event.time_to_change_opacity)
        if isinstance(event, SwitchAnimationForEntity):
            animated_particle_cmp: AnimatedCharacterComp | None = self.entity_manager.get_component(event.entity_id, AnimatedCharacterComp)
            if animated_particle_cmp is not None:
                if not animated_particle_cmp.current_animation == AnimationType.ATTACK:
                    animated_particle_cmp.current_animation = event.new_animation_type
                    animated_particle_cmp.current_animated_sprite.current_frame = 0
                    animated_particle_cmp.current_animated_sprite.last_update = 0

    def update(self, dt: float) -> None:
        # Handle Animated Sprites
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

        # Handle Animated characters
        for entity_id in self.entity_manager.get_entities_with(AnimatedCharacterComp):
            animated_particle_cmp: AnimatedCharacterComp | None = self.entity_manager.get_component(entity_id, AnimatedCharacterComp)

            animated_particle_cmp.current_animated_sprite.last_update += dt
            if animated_particle_cmp.current_animated_sprite.last_update >= animated_particle_cmp.current_animated_sprite.animation_speed:
                animated_particle_cmp.current_animated_sprite.last_update = 0
                animated_particle_cmp.current_animated_sprite.current_frame += 1
                if animated_particle_cmp.current_animated_sprite.current_frame >= len(animated_particle_cmp.current_animated_sprite.frames):
                    animated_particle_cmp.current_animated_sprite.current_frame = 0
                    if animated_particle_cmp.current_animated_sprite.one_shot:
                        animated_particle_cmp.current_animation = AnimationType.IDLE


            # if the character is moving, after the idle animation gets triggered, we set

            if animated_particle_cmp.current_animation == AnimationType.MOVING:
                physics_cmp: PhysicsComp | None = self.entity_manager.get_component(entity_id, PhysicsComp)
                if abs(physics_cmp.velocity.x) < 0.01:
                    animated_particle_cmp.current_animation = AnimationType.IDLE

            if animated_particle_cmp.current_animation == AnimationType.IDLE:
                physics_cmp: PhysicsComp | None = self.entity_manager.get_component(entity_id, PhysicsComp)
                if abs(physics_cmp.velocity.x) >= 0.01:
                    animated_particle_cmp.current_animation = AnimationType.MOVING

            # each frame check if animation type got changed, then change the current animation:
            if animated_particle_cmp.current_animation == AnimationType.IDLE:
                animated_particle_cmp.current_animated_sprite = animated_particle_cmp.idle_animated_sprite
            elif animated_particle_cmp.current_animation == AnimationType.ATTACK:
                animated_particle_cmp.current_animated_sprite = animated_particle_cmp.attack_animated_sprite
            elif animated_particle_cmp.current_animation == AnimationType.MOVING:
                animated_particle_cmp.current_animated_sprite = animated_particle_cmp.moving_animated_sprite
            elif animated_particle_cmp.current_animation == AnimationType.HIT:
                animated_particle_cmp.current_animated_sprite = animated_particle_cmp.hit_animated_sprite

        # Handle Actual Particles:
        for entity_id in self.entity_manager.get_entities_with(ParticleComp):
            particle_cmp: ParticleComp | None = self.entity_manager.get_component(entity_id, ParticleComp)

            particle_cmp.time_alive += dt
            if particle_cmp.time_alive > particle_cmp.life_duration:
                self.entity_manager.delete_entity(entity_id)

            if particle_cmp.time_to_change_opacity > 0 and particle_cmp.time_alive > particle_cmp.time_to_change_opacity:
                render_cmp: RenderableComp | None = self.entity_manager.get_component(entity_id, RenderableComp)

                # Calculate how long we've been fading
                fade_elapsed = particle_cmp.time_alive - particle_cmp.time_to_change_opacity
                fade_remaining = particle_cmp.life_duration - particle_cmp.time_to_change_opacity

                # Calculate opacity as a percentage (0-255 range)
                fade_progress = fade_elapsed / fade_remaining
                render_cmp.color.a = int(255 * max(0.0, 1 - fade_progress))

            # calculate what needs to be added to position of the particle to go in the desired direction

            transform_cmp: TransformComp | None = self.entity_manager.get_component(entity_id, TransformComp)
            angle_rad = math.radians(particle_cmp.direction)
            displacement_x = particle_cmp.speed * math.cos(angle_rad) * dt
            displacement_y = particle_cmp.speed * math.sin(angle_rad) * dt

            transform_cmp.position.x += displacement_x
            transform_cmp.position.y += displacement_y

    def create_particles(self, particle_count, x, y, position_offset, radius, radius_offset, color,
                         angle_from, angle_to, speed, speed_offset, life_duration, life_duration_offset,
                         time_to_change_opacity):
        for i in range(particle_count):
            new_x = x + random.randint(-position_offset, position_offset)
            new_y = y + random.randint(-position_offset, position_offset)

            new_radius = radius + random.randint(-radius_offset, radius_offset)

            direction = random.randint(angle_from, angle_to)

            new_speed = speed + random.randint(-speed_offset, speed_offset)

            new_life_duration = life_duration + random.randint(int(-life_duration_offset*100), int(life_duration_offset*100))/100

            factory.create_circle_particle(self.entity_manager, new_x, new_y, new_radius, color, direction, new_speed,
                                           new_life_duration, time_to_change_opacity)