class Command:
    def execute(self):
        pass


class JumpDownCmd(Command):
    def __init__(self, player_system):
        self.player_system = player_system

    def execute(self):
        self.player_system.jump_key_down()


class MoveLeftDownCmd(Command):
    def __init__(self, player_system):
        self.player_system = player_system

    def execute(self):
        self.player_system.left_key_down()


class MoveRightDownCmd(Command):
    def __init__(self, player_system):
        self.player_system = player_system

    def execute(self):
        self.player_system.right_key_down()


class JumpUpCmd(Command):
    def __init__(self, player_system):
        self.player_system = player_system

    def execute(self):
        self.player_system.jump_key_up()


class MoveRightUpCmd(Command):
    def __init__(self, player_system):
        self.player_system = player_system

    def execute(self):
        self.player_system.right_key_up()


class MoveLeftUpCmd(Command):
    def __init__(self, player_system):
        self.player_system = player_system

    def execute(self):
        self.player_system.left_key_up()


class PointUpKeyUpCmd(Command):
    def __init__(self, player_system):
        self.player_system = player_system

    def execute(self):
        self.player_system.up_key_up()


class PointDownKeyUpCmd(Command):
    def __init__(self, player_system):
        self.player_system = player_system

    def execute(self):
        self.player_system.down_key_up()


class PointUpKeyDownCmd(Command):
    def __init__(self, player_system):
        self.player_system = player_system

    def execute(self):
        self.player_system.up_key_down()


class PointDownKeyDownCmd(Command):
    def __init__(self, player_system):
        self.player_system = player_system

    def execute(self):
        self.player_system.down_key_down()


class DashKDownCmd(Command):
    def __init__(self, player_system):
        self.player_system = player_system

    def execute(self):
        self.player_system.dash_key_down()


jump_down_cmd = None
move_left_down_cmd = None
move_right_down_cmd = None
jump_up_cmd = None
move_left_up_cmd = None
move_right_up_cmd = None
dash_k_down_cmd = None
point_up_key_up = None
point_up_key_down = None
point_down_key_up = None
point_down_key_down = None

def initialize(player_system):
    global jump_down_cmd, move_right_down_cmd, move_left_down_cmd, jump_up_cmd, move_left_up_cmd, move_right_up_cmd, \
        dash_k_down_cmd, point_down_key_down, point_up_key_down, point_down_key_up, point_up_key_up
    jump_down_cmd = JumpDownCmd(player_system)
    move_left_down_cmd = MoveLeftDownCmd(player_system)
    move_right_down_cmd = MoveRightDownCmd(player_system)
    jump_up_cmd = JumpUpCmd(player_system)
    move_left_up_cmd = MoveLeftUpCmd(player_system)
    move_right_up_cmd = MoveRightUpCmd(player_system)
    dash_k_down_cmd = DashKDownCmd(player_system)
    point_up_key_up = PointUpKeyUpCmd(player_system)
    point_down_key_down = PointDownKeyDownCmd(player_system)
    point_down_key_up = PointDownKeyUpCmd(player_system)
    point_up_key_down = PointUpKeyDownCmd(player_system)
