class Event:
    """
    Abstract class for storing data about and event
    that then gets handled by listener
    """
    pass


class PlayerMovedEvent(Event):
    """
    Event data class for player movement.
    Inherits Event abstract class
    """

    def __init__(self, rect, color):
        self.rect = rect
        self.color = color


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
        self.listeners = []

    def subscribe(self, event_listener):
        self.listeners.append(event_listener)

    def unsubscribe(self, event_listener):
        self.listeners.remove(event_listener)

    def notify(self, event):
        for listener in self.listeners:
            listener.on_notify(event)