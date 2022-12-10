import tkinter as tk
import os

# select a color as the transparent color
TRANSPARENT_COLOR = "#abcdef"


def create_root():
    global root
    root = tk.Tk()

    # disable closing window
    root.overrideredirect(1)

    # allow to be moved
    root.bind("<Button-1>", start_drag)
    root.bind("<B1-Motion>", drag_window)

    # keep window on front (windows manager)
    root.wm_attributes("-topmost", 1)
    folder = f"{os.path.dirname(os.path.realpath(__file__))}\\"
    image = tk.PhotoImage(file=f"{folder}cat.png")

    # transparent bg
    root.attributes("-transparentcolor", TRANSPARENT_COLOR)
    tk.Label(root, image=image, bg=TRANSPARENT_COLOR).pack()


def main_loop():
    while True:
        try:
            root.lift()
            root.update()
        except KeyboardInterrupt:
            print("Bye bye.")
            break


def start_drag(event):
    global dx, dy
    dx, dy = event.x, event.y


def drag_window(event):
    root.geometry(f"+{event.x_root-dx}+{event.y_root-dy}")


if __name__ == "__main__":
    # define global root
    create_root()
    main_loop()
