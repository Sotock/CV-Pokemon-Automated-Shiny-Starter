import tkinter as tk
from tkinter import ttk, messagebox

from instances.manual_session import ManualSession
from gui.emulator_view import EmulatorView


class PreparationWindow(tk.Toplevel):

    def __init__(
            self,
            parent,
            game,
            starter,
            trainer_name,
            on_finalized
    ):

        super().__init__(parent)

        self.withdraw()

        self.parent = parent
        self.on_finalized = on_finalized

        self.session = None
        self.view = None

        self.title("Game Preparation")
        self.resizable(False, False)

        self.transient(parent.winfo_toplevel())

        self.protocol(
            "WM_DELETE_WINDOW",
            self.cancel_preparation
        )

        try:

            self.session = ManualSession(
                game,
                starter,
                trainer_name
            )

            self.create_widgets()

            self.deiconify()
            self.grab_set()

            self.view.start()

        except Exception:

            if self.view is not None:
                self.view.stop()

            if self.session is not None:
                self.session.close()

            self.destroy()

            raise

    def create_widgets(self):

        content = ttk.Frame(
            self,
            padding=15
        )

        content.pack(
            fill="both",
            expand=True
        )

        ttk.Label(
            content,
            text="Prepare Hunting Profile",
            font=("Segoe UI", 20, "bold")
        ).pack(
            anchor="w"
        )

        ttk.Label(
            content,
            text=self.session.profile_name,
            font=("Segoe UI", 12, "bold")
        ).pack(
            anchor="w",
            pady=(5, 10)
        )

        ttk.Label(
            content,
            text=(
                f"Game: {self.session.game}\n"
                f"Trainer: {self.session.trainer_name}\n"
                f"Target: {self.session.starter}"
            )
        ).pack(
            anchor="w",
            pady=(0, 10)
        )

        ttk.Label(
            content,
            text=(
                "Play through the introduction, stand in front "
                "of the selected starter,\nand save in-game "
                "before accepting the Pokemon."
            ),
            justify="left"
        ).pack(
            anchor="w",
            pady=(0, 10)
        )

        self.view = EmulatorView(
            content,
            self.session,
            scale=2
        )

        self.view.pack(
            pady=(0, 10)
        )

        controls = ttk.LabelFrame(
            content,
            text="Keyboard Controls",
            padding=10
        )

        controls.pack(
            fill="x",
            pady=(0, 10)
        )

        ttk.Label(
            controls,
            text=(
                "Z: A     X: B     Enter: Start     "
                "Backspace: Select\n"
                "Arrow Keys: Movement     A: L     S: R"
            ),
            justify="left"
        ).pack(
            anchor="w"
        )

        self.status_var = tk.StringVar(
            value="Game preparation in progress."
        )

        ttk.Label(
            content,
            textvariable=self.status_var,
            wraplength=500
        ).pack(
            anchor="w",
            pady=(0, 10)
        )

        buttons = ttk.Frame(content)

        buttons.pack(
            fill="x"
        )

        self.cancel_button = ttk.Button(
            buttons,
            text="Cancel",
            command=self.cancel_preparation
        )

        self.cancel_button.pack(
            side="left"
        )

        self.finalize_button = ttk.Button(
            buttons,
            text="Finalize Profile",
            command=self.finalize_profile
        )

        self.finalize_button.pack(
            side="right"
        )

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

        self.finalize_button.configure(
            state="disabled"
        )

        self.status_var.set(
            "Finalizing hunting profile..."
        )

        try:

            metadata_path = self.session.finalize()

        except Exception as error:

            self.status_var.set(
                "Profile finalization failed."
            )

            messagebox.showerror(
                "Profile Finalization Failed",
                str(error),
                parent=self
            )

            self.finalize_button.configure(
                state="normal"
            )

            # Resume gameplay if validation failed
            # before the emulator was released.

            if self.session.core is not None:

                self.view.start()

                self.status_var.set(
                    "Game preparation in progress."
                )

            else:

                self.status_var.set(
                    "Emulator closed. The temporary save "
                    "is retained. Finalization can be retried."
                )

            return

        profile_name = metadata_path.parent.name

        self.session.close()

        self.grab_release()

        self.destroy()

        self.on_finalized(profile_name)

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

        self.session.close()

        self.grab_release()

        self.destroy()