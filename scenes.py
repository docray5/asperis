import pygame

import commands
import core
import factory
from commands import SwitchSceneToGameCmd, PauseGameCmd, SwitchSceneToMenuCmd
from ecs.components import PhysicsComp, PlayerComp, EnemyType, RenderableComp, ClickableComp
from ecs.entity_manger import EntityManager
from ecs.system_manager import SystemManager
from events import CreateParticlesEvent
from systems.camera_system import CameraSystem
from systems.clickable_system import ClickableSystem
from systems.enemy_system import EnemySystem
from systems.health_system import HealthSystem
from systems.input_system import InputSystem
from systems.particle_system import ParticleSystem
from systems.physics_system import PhysicsSystem
from systems.player_system import PlayerSystem
from systems.render_system import RenderSystem


class Scene:
    def __init__(self):
        self.entity_manager = EntityManager()
        self.system_manager = SystemManager()

    def initialize(self, scene_manager, screen):
        """This is where you create all the entities for the currently displayed scene"""
        pass

    def update(self, dt):
        self.entity_manager.purge_dead_entities()

        self.system_manager.update(dt)


class SceneManager:
    def __init__(self, current_scene, screen):
        self.current_scene: Scene = current_scene
        self.screen = screen
        self.current_scene.initialize(self, self.screen)

    def update(self, dt):
        self.current_scene.update(dt)

    def switch_scene(self, new_scene):
        self.current_scene = new_scene
        self.current_scene.initialize(self, self.screen)


class MenuScene(Scene):
    def initialize(self, scene_manager, screen):
        core.reinitialize()

        factory.create_button(self.entity_manager, core.VIEWPORT_WIDTH / 2, core.VIEWPORT_HEIGHT / 2, 128, 32, "play", SwitchSceneToGameCmd(scene_manager))
        factory.create_button(self.entity_manager, core.VIEWPORT_WIDTH / 2, core.VIEWPORT_HEIGHT / 2 + 8 + 32, 128, 32, "quit", commands.quit_cmd)

        # systems
        particle_system = ParticleSystem(self.entity_manager)
        clickable_system = ClickableSystem(self.entity_manager)

        self.system_manager.add_system(InputSystem(self.entity_manager))
        self.system_manager.add_system(particle_system)
        self.system_manager.add_system(RenderSystem(self.entity_manager, screen))

        # events and commands:
        commands.initialize(clickable_system)

        core.event_manager.subscribe(particle_system)
        core.event_manager.subscribe(clickable_system)

        factory.create_label(self.entity_manager, core.VIEWPORT_WIDTH / 2, 32, 15, pygame.Color(244, 244, 244), "Welcome to my game!")
        factory.create_label(self.entity_manager, core.VIEWPORT_WIDTH / 2, 32*2, 15, pygame.Color(244, 244, 244), "Controls: WASD - walk, Space - jump, LCTRL - dash, RIGHT Control or Mouse Button - slash.")
        factory.create_label(self.entity_manager, core.VIEWPORT_WIDTH / 2, 32*3, 15, pygame.Color(244, 244, 244), "The objective is to kill all the enemies.")
        factory.create_label(self.entity_manager, core.VIEWPORT_WIDTH / 2, 32*4, 15, pygame.Color(core.WIN_COLOR), "Enjoy!")


