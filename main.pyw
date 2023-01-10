import tkinter as tk

from time import time, sleep
from random import randint, choice, seed
from sys import platform
from os import listdir

import lib.utils as utils
import lib.helpers as helpers

if platform == "darwin":
    PLATFORM = "MAC"
if platform in ["win32", "win64"]:
    PLATFORM = "WINDOWS"


class MainApp(tk.Tk):
    def __init__(self):
        self.menu: tk.Menu
        self.dx: int
        self.dy: int

        self.frame_num = 0
        self.mouse_lock_pos = None

        self.dragging = False

        self.drag_window_stage = 0
        self.eat_cursor_stage = 0
        self.eat_cursor_timer = None

        self.my_window_id: int
        self.other_window_id = utils.get_active_window()
        self.second_window = None

        self.state = "Sleep"
        self.sleeping = False

        # play action instance variables
        self.action = "Idle"
        self.action_start_time = time()

        self.movement_direction = ""
        self.movement_speed = 1

        self.falling = False

        if PLATFORM == "WINDOWS":
            self.ground_level = 65  # fullscreen
        if PLATFORM == "MAC":
            self.ground_level = 70

        # init
        super().__init__()

        # add sprite frames
        self.sprite_frame = 0
        self.frames = {}
        folder = helpers.get_sub_directory("animations")
        for name in [
            n.strip().replace(".gif", "")
            for n in listdir(folder)
        ]:
            count, current, frames = helpers.init_sprite_frames(name)
            self.frames[name.split("-")[0].strip()] = {
                "count": count,
                "current": current,
                "frames": frames
            }

        # define sprite label
        self.sprite_label = tk.Label(
            self, image=self.frames["idle"]["frames"][0], bg="white")
        self.sprite_label.pack()

        self.config_window()
        self.bind_actions()
        self.add_menu()

    def main_loop(self):
        # check quit
        if self.state == "Quit":
            raise KeyboardInterrupt

        if self.second_window:
            self.second_window.update()

        self.lift()
        self.update()

        # store active windows to switch to if needed
        a_win = utils.get_active_window()
        if a_win not in (self.other_window_id, self.my_window_id):
            self.other_window_id = a_win

        # update frame num
        self.frame_num += 1
        if self.frame_num == 60:
            self.frame_num = 0

        # update sprite frame every other frame
        if self.frame_num % 2 == 0:
            try:
                self.next_sprite_frame()
            except KeyError as e:
                print(e)

        # update frame count
        if self.sprite_frame == self.movement_speed:
            self.sprite_frame = 0
        self.sprite_frame += 1

        # check if should be falling
        if (
            self.winfo_y() < self.winfo_screenheight() - self.ground_level
            and
            (
                (
                    self.state == "Play"
                    and self.action not in ["Fly", "Eat Cursor", "Drag Window"]
                ) or
                (
                    self.state == "Sleep"
                ) or
                (
                    self.state == "Quit"
                )
            )
        ):
            self.falling = True

        if not self.dragging:
            if not self.falling:
                if self.state == "Play":
                    self.play_state()
                elif self.state == "Sleep":
                    self.sleep_state()
            else:
                self.fall()

    def play_state(self):
        # reset sleep state if necesarry
        if self.sleeping:
            self.sleeping = False

        # set seed so action continuity is retained
        seed(str(self.action_start_time))

        # check if an action is being performed
        if self.action == "":
            # reset start time
            self.action_start_time = time()
            # choose new action
            action_rng = randint(0, 99)
            action_weightings = {
                "Idle": range(0, 40),
                "Walk": range(40, 70),
                "Fly": range(70, 90),
                "Eat Cursor": range(90, 95),
                "Drag Window": range(95, 100),
            }
            for action in action_weightings:
                if action_rng in action_weightings[action]:
                    self.action = action
                    break
            print(f"Doing action: {self.action}")
            # reset start time
            self.action_start_time = time()
            # reset animation frame counter
            self.sprite_frame = 0

        elif self.action == "Idle":
            limit = randint(2, 10)
            # do nothing for some time
            if time() - self.action_start_time > limit:
                self.action = ""

        elif self.action == "Eat Cursor":
            mouse_pos = utils.mouse_position()
            # determine direction to be pointing
            diff = (
                mouse_pos["x"] -
                self.winfo_x() -
                (self.winfo_width() / 2)
            )

            if abs(diff) < 10:
                self.movement_direction = ""
            else:
                self.movement_direction = "Left" if diff < 0 else "Right"

            if self.eat_cursor_stage == 0:
                # fly near mouse position
                x_offset = (
                    100 if mouse_pos["x"] < self.winfo_x()
                    else -100 - self.winfo_width()
                )
                # overwrite offset if at edge of screen
                if mouse_pos["x"] < 100:
                    x_offset = 100
                if mouse_pos["x"] > self.winfo_screenwidth() - 200:
                    x_offset = -100

                target = (
                    mouse_pos["x"] +
                    x_offset, mouse_pos["y"] - 40
                )
                at_target = helpers.fly_to_target(self, target, t_range=5)
                if at_target:
                    self.eat_cursor_stage = 1

            if self.eat_cursor_stage == 1:
                # lock mouse movement, wait 3 seconds
                if not self.eat_cursor_timer:
                    self.eat_cursor_timer = time()
                if time() - self.eat_cursor_timer > 3:
                    self.eat_cursor_stage = 2
                    self.eat_cursor_timer = None\

            if self.eat_cursor_stage == 2:
                # set timer to steadily increase speed
                if not self.eat_cursor_timer:
                    self.eat_cursor_timer = time()

                speed = int(time() - self.eat_cursor_timer) * 2

                # suck in cursor
                target = (
                    self.winfo_x() + self.winfo_width() / 2,
                    self.winfo_y() + self.winfo_height() / 2
                )
                at_target = utils.move_mouse_to_target(target, speed or 1)

                if at_target:
                    self.eat_cursor_stage = 3
                    self.eat_cursor_timer = None
                    self.mouse_lock_pos = utils.mouse_position()
                    self.config(cursor="none")

            if self.eat_cursor_stage == 3:
                self.movement_direction = ""
                # hold for 3 seconds, reset
                if not self.eat_cursor_timer:
                    self.eat_cursor_timer = time()

                if time() - self.eat_cursor_timer > 3:
                    self.config(cursor="hand2")
                    self.eat_cursor_stage = 0
                    self.eat_cursor_timer = None
                    self.action = ""
                    return

                utils.move_mouse(self.mouse_lock_pos)

        elif self.action == "Drag Window":
            if not self.second_window:
                self.drag_window_stage = 0
                self.movement_direction = ""

            try:
                self.drag_window_action()

            # catch closing of window as it is dragged
            except Exception as e:
                if str(e)[:32] == "bad window path name \".!toplevel":
                    self.second_window = None
                    self.action = ""
                    self.drag_window_stage = 0
                else:
                    raise e

        elif self.action == "Fly":
            # choose random x and y coordinate on screen to fly to
            target = (randint(100, self.winfo_screenwidth() - 100),
                      randint(120, self.winfo_screenheight() - 100))
            at_target = helpers.fly_to_target(self, target, t_range=10)
            # check if at target
            if at_target:
                self.action = ""

        elif self.action == "Walk":
            # choose random x coordinate on screen to walk to
            target = randint(100, self.winfo_screenwidth() - 100)
            at_target = helpers.walk_to_target(self, target, t_range=5)
            # check if at target
            if at_target:
                self.action = ""
                self.movement_direction = ""

    def drag_window_action(self):
        if self.drag_window_stage == 0:
            # define window
            self.second_window = tk.Toplevel()

            # find image to use
            folder = helpers.get_sub_directory("images")
            files = [f for f in listdir(folder) if f[-4:] == ".png"]
            # reset seed for choice
            seed(time())
            self.second_window.image = tk.PhotoImage(
                file=folder + choice(files)
            )

            self.second_window.title("")
            self.second_window.geometry(
                str(self.second_window.image.width()) +
                "x" +
                str(self.second_window.image.height())
            )
            self.second_window.wm_attributes("-alpha", 0)
            self.second_window.update()
            self.place_at(
                self.second_window,
                -1 * self.second_window.winfo_width() - 10,
                randint(
                    100,
                    self.winfo_screenheight() -
                    self.second_window.winfo_height()
                )
            )
            self.second_window.wm_attributes("-alpha", 1)

            # set resizable
            self.second_window.resizable(False, False)
            self.second_window.transient(self)

            # set on top of other windows
            self.second_window.wm_attributes("-topmost", 1)

            # set image
            self.second_window.iconbitmap(folder + "favicon.ico")
            tk.Label(
                self.second_window,
                image=self.second_window.image,
                bg="grey"
            ).pack()
            # set focus back
            utils.set_active_window(self.other_window_id)
            # set drag window stage
            self.drag_window_stage = 1

        elif self.drag_window_stage == 1:
            # fly to window corner
            target = (
                self.second_window.winfo_x() +
                self.second_window.winfo_width() - self.winfo_width(),
                self.second_window.winfo_y() - self.winfo_height() / 2
            )
            at_target = helpers.fly_to_target(
                self, target, t_range=10)
            if at_target:
                self.drag_window_stage = 2

        elif self.drag_window_stage == 2:
            target = (
                self.second_window.winfo_x() +
                self.second_window.winfo_width() - self.winfo_width(),
                self.second_window.winfo_y() - self.winfo_height() / 2
            )
            at_target = helpers.fly_to_target(
                self, target, t_range=5)
            if not at_target:
                self.drag_window_stage = 1

            # drag window on screen
            # drag slowly
            if self.frame_num % 4 == 0:
                self.place_at(
                    self,
                    self.winfo_x() + 1,
                    self.winfo_y()
                )
                self.place_at(
                    self.second_window,
                    self.second_window.winfo_x() + 1,
                    self.second_window.winfo_y()
                )
            # fix buggy movement on mac
            if PLATFORM == "MAC":
                if self.winfo_x() == -2:
                    self.place_at(
                        self,
                        self.winfo_x() + 2,
                        self.winfo_y()
                    )
                if self.second_window.winfo_x() == -2:
                    self.place_at(
                        self.second_window,
                        self.second_window.winfo_x() + 2,
                        self.second_window.winfo_y()
                    )
            if self.second_window.winfo_x() >= randint(
                0,
                (
                    self.winfo_screenwidth() -
                    self.second_window.winfo_width()
                )
            ):
                self.drag_window_stage = 3

        elif self.drag_window_stage == 3:
            # fly a little away from window
            target = (
                self.second_window.winfo_x() +
                self.second_window.winfo_width() + 100,
                self.second_window.winfo_y() - 50
            )
            at_target = helpers.fly_to_target(
                self, target, t_range=10)
            if at_target:
                self.drag_window_stage = 0
                self.second_window = None
                self.action = ""

    def sleep_state(self):
        if not self.sleeping:
            target = self.winfo_screenwidth() - 100
            at_target = helpers.walk_to_target(self, target, t_range=5)
            # check if at target
            if at_target:
                self.movement_direction = ""
                self.sleeping = True
        else:
            pass

    def fall(self):
        # check if still should be falling
        if self.winfo_y() > self.winfo_screenheight() - self.ground_level:
            self.falling = False
            # place back on ground
            self.place_at(
                self,
                self.winfo_x(),
                self.winfo_screenheight() - self.ground_level
            )
            self.movement_direction = ""
            return

        # only fall every other frame
        if self.frame_num % 2 == 0:
            if self.movement_direction == "Left":
                x_offset = -1
            elif self.movement_direction == "Right":
                x_offset = 1
            else:
                x_offset = 0
        else:
            x_offset = 0
        # overwrite offset if at edge
        if (
            self.winfo_x() < 0
            or self.winfo_x() > self.winfo_screenwidth() - 100
        ):
            x_offset = 0
            self.movement_direction = ""

        self.place_at(
            self,
            self.winfo_x() + x_offset,
            self.winfo_y() + self.movement_speed
        )

    def next_sprite_frame(self):
        if self.falling:
            if self.movement_direction:
                helpers.go_to_next_sprite_frame(
                    self,
                    self.frames[f"falling {self.movement_direction.lower()}"]
                )
            else:
                helpers.go_to_next_sprite_frame(
                    self, self.frames["falling"])
            return

        if self.state == "Sleep":
            if self.movement_direction != "":
                helpers.go_to_next_sprite_frame(
                    self,
                    self.frames[f"walk {self.movement_direction.lower()}"]
                )
            else:
                helpers.go_to_next_sprite_frame(self, self.frames["sleep"])

        elif self.state == "Play":
            if self.action == "Idle":
                helpers.go_to_next_sprite_frame(self, self.frames["idle"])
            elif self.action == "Fly":
                if self.movement_direction == "":
                    return
                helpers.go_to_next_sprite_frame(
                    self,
                    self.frames[f"fly {self.movement_direction.lower()}"]
                )
            elif self.action == "Walk":
                if self.movement_direction == "":
                    return
                helpers.go_to_next_sprite_frame(
                    self,
                    self.frames[f"walk {self.movement_direction.lower()}"]
                )
            elif self.action == "Drag Window":
                if self.drag_window_stage in (1, 3):
                    helpers.go_to_next_sprite_frame(
                        self,
                        self.frames[f"fly {self.movement_direction.lower()}"]
                    )
                if self.drag_window_stage == 2:
                    helpers.go_to_next_sprite_frame(
                        self,
                        self.frames["drag"]
                    )
            elif self.action == "Eat Cursor":
                if self.eat_cursor_stage == 0:
                    # fly to cursor
                    helpers.go_to_next_sprite_frame(
                        self,
                        self.frames[f"fly {self.movement_direction.lower()}"]
                    )
                if self.eat_cursor_stage == 1:
                    # wait 3 seconds
                    helpers.go_to_next_sprite_frame(
                        self,
                        self.frames[f"fly {self.movement_direction.lower()}"]
                    )
                if self.eat_cursor_stage == 2:
                    # suck in
                    if self.movement_direction:
                        helpers.go_to_next_sprite_frame(
                            self,
                            self.frames[
                                f"suck {self.movement_direction.lower()}"
                            ]
                        )
                    else:
                        helpers.go_to_next_sprite_frame(
                            self,
                            self.frames["suck"]
                        )
                if self.eat_cursor_stage == 3:
                    # wait 3 seconds
                    helpers.go_to_next_sprite_frame(
                        self,
                        self.frames["eat"]
                    )

    def config_window(self):
        # hand cursor
        self.config(cursor="hand2")
        # disable closing
        self.overrideredirect(1)
        # keep on top of other windows
        self.wm_attributes("-topmost", 1)
        # replace white with transparent
        if PLATFORM == "WINDOWS":
            self.wm_attributes("-transparentcolor", "white")
        if PLATFORM == "MAC":
            self.wm_attributes("-transparent", True)
            self.attributes("-alpha", 0.8)
            self.sprite_label.config(bg="#0f0f0f")
            # TODO: figure out how to make transparent background
        # place window starting at bottom right of screen
        self.place_at(
            self,
            self.winfo_screenwidth() - 100,
            self.winfo_screenheight() - self.ground_level
        )
        # set my window id
        self.lift()
        self.my_window_id = utils.get_active_window()

    def place_at(self, obj, x, y):
        obj.geometry(f"+{x}+{y}")

    def bind_actions(self):
        # allow to be moved
        self.bind("<Button-1>", self.start_drag)
        self.bind("<ButtonRelease-1>", self.end_drag)
        self.bind("<B1-Motion>", self.drag_window)

    def start_drag(self, event):
        self.dx, self.dy = event.x, event.y
        self.dragging = True
        self.config(cursor="none")

    def end_drag(self, _):
        utils.set_active_window(self.other_window_id)
        self.dragging = False
        self.config(cursor="hand2")

    def drag_window(self, event):
        # disable if doing non draggable actions
        if self.action == "Drag Window" and self.drag_window_stage >= 2:
            return

        # move location
        new_x, new_y = event.x_root-self.dx, event.y_root-self.dy

        # move geometry
        self.geometry(f"+{new_x}+{new_y}")

    def add_menu(self):
        FONT = "Corbel"
        if PLATFORM == "WINDOWS":
            FONT_SIZE = 8
        if PLATFORM == "MAC":
            FONT_SIZE = 12

        def menu_popup(event):
            try:
                self.menu.tk_popup(event.x_root, event.y_root)
            finally:
                self.menu.grab_release()
                utils.set_active_window(self.other_window_id)

        self.menu = tk.Menu(self, tearoff=0)
        self.menu.add_command(
            label="play!",
            font=(FONT, FONT_SIZE),
            command=lambda: self._change_state("Play")
        )
        self.menu.add_command(
            label="sleep",
            font=(FONT, FONT_SIZE),
            command=lambda: self._change_state("Sleep")
        )
        self.menu.add_separator()
        self.menu.add_command(
            label="bye bye",
            font=(FONT, FONT_SIZE),
            command=lambda: self._change_state("Quit")
        )

        if PLATFORM == "WINDOWS":
            self.bind("<Button-3>", menu_popup)
        if PLATFORM == "MAC":
            self.bind("<Button-2>", menu_popup)

    def _change_state(self, new_state):
        self.state = new_state


if __name__ == "__main__":
    app = MainApp()
    while True:
        try:
            app.main_loop()
            FPS = 100
            sleep(1 / FPS)
        except KeyboardInterrupt:
            print("byebye.")
            break
