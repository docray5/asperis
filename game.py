import core
from ecs.entity_manger import EntityManager
from ecs.system_manager import SystemManager


class Scene:
    def __init__(self):
        self.entity_manager = EntityManager()
        self.system_manager = SystemManager()

    def initialize(self):
        """This is where you create all the entities for the currently displayed scene"""
        pass

    def update(self, dt):
        self.entity_manager.purge_dead_entities()

        self.system_manager.update(dt)


class SceneManager:
    def __init__(self, current_scene):
        self.current_scene: Scene = current_scene

    def update(self, dt):
        self.current_scene.update(dt)