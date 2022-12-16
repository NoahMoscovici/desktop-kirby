from ctypes import windll, Structure, c_long, byref

"""
NOTE: I have no idea what most of this code does,
it's yoinked from StackOverflow and solves a lot of
python utility stuff without needing external libraries.
"""


class POINT(Structure):
    _fields_ = [("x", c_long), ("y", c_long)]


def mouse_position():
    pt = POINT()
    windll.user32.GetCursorPos(byref(pt))
    return {"x": pt.x, "y": pt.y}


def get_active_window():
    active_window = windll.user32.GetForegroundWindow()
    return active_window


def set_active_window(window_id):
    windll.user32.SetForegroundWindow(window_id)
