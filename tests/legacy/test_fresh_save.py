from pathlib import Path
from time import perf_counter
import tkinter as tk
import shutil
import gc

from PIL import Image, ImageTk

import mgba.core
import mgba.image
import mgba.vfs
import mgba.log


PROJECT_DIR = Path(__file__).resolve().parents[2]

SOURCE_ROM = (
        PROJECT_DIR / "roms"
        / "Pokemon - FireRed Version (USA, Europe) (Rev 1).gba"
)

TEST_DIR = PROJECT_DIR / "temp" / "fresh_save_test"

SCALE = 3
TARGET_FPS = 59.7275
FRAME_INTERVAL = 1.0 / TARGET_FPS

KEY_MAPPING = {
    "z": 0,
    "x": 1,
    "BackSpace": 2,
    "Return": 3,
    "Right": 4,
    "Left": 5,
    "Up": 6,
    "Down": 7,
    "s": 8,
    "a": 9
}


class EmulatorLogger(mgba.log.Logger):

    def log(self, category, level, message):
        if level in (self.FATAL, self.ERROR, self.WARN):
            super().log(category, level, message)


mgba.log.install_default(EmulatorLogger())


# Prepare isolated test directory

TEST_DIR.mkdir(parents=True, exist_ok=True)

ROM_PATH = TEST_DIR / SOURCE_ROM.name
SAVE_PATH = ROM_PATH.with_suffix(".sav")

shutil.copy2(SOURCE_ROM, ROM_PATH)

print("Existing save:", SAVE_PATH.exists())


# Initialize emulator

core = mgba.core.load_path(str(ROM_PATH))

if core is None:
    raise RuntimeError("Unable to load ROM.")

if not SAVE_PATH.exists():
    SAVE_PATH.write_bytes(b"\xff" * 131072)
    print("Blank battery save created.")

save = mgba.vfs.open_path(str(SAVE_PATH), "r+")

if save is None:
    raise RuntimeError("Unable to open battery save.")

if not core.load_save(save):
    save.close()
    raise RuntimeError("Unable to attach battery save.")

print("Battery save successfully attached.")
print("Save size:", SAVE_PATH.stat().st_size)

screen = mgba.image.Image(
    *core.desired_video_dimensions()
)

core.set_video_buffer(screen)
core.reset()

print("Emulator initialized.")


# Initialize display

root = tk.Tk()
root.title("libmGBA Fresh Save Test")
root.resizable(False, False)

display = tk.Label(root, borderwidth=0)
display.pack()

running = True
frame_count = 0

start_time = perf_counter()
next_frame_time = start_time


# Framebuffer rendering and frame pacing

def update_frame():
    global frame_count, next_frame_time

    if not running:
        return

    core.run_frame()

    frame = screen.to_pil().convert("RGB")

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


# Keyboard controls

def key_pressed(event):
    key = KEY_MAPPING.get(event.keysym)

    if key is not None:
        core.add_keys(key)


def key_released(event):
    key = KEY_MAPPING.get(event.keysym)

    if key is not None:
        core.clear_keys(key)


def release_all_keys(event):
    for key in KEY_MAPPING.values():
        core.clear_keys(key)


# Window closure

def close_window():
    global running

    running = False

    root.destroy()


root.bind("<KeyPress>", key_pressed)
root.bind("<KeyRelease>", key_released)
root.bind("<FocusOut>", release_all_keys)

root.focus_set()

root.protocol("WM_DELETE_WINDOW", close_window)


# Execute emulator

try:
    update_frame()
    root.mainloop()

finally:
    elapsed = perf_counter() - start_time

    core = None
    gc.collect()
    screen = None

    print()
    print("Emulator closed.")
    print(f"Total frames rendered: {frame_count}")
    print(f"Elapsed time: {elapsed:.2f} seconds")

    if elapsed > 0:
        print(f"Average FPS: {frame_count / elapsed:.2f}")

    print()
    print("--- Save Verification ---")
    print("Save exists:", SAVE_PATH.is_file())

    if SAVE_PATH.is_file():
        print("Save size:", SAVE_PATH.stat().st_size)
        print("Save location:", SAVE_PATH)

    print()
    print("Fresh save test completed.")