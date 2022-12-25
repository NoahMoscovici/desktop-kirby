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
