import tkinter as tk
from time import perf_counter

from PIL import Image, ImageTk


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


class EmulatorView(tk.Frame):

    def __init__(self, parent, session, scale=3):
        super().__init__(parent)

        self.session = session
        self.scale = scale

        self.running = False
        self.frame_count = 0
        self.start_time = None
        self.next_frame_time = None
        self.after_id = None

        self.display = tk.Label(
            self,
            borderwidth=0,
            takefocus=True
        )

        self.display.pack()

        self.display.bind(
            "<KeyPress>", self.key_pressed
        )

        self.display.bind(
            "<KeyRelease>", self.key_released
        )

        self.display.bind(
            "<FocusOut>", self.release_all_keys
        )

        self.display.bind(
            "<Button-1>",
            lambda event: self.display.focus_set()
        )

    def start(self):
        if self.running:
            return

        self.running = True
        self.frame_count = 0

        self.start_time = perf_counter()
        self.next_frame_time = self.start_time

        self.display.focus_set()

        self.update_frame()

    def update_frame(self):
        self.after_id = None

        if not self.running:
            return

        self.session.run_frame()

        frame = self.session.get_frame()

        width, height = frame.size

        frame = frame.resize(
            (
                width * self.scale,
                height * self.scale
            ),
            Image.Resampling.NEAREST
        )

        photo = ImageTk.PhotoImage(frame)

        self.display.configure(image=photo)
        self.display.image = photo

        self.frame_count += 1

        self.next_frame_time += (
            self.session.frame_interval
        )

        delay = max(
            0,
            int(
                (
                        self.next_frame_time
                        - perf_counter()
                ) * 1000
            )
        )

        self.after_id = self.after(
            delay,
            self.update_frame
        )

    def key_pressed(self, event):
        key = KEY_MAPPING.get(event.keysym)

        if self.running and key is not None:
            self.session.press_key(key)

    def key_released(self, event):
        key = KEY_MAPPING.get(event.keysym)

        if key is not None:
            self.session.release_key(key)

    def release_all_keys(self, event=None):
        self.session.release_all_keys()

    def stop(self):
        self.running = False

        if self.after_id is not None:
            self.after_cancel(self.after_id)
            self.after_id = None

        self.release_all_keys()

    def destroy(self):
        self.stop()
        super().destroy()