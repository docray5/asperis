from ecs.system import System


class SystemManager:
    """
    Kinda like the Engine from Ashley ECS framework for LibGdx
    Manages all the systems and updates them once per frame
    """

    def __init__(self):
        self.systems: list[System] = []

    def add_system(self, system: System) -> None:
        """
        Systems will be updated in the order they are added.
        """
        self.systems.append(system)

    def update(self, dt: float) -> None:
        """Update all the systems in the order with which they've been added in"""
        for system in self.systems:
            if not system.paused:
                system.update(dt)