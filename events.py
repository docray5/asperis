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