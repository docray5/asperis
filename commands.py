import sys
from threading import Timer
import pygame


class Command:
    def execute(self):
        pass


class JumpDownCmd(Command):
    def __init__(self, player_system):
        self.player_system = player_system

    def execute(self):
        if self.player_system is None:
            return
        self.player_system.jump_key_down()


class MoveLeftDownCmd(Command):
    def __init__(self, player_system):
        self.player_system = player_system

    def execute(self):
        if self.player_system is None:
            return
        self.player_system.left_key_down()


class MoveRightDownCmd(Command):
    def __init__(self, player_system):
        self.player_system = player_system

    def execute(self):
        if self.player_system is None:
            return
        self.player_system.right_key_down()


class JumpUpCmd(Command):
    def __init__(self, player_system):
        self.player_system = player_system

    def execute(self):
        if self.player_system is None:
            return
        self.player_system.jump_key_up()


class MoveRightUpCmd(Command):
    def __init__(self, player_system):
        self.player_system = player_system

    def execute(self):
        if self.player_system is None:
            return
        self.player_system.right_key_up()


class MoveLeftUpCmd(Command):
    def __init__(self, player_system):
        self.player_system = player_system

    def execute(self):
        if self.player_system is None:
            return
        self.player_system.left_key_up()


class PointUpKeyUpCmd(Command):
    def __init__(self, player_system):
        self.player_system = player_system

    def execute(self):
        if self.player_system is None:
            return
        self.player_system.up_key_up()


class PointDownKeyUpCmd(Command):
    def __init__(self, player_system):
        self.player_system = player_system

    def execute(self):
        if self.player_system is None:
            return
        self.player_system.down_key_up()


class PointUpKeyDownCmd(Command):
    def __init__(self, player_system):
        self.player_system = player_system

    def execute(self):
        if self.player_system is None:
            return
        self.player_system.up_key_down()


class PointDownKeyDownCmd(Command):
    def __init__(self, player_system):
        self.player_system = player_system

    def execute(self):
        if self.player_system is None:
            return
        self.player_system.down_key_down()


class DashKDownCmd(Command):
    def __init__(self, player_system):
        self.player_system = player_system

    def execute(self):
        if self.player_system is None:
            return
        self.player_system.dash_key_down()


class AttackKeyDownCmd(Command):
    def __init__(self, player_system):
        self.player_system = player_system

    def execute(self):
        if self.player_system is None:
            return
        self.player_system.attack_key_down()


class MouseBtnDownCmd(Command):
    def __init__(self, clickable_system):
        self.clickable_system = clickable_system

    def execute(self):
        self.clickable_system.mouse_btn_down()


class MouseMotionCmd(Command):
    def __init__(self, clickable_system):
        self.clickable_system = clickable_system

    def execute(self):
        self.clickable_system.mouse_motion()


class ChangeColorToCmd(Command):
    def __init__(self, renderable_cmp, new_color):
        self.renderable_cmp = renderable_cmp
        self.new_color = new_color

    def execute(self):
        self.renderable_cmp.color = self.new_color


class SwitchSceneToMenuCmd(Command):
    def __init__(self, scene_manager):
        self.scene_manager = scene_manager

    def execute(self):
        from scenes import MenuScene
        self.scene_manager.switch_scene(MenuScene())


class SwitchSceneToGameCmd(Command):
    def __init__(self, scene_manager):
        self.scene_manager = scene_manager

    def execute(self):
        from scenes import GameScene
        self.scene_manager.switch_scene(GameScene())


class SwitchSceneToGameOverCmd(Command):
    def __init__(self, scene_manager, game_scene):
        self.scene_manager = scene_manager
        self.game_scene = game_scene

    def execute(self):
        self.game_scene.freeze()
        t = Timer(1, self._switch_to_game_over)
        t.start()


    def _switch_to_game_over(self):
        from scenes import GameOverScene
        self.scene_manager.switch_scene(GameOverScene())


class PauseGameCmd(Command):
    def __init__(self, game_scene):
        self.game_scene = game_scene

    def execute(self):
        if self.game_scene is None:
            return
        self.game_scene.pause()


class QuitCmd(Command):
    def execute(self):
        pygame.quit()
        sys.exit()


jump_down_cmd = None
move_left_down_cmd = None
move_right_down_cmd = None
jump_up_cmd = None
move_left_up_cmd = None
move_right_up_cmd = None
dash_k_down_cmd = None
point_up_key_up_cmd = None
point_up_key_down_cmd = None
point_down_key_up_cmd = None
point_down_key_down_cmd = None
attack_key_down_cmd = None
mouse_btn_down_cmd = None
mouse_motion_cmd = None
pause_game_cmd = None
quit_cmd = None
switch_to_game_over_cmd = None

def initialize(clickable_system, player_system=None, game_scene=None, scene_manager=None):
    global jump_down_cmd, move_right_down_cmd, move_left_down_cmd, jump_up_cmd, move_left_up_cmd, move_right_up_cmd, \
        dash_k_down_cmd, point_down_key_down_cmd, point_up_key_down_cmd, point_down_key_up_cmd, point_up_key_up_cmd, attack_key_down_cmd, \
        mouse_btn_down_cmd, mouse_motion_cmd, pause_game_cmd, quit_cmd, switch_to_game_over_cmd
    jump_down_cmd = JumpDownCmd(player_system)
    move_left_down_cmd = MoveLeftDownCmd(player_system)
    move_right_down_cmd = MoveRightDownCmd(player_system)
    jump_up_cmd = JumpUpCmd(player_system)
    move_left_up_cmd = MoveLeftUpCmd(player_system)
    move_right_up_cmd = MoveRightUpCmd(player_system)
    dash_k_down_cmd = DashKDownCmd(player_system)
    point_up_key_up_cmd = PointUpKeyUpCmd(player_system)
    point_down_key_down_cmd = PointDownKeyDownCmd(player_system)
    point_down_key_up_cmd = PointDownKeyUpCmd(player_system)
    point_up_key_down_cmd = PointUpKeyDownCmd(player_system)
    attack_key_down_cmd = AttackKeyDownCmd(player_system)
    mouse_btn_down_cmd = MouseBtnDownCmd(clickable_system)
    mouse_motion_cmd = MouseMotionCmd(clickable_system)
    pause_game_cmd = PauseGameCmd(game_scene)
    quit_cmd = QuitCmd()
    switch_to_game_over_cmd = SwitchSceneToGameOverCmd(scene_manager, game_scene)
