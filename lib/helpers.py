from os import path
from tkinter import PhotoImage
from sys import platform

# this contains helper functions to reduce duplicated code from main.py

if platform == "darwin":
    PLATFORM = "MAC"
if platform in ["win32", "win64"]:
    PLATFORM = "WINDOWS"


def init_sprite_frames(name):
    divisor = (
        "\\" if PLATFORM == "WINDOWS"
        else "/" if PLATFORM == "MAC"
        else ""
    )
    folder = path.dirname(path.realpath(__file__)).split(f"{divisor}lib")[0]
    lis = [s.strip() for s in name.split("|")]

    if len(lis) == 2:
        name, frame_count = lis
    else:
        print(f"Uh oh, naming for the gif: {name} is wrong!")
        raise Exception

    frames = [
        PhotoImage(
            file=f"{folder}{divisor}animations"
            f"{divisor}{name} | {frame_count}.gif",
            format=f"gif -index {i}"
        )
        for i in range(int(frame_count))
    ]

    return int(frame_count), 0, frames


def go_to_next_sprite_frame(obj, f):
    f["current"] += 1
    # reset current frame if at end of animation
    if f["current"] == f["count"]:
        f["current"] = 0
    # change sprite
    obj.sprite_label.configure(
        image=f["frames"][f["current"]]
    )


def get_sub_directory(name):
    divisor = (
        "\\" if PLATFORM == "WINDOWS"
        else "/" if PLATFORM == "MAC"
        else ""
    )
    # get base dir
    folder = path.dirname(path.realpath(__file__)).split(f"{divisor}lib")[0]
    folder = folder + divisor + name + divisor
    return folder


def walk_to_target(obj, target, t_range):
    # find vector to get there
    move = 1 if target - obj.winfo_x() > 0 else -1
    obj.movement_direction = "Left" if move < 0 else "Right"
    # use movement_speed
    move = move * obj.movement_speed
    # walk to that location
    if obj.sprite_frame == 1:
        obj.place_at(obj, obj.winfo_x()+move, obj.winfo_y())

    # check if at target
    if abs(target - obj.winfo_x()) < t_range:
        obj.place_at(
            obj,
            int(target),
            obj.winfo_y()
        )
        return True
    else:
        return False


def fly_to_target(obj, target, t_range):
    dist_to_target = (
        abs(target[0] - obj.winfo_x()),
        abs(target[1] - obj.winfo_y())
    )

    if dist_to_target[0] == 0 and dist_to_target[1] == 0:
        return True

    # find vector to get there
    divisor = min(dist_to_target)
    one_dir = False
    if divisor < t_range:
        divisor = max(dist_to_target)
        one_dir = True

    vector_to_target = (
        int((target[0] - obj.winfo_x()) / divisor),
        int((target[1] - obj.winfo_y()) / divisor)
    )

    # enforce speed limit, + apply movement speed
    vector_to_target = [
        sorted([-2, v, 2])[1]
        for v in vector_to_target
    ]
    if one_dir:
        vector_to_target = [
            v * 2 * obj.movement_speed for v in vector_to_target
        ]
    else:
        vector_to_target = [
            v * obj.movement_speed for v in vector_to_target
        ]

    obj.movement_direction = (
        "Left" if vector_to_target[0] < 0 else "Right"
    )

    # fly to location
    if obj.sprite_frame == 1:
        obj.place_at(
            obj,
            obj.winfo_x()+vector_to_target[0],
            obj.winfo_y()+vector_to_target[1]
        )

    # check if at target
    if all([d < t_range for d in dist_to_target]):
        obj.place_at(
            obj,
            int(target[0]),
            int(target[1])
        )
        return True
    else:
        return False
