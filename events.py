import pygame


class Event:
    """
    Abstract data class for storing data about and event
    that then gets handled by listener
    """
    pass


class ShakeCameraEvent(Event):
    def __init__(self, strength, duration):
        self.strength = strength
        self.duration = duration


class HitEvent(Event):
    def __init__(self, entity_id, damage_dealt):
        self.entity_id = entity_id
        self.damage_dealt = damage_dealt


class CreateParticlesEvent(Event):
    def __init__(self, particle_count: int, x: float, y: float, position_offset: int, radius: int, radius_offset: int,
                 color: pygame.Color, angle_from: int, angle_to: int, speed: float, speed_offset: int,
                 life_duration: float, life_duration_offset: float, time_to_change_opacity: float):
        self.particle_count = particle_count
        self.x = x
        self.y = y
        self.position_offset = position_offset
        self.radius = radius
        self.radius_offset = radius_offset
        self.color = color
        self.angle_from = angle_from
        self.angle_to = angle_to
        self.speed = speed
        self.speed_offset = speed_offset
        self.life_duration = life_duration
        self.life_duration_offset = life_duration_offset
        self.time_to_change_opacity = time_to_change_opacity


class AttackEvent(Event):
    def __init__(self, player_id):
        self.player_id = player_id


class EventListener:
    """
    Abstract class event listener
    """

    def on_notify(self, event: Event):
        """
        Abstract class for handling events by the listener
        :param event: holds event data must be a class that inherits from Event
        """
        pass


class EventManager:
    """
    Manages Events, only one per game
    """

    def __init__(self):
        self.listeners: list[EventListener] = list()

    def subscribe(self, event_listener: EventListener):
        self.listeners.append(event_listener)

    def unsubscribe(self, event_listener: EventListener):
        self.listeners.remove(event_listener)

    def notify(self, event: Event):
        for listener in self.listeners:
            listener.on_notify(event)