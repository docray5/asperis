import random
from ecs.components import Component


class EntityManager:
    """
    Manages entity creation, deletion, and component assignment.
    Uses a simple dictionary-based approach.
    """

    def __init__(self, id_bits: int = 32):
        self._id_bits: int = id_bits
        self._max_id: int = 2 ** id_bits
        self._max_retries: int = 10
        self._entities: dict[int, dict[type[Component], Component]] = {}
        self._dead_entities: set[int] = set()
        self._used_ids: set[int] = set()

    def _generate_random_id(self) -> int:
        """
        Generate random ID
        It does retry on collision and support 32-bit random number on default
        so "should" be generally safe for a lot of entities
        """
        for _ in range(self._max_retries):
            entity_id = random.randint(0, self._max_id - 1)

            if entity_id not in self._used_ids:
                return entity_id

        raise RuntimeError(
            f"Failed to generate unique ID after {self._max_retries} attempts. " +
            f"ID space exhausted: {len(self._used_ids)}/{self._max_id} used."
        )

    def create_entity(self) -> int:
        """
        Create a new entity and return its ID
        """
        entity_id = self._generate_random_id()
        self._entities[entity_id] = {}
        self._used_ids.add(entity_id)
        return entity_id

    def delete_entity(self, entity_id: int) -> None:
        """
        Mark entity for deletion (deferred)
        """
        self._dead_entities.add(entity_id)

    def purge_dead_entities(self) -> None:
        """
        Actually remove dead entities from the system
        You need to call this guy once per frame in the main method
        """
        for entity_id in self._dead_entities:
            if entity_id in self._entities:
                del self._entities[entity_id]
        self._dead_entities.clear()

    def add_component(self, entity_id: int, component: Component) -> None:
        """
        Attach a component to an entity
        """
        if entity_id not in self._entities:
            raise ValueError(f"Entity {entity_id} does not exist")
        self._entities[entity_id][type(component)] = component

    def add_components(self, entity_id: int, *components: Component) -> None:
        """
        Attach multiple components to an entity
        """
        for component in components:
            self.add_component(entity_id, component)

    def remove_component(self, entity_id: int, component_type: type[Component]) -> None:
        """
        Remove a component from an entity
        """
        if entity_id in self._entities and component_type in self._entities[entity_id]:
            del self._entities[entity_id][component_type]

    def get_component(self, entity_id: int, component_type: type[Component]) -> Component | None:
        """
        Get a specific component from an entity
        """
        if entity_id in self._entities:
            return self._entities[entity_id].get(component_type)
        return None

    def has_components(self, entity_id: int, *component_types: type[Component]) -> bool:
        """
        Check if entity has all specified components
        """
        if entity_id not in self._entities or entity_id in self._dead_entities:
            return False
        return all(comp_type in self._entities[entity_id] for comp_type in component_types)

    def get_entities_with(self, *component_types: type[Component]) -> list[int]:
        """
        (This actually gets entity ids)
        Query: Get all entities that have all specified components.
        This is the core query mechanism for systems.
        """
        matching: list[int] = []
        for entity_id, components in self._entities.items():
            if entity_id in self._dead_entities:
                continue
            if all(comp_type in components for comp_type in component_types):
                matching.append(entity_id)
        return matching