class GameScene(Scene):
    def __init__(self):
        super().__init__()
        self.pause_menu_entities = None

    def initialize(self, scene_manager, screen):
        core.reinitialize()

        player_id = factory.create_player(self.entity_manager, 0, 0, 32, 48)

        factory.create_tile(self.entity_manager, 64, core.VIEWPORT_HEIGHT - 72, 128, 16)
        factory.create_tile(self.entity_manager, core.VIEWPORT_WIDTH / 2, core.VIEWPORT_HEIGHT / 2 + 32, 128, 16)
        factory.create_tile(self.entity_manager, -core.VIEWPORT_WIDTH * 2, core.VIEWPORT_HEIGHT, core.VIEWPORT_WIDTH * 4, 32)
        # factory.create_tile(self.entity_manager, core.VIEWPORT_WIDTH, core.VIEWPORT_HEIGHT-32, 32, 32) for showcase of physics

        factory.create_enemy(self.entity_manager, -100, 0, 32, 32)
        # factory.create_enemy(self.entity_manager, -200, 0, 32, 32)
        # factory.create_enemy(self.entity_manager, -300, 0, 32, 32)
        # factory.create_enemy(self.entity_manager, -400, 0, 32, 32)
        factory.create_enemy(self.entity_manager, core.VIEWPORT_WIDTH / 2 + 64, core.VIEWPORT_HEIGHT / 2, 32, 32, 80,
                             EnemyType.PATROLLING)

        factory.create_boss(self.entity_manager, core.VIEWPORT_WIDTH * 2 - core.BOSS_SIZE[0], 0)

        # Set up the engine's systems
        player_system = PlayerSystem(self.entity_manager, self.entity_manager.get_component(player_id, PlayerComp),
                                     self.entity_manager.get_component(player_id, PhysicsComp))
        camera_system = CameraSystem(self.entity_manager)
        health_system = HealthSystem(self.entity_manager)
        physics_system = PhysicsSystem(self.entity_manager)
        particle_system = ParticleSystem(self.entity_manager)
        clickable_system = ClickableSystem(self.entity_manager)

        self.pause_menu_entities = [
            factory.create_darker_overlay(self.entity_manager),
            factory.create_button(self.entity_manager, core.VIEWPORT_WIDTH / 2, core.VIEWPORT_HEIGHT / 2,
                                  192, 32, ".resume.", PauseGameCmd(self)),
            factory.create_button(self.entity_manager, core.VIEWPORT_WIDTH / 2, core.VIEWPORT_HEIGHT / 2 + 8 + 32,
                                  192, 32, ".menu.", SwitchSceneToMenuCmd(scene_manager))
        ]

        self.system_manager.add_system(InputSystem(self.entity_manager))
        self.system_manager.add_system(player_system)
        self.system_manager.add_system(EnemySystem(self.entity_manager, player_id))
        self.system_manager.add_system(physics_system)
        self.system_manager.add_system(health_system)
        self.system_manager.add_system(particle_system)
        self.system_manager.add_system(camera_system)
        self.system_manager.add_system(RenderSystem(self.entity_manager, screen))

        commands.initialize(clickable_system, player_system, self, scene_manager)

        # Setup event listeners
        core.event_manager.subscribe(camera_system)
        core.event_manager.subscribe(health_system)
        core.event_manager.subscribe(physics_system)
        core.event_manager.subscribe(particle_system)
        core.event_manager.subscribe(clickable_system)

        core.won = False
        core.paused = False
        for entity_id in self.pause_menu_entities:
            render_cmp: RenderableComp | None = self.entity_manager.get_component(entity_id, RenderableComp)
            render_cmp.render = core.paused
            clickable_cmp: ClickableComp | None = self.entity_manager.get_component(entity_id, ClickableComp)
            if clickable_cmp is not None:
                clickable_cmp.clickable = core.paused

    def pause(self):
        print("Game paused")
        core.paused = not core.paused
        for system in self.system_manager.systems:
            if isinstance(system, RenderSystem) or isinstance(system, InputSystem) or isinstance(system, ClickableSystem):
                continue
            system.paused = not system.paused

        for entity_id in self.pause_menu_entities:
            render_cmp: RenderableComp | None = self.entity_manager.get_component(entity_id, RenderableComp)
            render_cmp.render = core.paused
            clickable_cmp: ClickableComp | None = self.entity_manager.get_component(entity_id, ClickableComp)
            if clickable_cmp is not None:
                clickable_cmp.clickable = core.paused

    def freeze(self):
        for system in self.system_manager.systems:
            if isinstance(system, RenderSystem) or isinstance(system, ClickableSystem) or isinstance(system, ParticleSystem):
                continue
            system.paused = not system.paused


class GameOverScene(Scene):
    def initialize(self, scene_manager, screen):
        core.reinitialize()

        # systems
        particle_system = ParticleSystem(self.entity_manager)
        clickable_system = ClickableSystem(self.entity_manager)

        self.system_manager.add_system(InputSystem(self.entity_manager))
        self.system_manager.add_system(particle_system)
        self.system_manager.add_system(RenderSystem(self.entity_manager, screen))

        # events and commands:
        commands.initialize(clickable_system)

        core.event_manager.subscribe(particle_system)
        core.event_manager.subscribe(clickable_system)

        factory.create_button(self.entity_manager, core.VIEWPORT_WIDTH / 2, core.VIEWPORT_HEIGHT / 2, 128, 32, "menu",
                              SwitchSceneToMenuCmd(scene_manager))

        text = "You're dead..."
        color = core.LOSE_COLOR

        if core.won:
            text = "Y O U   W O N !"
            color = core.WIN_COLOR

        core.event_manager.notify(
                CreateParticlesEvent(150, core.VIEWPORT_WIDTH / 2, core.VIEWPORT_HEIGHT / 2,
                                     64, 8, 7, pygame.Color(color),
                                     0, 360, 400, 200, 1, 0.5, 0.3, affected_by_camera=False))

        factory.create_label(self.entity_manager, core.VIEWPORT_WIDTH / 2, 100, 50, color, text)