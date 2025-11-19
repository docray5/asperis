import core

class Command:
    def __init__(self):
        pass

    def execute(self):
        pass


class JumpDownCmd(Command):
    def __init__(self, player):
        super().__init__()
        self.player = player

    def execute(self):
        self.player.jump_down()


class MoveLeftDownCmd(Command):
    def __init__(self, player):
        super().__init__()
        self.player = player

    def execute(self):
        self.player.left_key_down()


class MoveRightDownCmd(Command):
    def __init__(self, player):
        super().__init__()
        self.player = player

    def execute(self):
        self.player.right_key_down()


class JumpUpCmd(Command):
    def __init__(self, player):
        super().__init__()
        self.player = player

    def execute(self):
        self.player.jump_up()


class MoveRightUpCmd(Command):
    def __init__(self, player):
        super().__init__()
        self.player = player

    def execute(self):
        self.player.right_key_up()


class MoveLeftUpCmd(Command):
    def __init__(self, player):
        super().__init__()
        self.player = player

    def execute(self):
        self.player.left_key_up()

jump_down_cmd = None
move_left_down_cmd = None
move_right_down_cmd = None
jump_up_cmd = None
move_left_up_cmd = None
move_right_up_cmd = None

def initialize(player):
    global jump_down_cmd, move_right_down_cmd, move_left_down_cmd, \
        jump_up_cmd, move_left_up_cmd, move_right_up_cmd
    jump_down_cmd = JumpDownCmd(player)
    move_left_down_cmd = MoveLeftDownCmd(player)
    move_right_down_cmd = MoveRightDownCmd(player)
    jump_up_cmd = JumpUpCmd(player)
    move_left_up_cmd = MoveLeftUpCmd(player)
    move_right_up_cmd = MoveRightUpCmd(player)
