from sys import platform
from ctypes import Structure, c_long, byref

if platform == "darwin":
    # mac will need to download pyautogui library
    # python3 -m pip install pyautogui
    from pyautogui import position
    PLATFORM = "MAC"
if platform in ["win32", "win64"]:
    from ctypes import windll
    PLATFORM = "WINDOWS"


class POINT(Structure):
    _fields_ = [("x", c_long), ("y", c_long)]


def move_mouse(pos):
    if PLATFORM == "WINDOWS":
        windll.user32.SetCursorPos(pos["x"], pos["y"])


def move_mouse_to_target(target, speed):
    pos = mouse_position()
    delta = (
        target[0] - pos["x"],
        target[1] - pos["y"]
    )
    vector = [
        sorted([-1 * speed, d, speed])[1]
        for d in delta
    ]
    # move by vector
    windll.user32.SetCursorPos(
        int(pos["x"] + vector[0]), int(pos["y"] + vector[1])
    )

    new_pos = mouse_position()
    at_x, at_y = False, False

    if abs(target[0] - pos["x"]) < speed:
        windll.user32.SetCursorPos(int(target[0]), int(new_pos["y"]))
        at_x = True

    if abs(target[1] - pos["y"]) < speed:
        windll.user32.SetCursorPos(int(new_pos["x"]), int(target[1]))
        at_y = True

    if at_x and at_y:
        return True
    else:
        return False


def mouse_position():
    if PLATFORM == "WINDOWS":
        pt = POINT()
        windll.user32.GetCursorPos(byref(pt))
        return {"x": pt.x, "y": pt.y}
    if PLATFORM == "MAC":
        pos = position()
        return {"x": pos[0], "y": pos[1]}


def get_active_window():
    if PLATFORM == "WINDOWS":
        active_window = windll.user32.GetForegroundWindow()
        return active_window


def set_active_window(window_id):
    if PLATFORM == "WINDOWS":
        windll.user32.SetForegroundWindow(window_id)
