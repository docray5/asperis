from abc import ABC, abstractmethod
from ecs.entity_manger import EntityManager


class System(ABC):
    """Base class for all systems"""

    def __init__(self, entity_manager: EntityManager):
        """
        :param entity_manager: used for later accessing entities.
        """
        self.entity_manager = entity_manager
        self.paused = False

    @abstractmethod
    def update(self, dt: float) -> None:
        """
        Update the system. Called once per frame.
        You need to set up the entities that belong to this system yourself.
        Ex:
        for entity_id in self.entity_manager.get_entities_with(Position, Velocity):
            # do something
        """
        pass
