import tkinter as tk
from PIL import Image, ImageTk
from time import perf_counter

from instances.library_manager import LibraryInstance

from pathlib import Path


PROFILE_NAME = "FireRed TEST Bulbasaur"
SCALE = 3
TARGET_FPS = 59.7275
FRAME_INTERVAL = 1.0 / TARGET_FPS

KEY_MAPPING = {
    "z": 0,           # A
    "x": 1,           # B
    "BackSpace": 2,   # Select
    "Return": 3,      # Start
    "Right": 4,
    "Left": 5,
    "Up": 6,
    "Down": 7,
    "s": 8,           # R
    "a": 9            # L
}

instance = LibraryInstance(PROFILE_NAME)

instance.core.reset()

root = tk.Tk()
root.title("libmGBA Live Framebuffer Test")
root.resizable(False, False)

display = tk.Label(root, borderwidth=0)
display.pack()

running = True
frame_count = 0

start_time = perf_counter()
next_frame_time = start_time


def update_frame():
    global frame_count, next_frame_time

    if not running:
        return

    instance.core.run_frame()

    frame = instance.screen.to_pil().convert("RGB")

    frame = frame.resize(
        (240 * SCALE, 160 * SCALE),
        Image.Resampling.NEAREST
    )

    photo = ImageTk.PhotoImage(frame)

    display.configure(image=photo)
    display.image = photo

    frame_count += 1

    next_frame_time += FRAME_INTERVAL

    delay = max(
        0,
        int((next_frame_time - perf_counter()) * 1000)
    )

    root.after(delay, update_frame)

def key_pressed(event):
    key = KEY_MAPPING.get(event.keysym)

    if key is not None:
        instance.core.add_keys(key)


def key_released(event):
    key = KEY_MAPPING.get(event.keysym)

    if key is not None:
        instance.core.clear_keys(key)


def release_all_keys(event):
    for key in KEY_MAPPING.values():
        instance.core.clear_keys(key)

def close_window():
    global running

    running = False

    root.destroy()

root.bind("<KeyPress>", key_pressed)
root.bind("<KeyRelease>", key_released)
root.bind("<FocusOut>", release_all_keys)
root.focus_set()

def capture_screenshot(event):
    path = (
            Path(__file__).resolve().parents[2]
            / "docs" / "figures" / "macro"
            / "selection_failure.png"
    )

    instance.screen.to_pil().convert("RGB").save(path)
    print(f"Screenshot saved: {path}")


root.bind("<F12>", capture_screenshot)

root.protocol("WM_DELETE_WINDOW", close_window)

try:
    update_frame()
    root.mainloop()

finally:
    elapsed = perf_counter() - start_time

    instance.close()

    print(f"Total frames rendered: {frame_count}")
    print(f"Elapsed time: {elapsed:.2f} seconds")
    print(f"Average FPS: {frame_count / elapsed:.2f}")
    print("Live framebuffer test completed.")