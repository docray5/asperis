import core
from ecs.components import PlayerComp
from ecs.entity_manger import EntityManager
from ecs.system import System


class PlayerSystem(System):
    """
    It's more like a manager, as it Manages input calls for the player.
    Does not contain physics it just sets/alerts the physics system about changes
    """
    def __init__(self, entity_manager: EntityManager, player_comp: PlayerComp | None):
        super().__init__(entity_manager)
        self.player_comp: PlayerComp = player_comp

    def update(self, dt: float) -> None:
        # Why do I split the two axis'? It helps with determining from which side did the player
        # hit an obstacle and at the same time does not affect physics accuracy.

        # handle input

        self.player_comp.input_x_dir = 0
        if self.player_comp.right_held and not self.player_comp.left_held:
            self.player_comp.input_x_dir = 1

        if self.player_comp.left_held and not self.player_comp.right_held:
            self.player_comp.input_x_dir = -1

        if self.player_comp.jump_held:
            self.player_comp.jump_buffer_counter = self.player_comp.jump_buffer_time
            if self.player_comp.on_ground:
                self.jump(self.player_comp.jump_force)

        self.player_comp.last_dashed += dt

        # Handle dash:
        if self.player_comp.dashing:
            # print("dashing...")

            self.player_comp.dash_time += dt
            if self.player_comp.dash_time >= self.player_comp.dash_duration:
                # Dash finished
                self.player_comp.dashing = False
                # if self.player_comp.velocity.y < 0:
                #     self.player_comp.velocity.y = -250
                if self.player_comp.velocity.y == 0 and self.player_comp.on_ground:
                    self.player_comp.dashes_left = self.player_comp.max_dash_amount

        # reduce penalty for changing direction and apply proper accel rates
        if self.player_comp.input_x_dir != 0 and (
                self.player_comp.velocity.x * self.player_comp.input_x_dir) < 0:
            if self.player_comp.on_ground:
                self.player_comp.acceleration.x = self.player_comp.ground_accel_rate * 2 * self.player_comp.input_x_dir
            else:
                self.player_comp.acceleration.x = self.player_comp.air_accel_rate * 2 * self.player_comp.input_x_dir
        else:
            if self.player_comp.on_ground:
                self.player_comp.acceleration.x = self.player_comp.ground_accel_rate * self.player_comp.input_x_dir
            else:
                self.player_comp.acceleration.x = self.player_comp.air_accel_rate * self.player_comp.input_x_dir

        # === Y-axis: ===

        if self.player_comp.on_ground:
            self.player_comp.coyote_counter = 0
        else:
            self.player_comp.jump_buffer_counter -= dt
            self.player_comp.coyote_counter += dt

        # if self.player_comp.last_jump_counter <= self.player_comp.jump_release_time:
        if self.player_comp.jumping:
            self.player_comp.last_jump_counter += dt

        if self.player_comp.on_ground and self.player_comp.jump_buffer_counter > 0:
            self.jump(self.player_comp.jump_force*0.5)
            self.player_comp.jump_buffer_counter = 0

        if core.DEBUG:
            print("---Player:---")
            print("On ground:", self.player_comp.on_ground)
            print("Jumping: ", self.player_comp.jumping)
            print("Jump buffer counter: ", self.player_comp.jump_buffer_counter)
            print("jump held: ", self.player_comp.jump_held)
            print("last jump counter: ", self.player_comp.last_jump_counter)
            print("coyote counter", self.player_comp.coyote_counter)

    def jump_key_down(self):
        self.player_comp.jump_held = True
        if not self.player_comp.on_ground and self.player_comp.coyote_counter < self.player_comp.coyote_time:
            self.jump(self.player_comp.jump_force)

    def jump_key_up(self):
        self.player_comp.jump_held = False

        if not self.player_comp.jumping or self.player_comp.velocity.y > 0:
            return

        self.player_comp.jumping = False
        if self.player_comp.last_jump_counter > self.player_comp.jump_release_time:
            self.player_comp.velocity.y *= 0.5
            if core.DEBUG: print("slowing down")

    def left_key_down(self):
        self.player_comp.left_held = True

    def right_key_down(self):
        self.player_comp.right_held = True

    def left_key_up(self):
        self.player_comp.left_held = False

    def right_key_up(self):
        self.player_comp.right_held = False

    def down_key_down(self):
        self.player_comp.dash_direction.y = 1

    def down_key_up(self):
        self.player_comp.dash_direction.y = 0

    def up_key_down(self):
        self.player_comp.dash_direction.y = -1

    def up_key_up(self):
        self.player_comp.dash_direction.y = 0

    def dash_key_up(self):
        pass

    def dash_key_down(self):
        if (self.player_comp.input_x_dir == 0 and self.player_comp.dash_direction.y == 0) or self.player_comp.dashes_left < 1 or self.player_comp.last_dashed < self.player_comp.dash_cool_down:
            return

        self.player_comp.velocity.x = self.player_comp.input_x_dir * core.DASH_SPEED
        self.player_comp.velocity.y = self.player_comp.dash_direction.y * core.DASH_SPEED
        if self.player_comp.dash_direction.y < 0:
            self.player_comp.velocity.y *= 0.4

        self.player_comp.dashing = True
        self.player_comp.dash_time = 0
        self.player_comp.dashes_left -= 1
        self.player_comp.last_dashed = 0
        print("Dash pressed")
        print(self.player_comp.velocity.y)

    def jump(self, force):
        if self.player_comp.jumping:
            return

        self.player_comp.velocity.y = force
        self.player_comp.jumping = True
        self.player_comp.on_ground = False
        self.player_comp.last_jump_counter = 0
        if core.DEBUG: print("--- Player Jumped ---")
