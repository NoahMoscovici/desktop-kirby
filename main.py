import tkinter as tk
import os

from input_lib import mouse_position, get_active_window, set_active_window
from time import time
from tkinter import Menu, PhotoImage
from random import randint, choice, seed


class MainApp(tk.Tk):
    def __init__(self):
        self.menu: Menu
        self.dx: int
        self.dy: int

        self.my_window_id: int
        self.other_window_id = get_active_window()

        self.last_frame_time = time()
        self.time_between_frames = 0.05

        self.state = "Play"

        # play action instance variables
        self.action = "Idle"
        self.action_start_time = time()
        self.walk_direction = ""
        self.walk_frame = 0
        self.walk_speed = 400  # low is actually fast here

        # init
        super().__init__()

        self.config_window()
        self.bind_actions()
        self.add_menu()

        folder = os.path.dirname(os.path.realpath(__file__))

        # add idle frames
        self.idle_frame_count = 40
        self.current_idle_frame = 0
        self.idle_frames = [
            PhotoImage(file=f"{folder}\\idle.gif",
                       format=f"gif -index {i}")
            for i in range(self.idle_frame_count)
        ]

        # add walk left frames
        self.walk_left_frame_count = 20
        self.current_walk_left_frame = 0
        self.walk_left_frames = [
            PhotoImage(file=f"{folder}\\walk left.gif",
                       format=f"gif -index {i}")
            for i in range(self.walk_left_frame_count)
        ]

        # add walk right frames
        self.walk_right_frame_count = 20
        self.current_walk_right_frame = 0
        self.walk_right_frames = [
            PhotoImage(file=f"{folder}\\walk right.gif",
                       format=f"gif -index {i}")
            for i in range(self.walk_right_frame_count)
        ]

        # define sprite label
        self.sprite_label = tk.Label(
            self, image=self.idle_frames[0], bg="black")
        self.sprite_label.pack()

    def main_loop(self):
        # this is ran every frame (~10,000 times a second)
        self.lift()
        self.update()

        # store active windows to switch to if needed
        a_win = get_active_window()
        if a_win not in (self.other_window_id, self.my_window_id):
            self.other_window_id = a_win

        # update sprite frame
        if time() - self.last_frame_time > self.time_between_frames:
            self.next_sprite_frame()
            self.last_frame_time = time()

        # update frame count
        if self.walk_frame == self.walk_speed:
            self.walk_frame = 0
        self.walk_frame += 1

        if self.state == "Play":
            self.play_state()
        elif self.state == "Sleep":
            self.sleep_state()
        elif self.state == "Quit":
            raise KeyboardInterrupt

    def play_state(self):
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
                # "Drag Window",
                # "Fly",
                "Walk",
            ])
            print(f"Doing action: {self.action}")
            # reset start time
            self.action_start_time = time()

        elif self.action == "Idle":
            limit = randint(2, 10)
            # do nothing for 2-10 seconds
            if time() - self.action_start_time > limit:
                self.action = ""

        elif self.action == "Eat Cursor":
            pos = mouse_position()
            print(pos["x"], pos["y"])

        elif self.action == "Drag Window":
            pass

        elif self.action == "Fly":
            pass

        elif self.action == "Walk":
            # choose random x coordinate on screen to walk to
            target = randint(100, self.winfo_screenwidth() - 100)
            # check if at target
            if abs(target - self.winfo_x()) < 5:
                self.action = ""
                self.walk_direction = ""
            # find vector to get there
            move = 1 if target - self.winfo_x() > 0 else -1
            self.walk_direction = "Left" if move < 0 else "Right"

            # walk to that location
            if self.walk_frame == 1:
                self.place_at(self.winfo_x()+move, self.winfo_y())

    def sleep_state(self):
        pass

    def next_sprite_frame(self):
        def idle_frame():
            self.current_idle_frame += 1
            # reset current frame if at end of animation
            if self.current_idle_frame == self.idle_frame_count:
                self.current_idle_frame = 0
            # change sprite
            self.sprite_label.configure(
                image=self.idle_frames[self.current_idle_frame])

        def walk_left_frame():
            self.current_walk_left_frame += 1
            # reset current frame if at end of animation
            if self.current_walk_left_frame == self.walk_left_frame_count:
                self.current_walk_left_frame = 0
            # change sprite
            self.sprite_label.configure(
                image=self.walk_left_frames[self.current_walk_left_frame])

        def walk_right_frame():
            self.current_walk_right_frame += 1
            # reset current frame if at end of animation
            if self.current_walk_right_frame == self.walk_right_frame_count:
                self.current_walk_right_frame = 0
            # change sprite
            self.sprite_label.configure(
                image=self.walk_right_frames[self.current_walk_right_frame])

        if self.action == "Idle":
            idle_frame()
        elif self.action == "Walk":
            # check direction
            if self.walk_direction == "Left":
                walk_left_frame()
            elif self.walk_direction == "Right":
                walk_right_frame()

    def config_window(self):
        # disable closing
        self.overrideredirect(1)
        # keep on top of other windows
        self.wm_attributes("-topmost", 1)
        # replace white with transparent
        self.wm_attributes("-transparentcolor", "black")
        # place window starting at bottom right of screen
        self.place_at(self.winfo_screenwidth() - 100,
                      self.winfo_screenheight() - 105)
        # set my window id
        self.lift()
        self.my_window_id = get_active_window()

    def place_at(self, x, y):
        self.geometry(f"+{x}+{y}")

    def bind_actions(self):
        # allow to be moved
        self.bind("<Button-1>", self.start_drag)
        self.bind("<ButtonRelease-1>", self.end_drag)
        self.bind("<B1-Motion>", self.drag_window)

    def start_drag(self, event):
        self.dx, self.dy = event.x, event.y

    def end_drag(self, _):
        set_active_window(self.other_window_id)

    def drag_window(self, event):
        self.geometry(f"+{event.x_root-self.dx}+{event.y_root-self.dy}")

    def add_menu(self):
        def menu_popup(event):
            try:
                self.menu.tk_popup(event.x_root, event.y_root)
            finally:
                self.menu.grab_release()
                set_active_window(self.other_window_id)

        self.menu = Menu(self, tearoff=0)
        self.menu.add_command(
            label="go to sleep",
            font=("Corbel", 8),
            command=lambda: self._change_state("Sleep")
        )
        self.menu.add_command(
            label="play!",
            font=("Corbel", 8),
            command=lambda: self._change_state("Play")
        )
        self.menu.add_separator()
        self.menu.add_command(
            label="bye bye",
            font=("Corbel", 8),
            command=lambda: self._change_state("Quit")
        )

        def set_action(x):
            self.action = x
        self.menu.add_separator()
        self.menu.add_command(
            label="dev: walk",
            command=lambda: set_action("Walk")
        )
        self.menu.add_command(
            label="dev: fly",
            command=lambda: set_action("Fly")
        )
        self.menu.add_command(
            label="dev: idle",
            command=lambda: set_action("Idle")
        )
        self.menu.add_command(
            label="dev: eat cursor",
            command=lambda: set_action("Eat Cursor")
        )
        self.menu.add_command(
            label="dev: drag window",
            command=lambda: set_action("Drag Window")
        )

        self.bind("<Button-3>", menu_popup)

    def _change_state(self, new_state):
        self.state = new_state


if __name__ == "__main__":
    app = MainApp()
    while True:
        try:
            app.main_loop()
        except KeyboardInterrupt:
            print("byebye.")
            break
