import tkinter as tk
from tkinter import ttk, messagebox

from instances.manual_session import ManualSession
from gui.widgets.emulator_view import EmulatorView
from gui.settings import (
    get_controls_text,
    get_music_volume,
    save_music_volume,
    audio_enabled
)
from gui.styling.window_style import apply_window_style
from gui.audio.audio_manager import (
    play_preparation_music,
    set_music_volume,
    stop_audio
)


# Provides interactive game preparation before permanent profile creation.
class PreparationWindow(tk.Toplevel):
    # Initializes the preparation session, window, and music preferences.
    def __init__(self, parent, game, starter, trainer_name, on_finalized):
        super().__init__(parent)
        self.withdraw()

        self.parent = parent
        self.on_finalized = on_finalized

        self.session = None
        self.view = None
        self.music_playing = False

        self.music_enabled = audio_enabled("preparation_music")
        self.saved_volume = get_music_volume()
        self.volume_var = tk.DoubleVar(value=self.saved_volume)
        self.volume_text = tk.StringVar(value=f"{self.saved_volume}%")

        self.title("Game Preparation")
        self.resizable(False, False)
        self.transient(parent.winfo_toplevel())
        self.protocol("WM_DELETE_WINDOW", self.cancel_preparation)

        try:
            self.session = ManualSession(game, starter, trainer_name)
            self.create_widgets()
            self.deiconify()
            apply_window_style(self)
            self.grab_set()
            self.view.start()

            self.music_playing = play_preparation_music(self.session.game)

            if not self.music_playing:
                self.volume_slider.configure(state="disabled")

        except Exception:
            self.stop_music()

            if self.view is not None:
                self.view.stop()

            if self.session is not None:
                self.session.close()

            self.destroy()
            raise

    # Creates profile information, gameplay display, and preparation controls.
    def create_widgets(self):
        content = ttk.Frame(self, padding=15)
        content.pack(fill="both", expand=True)

        ttk.Label(
            content,
            text="Prepare Hunting Profile",
            font=("Segoe UI", 20, "bold"),
            anchor="center"
        ).pack(fill="x", pady=(0, 8))

        ttk.Label(
            content,
            text=self.session.profile_name,
            font=("Segoe UI", 12, "bold"),
            anchor="center"
        ).pack(fill="x", pady=(0, 8))

        ttk.Label(
            content,
            text=(
                f"Game: {self.session.game}\n"
                f"Trainer: {self.session.trainer_name}\n"
                f"Target: {self.session.starter}"
            ),
            style="Secondary.TLabel",
            justify="center",
            anchor="center"
        ).pack(fill="x", pady=(0, 12))

        ttk.Separator(
            content,
            orient="horizontal"
        ).pack(fill="x", pady=(0, 12))

        ttk.Label(
            content,
            text=(
                "Play through the introduction, stand in front "
                "of the selected starter, and save in-game "
                "before accepting the Pokemon."
            ),
            justify="center",
            anchor="center",
            wraplength=480
        ).pack(fill="x", pady=(0, 12))

        self.view = EmulatorView(content, self.session, scale=2)
        self.view.pack(anchor="center", pady=(0, 10))

        self.create_volume_controls(content)

        controls = ttk.LabelFrame(
            content,
            text="Keyboard Controls",
            labelanchor="n",
            padding=10
        )
        controls.pack(fill="x", pady=(0, 10))

        ttk.Label(
            controls,
            text=get_controls_text(),
            justify="center",
            anchor="center",
            wraplength=460
        ).pack(fill="x")

        self.status_var = tk.StringVar(
            value="Game preparation in progress."
        )

        ttk.Label(
            content,
            textvariable=self.status_var,
            style="Secondary.TLabel",
            justify="center",
            anchor="center",
            wraplength=480
        ).pack(fill="x", pady=(0, 10))

        buttons = ttk.Frame(content)
        buttons.pack(anchor="center")

        self.cancel_button = ttk.Button(
            buttons,
            text="Cancel",
            width=18,
            command=self.cancel_preparation
        )
        self.cancel_button.pack(side="left", padx=6)

        self.finalize_button = ttk.Button(
            buttons,
            text="Finalize Profile",
            width=18,
            style="Accent.TButton",
            command=self.finalize_profile
        )
        self.finalize_button.pack(side="left", padx=6)

    # Creates the preparation music volume slider and percentage display.
    def create_volume_controls(self, parent):
        container = ttk.Frame(parent)
        container.pack(anchor="center", pady=(0, 12))

        ttk.Label(
            container,
            text="Music Volume",
            style="Secondary.TLabel"
        ).pack(side="left", padx=(0, 10))

        self.volume_slider = ttk.Scale(
            container,
            from_=0,
            to=100,
            orient="horizontal",
            length=220,
            variable=self.volume_var,
            command=self.update_music_volume,
            takefocus=False
        )
        self.volume_slider.pack(side="left")

        ttk.Label(
            container,
            textvariable=self.volume_text,
            width=5,
            anchor="center"
        ).pack(side="left", padx=(8, 0))

        self.volume_slider.bind(
            "<ButtonRelease-1>",
            self.finish_volume_adjustment
        )

        if not self.music_enabled:
            self.volume_slider.configure(state="disabled")

    # Applies volume changes immediately during slider adjustment.
    def update_music_volume(self, value):
        volume = round(float(value))
        self.volume_text.set(f"{volume}%")
        set_music_volume(volume)

    # Persists the music volume when it differs from the saved value.
    def persist_music_volume(self):
        volume = round(self.volume_var.get())

        if volume == self.saved_volume:
            return

        try:
            save_music_volume(volume)
            self.saved_volume = volume
        except (OSError, ValueError) as error:
            print(f"Unable to save music volume: {error}")

    # Saves the adjusted volume and returns keyboard focus to gameplay.
    def finish_volume_adjustment(self, event=None):
        self.persist_music_volume()
        self.view.display.focus_set()

    # Stops preparation music when playback is active.
    def stop_music(self):
        if self.music_playing:
            stop_audio()
            self.music_playing = False

    # Validates and finalizes the prepared save as a permanent profile.
    def finalize_profile(self):
        confirmed = messagebox.askyesno(
            "Finalize Hunting Profile",
            (
                f"Are you positioned in front of "
                f"{self.session.starter}?\n\n"
                "Have you saved in-game without "
                "accepting the starter?"
            ),
            parent=self
        )

        if not confirmed:
            self.view.display.focus_set()
            return

        self.view.stop()
        self.finalize_button.configure(state="disabled")
        self.status_var.set("Finalizing hunting profile...")

        try:
            metadata_path = self.session.finalize()
        except Exception as error:
            self.status_var.set("Profile finalization failed.")

            messagebox.showerror(
                "Profile Finalization Failed",
                str(error),
                parent=self
            )

            self.finalize_button.configure(state="normal")

            # Resume gameplay if validation failed before emulator release.
            if self.session.core is not None:
                self.view.start()
                self.status_var.set("Game preparation in progress.")
            else:
                self.persist_music_volume()
                self.stop_music()
                self.volume_slider.configure(state="disabled")

                self.status_var.set(
                    "Emulator closed. The temporary save "
                    "is retained. Finalization can be retried."
                )

            return

        profile_name = metadata_path.parent.name

        self.persist_music_volume()
        self.stop_music()
        self.session.close()

        self.grab_release()
        self.destroy()
        self.on_finalized(profile_name)

    # Cancels preparation and discards temporary game progress.
    def cancel_preparation(self):
        confirmed = messagebox.askyesno(
            "Cancel Game Preparation",
            (
                "Cancel profile preparation?\n\n"
                "Temporary game progress will be discarded."
            ),
            parent=self
        )

        if not confirmed:
            if self.session.core is not None:
                self.view.display.focus_set()
            return

        self.view.stop()
        self.persist_music_volume()
        self.stop_music()
        self.session.close()

        self.grab_release()
        self.destroy()