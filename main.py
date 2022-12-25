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

        self.drag_window_stage: int

        self.my_window_id: int
        self.other_window_id = utils.get_active_window()
        self.second_window = None

        self.state = "Play"
        self.sleeping = False

        # play action instance variables
        self.action = "Idle"
        self.action_start_time = time()

        # for speeds, low = fast
        self.movement_direction = ""
        self.movement_speed = 10

        self.falling = False

        if PLATFORM == "WINDOWS":
            self.ground_level = 105
        if PLATFORM == "MAC":
            self.ground_level = 70

        if PLATFORM == "MAC":
            self.movement_speed = int(self.movement_speed / 4)

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
            self.frames[name.split("|")[0].strip()] = {
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
            self.second_window.lift(self)
        self.lift()
        self.update()
        if self.second_window:
            self.second_window.update()

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
            self.next_sprite_frame()

        # update frame count
        self.update_motion_frames()

        # check if should be falling
        if (
            self.winfo_y() < self.winfo_screenheight() - self.ground_level
            and (
                self.state == "Play"
                and self.action not in ["Fly", "Eat Cursor", "Drag Window"]
            )
        ):
            self.falling = True

        if not self.falling:
            if self.state == "Play":
                self.play_state()
            elif self.state == "Sleep":
                self.sleep_state()
        else:
            self.fall()

    def update_motion_frames(self):
        if self.sprite_frame == self.movement_speed:
            self.sprite_frame = 0
        self.sprite_frame += 1

    def play_state(self):
        # reset sleep state if necesarry
        if self.sleeping:
            self.sleep_sleeping = False

        # set seed so action continuity is retained
        seed(str(self.action_start_time))

        # check if an action is being performed
        if self.action == "":
            # reset start time
            self.action_start_time = time()
            # choose new action
            self.action = choice([
                "Idle",
                # "Eat Cursor",
                "Drag Window",
                "Fly",
                "Walk",
            ])
            print(f"Doing action: {self.action}")
            # reset start time
            self.action_start_time = time()
            # reset animation frame counter
            self.sprite_frame = 0

        elif self.action == "Idle":
            limit = randint(2, 10)
            # do nothing for 2-10 seconds
            if time() - self.action_start_time > limit:
                self.action = ""

        elif self.action == "Eat Cursor":
            pos = utils.mouse_position()
            print(pos["x"], pos["y"])

        elif self.action == "Drag Window":
            if self.second_window:
                if self.drag_window_stage == 1:
                    # fly to window corner
                    target = (
                        self.second_window.winfo_x() +
                        self.second_window.winfo_width() - self.winfo_width(),
                        self.second_window.winfo_y() - self.winfo_height() / 2
                    )
                    at_target = helpers.fly_to_target(self, target, t_range=10)
                    if at_target:
                        self.drag_window_stage = 2

                elif self.drag_window_stage == 2:
                    # drag window on screen
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

            else:
                def reset_second_window():
                    self.second_window.destroy()
                    self.second_window = None
                    self.action = ""

                # define window
                self.second_window = tk.Toplevel(self)
                self.second_window.title("")
                self.second_window.protocol(
                    "WM_DELETE_WINDOW",
                    reset_second_window
                )
                # TODO: remove visual bug using withdraw
                #self.second_window.wm_withdraw()
                self.second_window.geometry("200x200")
                self.second_window.update()
                self.place_at(
                    self.second_window,
                    -1 * self.second_window.winfo_width() + 1,
                    randint(100, self.winfo_screenheight() - 100)
                )
                # set resizable
                self.second_window.resizable(False, False)
                # set on top of other windows
                self.second_window.wm_attributes("-topmost", 1)

                # image
                folder = helpers.get_sub_directory("images")
                files = [f for f in listdir(folder)]
                self.second_window.image = tk.PhotoImage(
                    file=folder + choice(files)
                )
                tk.Label(
                    self.second_window,
                    image=self.second_window.image,
                    bg="black"
                ).pack()
                # set focus back
                utils.set_active_window(self.other_window_id)

                # set drag window stage
                self.drag_window_stage = 1

        elif self.action == "Fly":
            # choose random x and y coordinate on screen to fly to
            target = (randint(100, self.winfo_screenwidth() - 100),
                      randint(120, self.winfo_screenheight() - 100))
            at_target = helpers.fly_to_target(self, target, t_range=10)
            # check if at target
            if at_target:
                self.action = ""
                self.movement_direction = ""

        elif self.action == "Walk":
            # choose random x coordinate on screen to walk to
            target = randint(100, self.winfo_screenwidth() - 100)
            at_target = helpers.walk_to_target(self, target, t_range=5)
            # check if at target
            if at_target:
                self.action = ""
                self.movement_direction = ""

    def sleep_state(self):
        if not self.sleeping:
            # choose random x coordinate on screen to walk to
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
            return

        self.place_at(
            self,
            self.winfo_x(),
            self.winfo_y() + self.movement_speed
        )

    def next_sprite_frame(self):
        if self.falling:
            helpers.go_to_next_sprite_frame(self, self.frames["falling"])
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
                if self.movement_direction != "":
                    helpers.go_to_next_sprite_frame(
                        self,
                        self.frames[f"fly {self.movement_direction.lower()}"]
                    )
            elif self.action == "Walk":
                if self.movement_direction != "":
                    helpers.go_to_next_sprite_frame(
                        self,
                        self.frames[f"walk {self.movement_direction.lower()}"]
                    )
            elif self.action == "Drag Window":
                # TODO: create drag window animations
                pass
            elif self.action == "Eat Cursor":
                # TODO: create eat cursor animations
                pass

    def config_window(self):
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

    def end_drag(self, _):
        utils.set_active_window(self.other_window_id)

    def drag_window(self, event):
        # disable if doing non draggable actions
        if self.action == "Drag Window" and self.drag_window_stage == 2:
            return
        self.geometry(f"+{event.x_root-self.dx}+{event.y_root-self.dy}")

    def add_menu(self):
        if PLATFORM == "WINDOWS":
            font_size = 8
        if PLATFORM == "MAC":
            font_size = 12

        def menu_popup(event):
            try:
                self.menu.tk_popup(event.x_root, event.y_root)
            finally:
                self.menu.grab_release()
                utils.set_active_window(self.other_window_id)

        self.menu = tk.Menu(self, tearoff=0)
        self.menu.add_command(
            label="go to sleep",
            font=("Corbel", font_size),
            command=lambda: self._change_state("Sleep")
        )
        self.menu.add_command(
            label="play!",
            font=("Corbel", font_size),
            command=lambda: self._change_state("Play")
        )
        self.menu.add_separator()
        self.menu.add_command(
            label="bye bye",
            font=("Corbel", font_size),
            command=lambda: self._change_state("Quit")
        )

        def set_action(x):
            self.action = x
        self.menu.add_separator()
        self.menu.add_command(
            label="dev: walk",
            font=("Corbel", font_size),
            command=lambda: set_action("Walk")
        )
        self.menu.add_command(
            label="dev: fly",
            font=("Corbel", font_size),
            command=lambda: set_action("Fly")
        )
        self.menu.add_command(
            label="dev: idle",
            font=("Corbel", font_size),
            command=lambda: set_action("Idle")
        )
        self.menu.add_command(
            label="dev: eat cursor",
            font=("Corbel", font_size),
            command=lambda: set_action("Eat Cursor")
        )
        self.menu.add_command(
            label="dev: drag window",
            font=("Corbel", font_size),
            command=lambda: set_action("Drag Window")
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
            # ~60 frames a second
            sleep(0.0166667)
        except KeyboardInterrupt:
            print("byebye.")
            break
