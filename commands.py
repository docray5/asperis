class Command:
    def __init__(self):
        pass

    def execute(self):
        pass


class JumpDownCmd(Command):
    def __init__(self, player_system):
        super().__init__()
        self.player_system = player_system

    def execute(self):
        self.player_system.jump_key_down()


class MoveLeftDownCmd(Command):
    def __init__(self, player_system):
        super().__init__()
        self.player_system = player_system

    def execute(self):
        self.player_system.left_key_down()


class MoveRightDownCmd(Command):
    def __init__(self, player_system):
        super().__init__()
        self.player_system = player_system

    def execute(self):
        self.player_system.right_key_down()


class JumpUpCmd(Command):
    def __init__(self, player_system):
        super().__init__()
        self.player_system = player_system

    def execute(self):
        self.player_system.jump_key_up()


class MoveRightUpCmd(Command):
    def __init__(self, player_system):
        super().__init__()
        self.player_system = player_system

    def execute(self):
        self.player_system.right_key_up()


class MoveLeftUpCmd(Command):
    def __init__(self, player_system):
        super().__init__()
        self.player_system = player_system

    def execute(self):
        self.player_system.left_key_up()

jump_down_cmd = None
move_left_down_cmd = None
move_right_down_cmd = None
jump_up_cmd = None
move_left_up_cmd = None
move_right_up_cmd = None

def initialize(player_system):
    global jump_down_cmd, move_right_down_cmd, move_left_down_cmd, \
        jump_up_cmd, move_left_up_cmd, move_right_up_cmd
    jump_down_cmd = JumpDownCmd(player_system)
    move_left_down_cmd = MoveLeftDownCmd(player_system)
    move_right_down_cmd = MoveRightDownCmd(player_system)
    jump_up_cmd = JumpUpCmd(player_system)
    move_left_up_cmd = MoveLeftUpCmd(player_system)
    move_right_up_cmd = MoveRightUpCmd(player_system)
