import tkinter as tk

from tkinter import ttk, messagebox

from gui.emulator_view import EmulatorView
from instances.manual_takeover import ManualTakeover


class ManualTakeoverWindow(tk.Toplevel):

    def __init__(
            self,
            parent,
            controller,
            on_finished
    ):

        super().__init__(parent)

        self.withdraw()

        self.parent = parent
        self.controller = controller
        self.on_finished = on_finished

        self.takeover = None
        self.view = None
        self.finishing = False

        self.title("Manual Takeover")
        self.resizable(False, False)
        self.transient(parent)

        self.protocol(
            "WM_DELETE_WINDOW",
            self.finish_takeover
        )

        try:

            self.takeover = ManualTakeover(
                controller
            )

            self.create_widgets()

            self.deiconify()
            self.grab_set()

            self.view.start()

        except Exception:

            if self.view is not None:

                self.view.stop()

            if self.takeover is not None:

                self.takeover.close()

            self.destroy()

            parent.grab_set()

            raise

    def create_widgets(self):

        instance = self.controller.instance

        container = ttk.Frame(
            self,
            padding=15
        )

        container.pack(
            fill="both",
            expand=True
        )

        ttk.Label(
            container,
            text=f"Shiny {instance.target_name}",
            font=("Segoe UI", 18, "bold")
        ).pack(
            anchor="w"
        )

        ttk.Label(
            container,
            text=f"Profile: {instance.profile_name}"
        ).pack(
            anchor="w"
        )

        ttk.Label(
            container,
            text=f"Instance: {instance.instance_id}"
        ).pack(
            anchor="w",
            pady=(0, 10)
        )

        ttk.Label(
            container,
            text=(
                "You now have manual control of the preserved "
                "emulator.\nSave your progress in-game before "
                "finishing manual takeover."
            ),
            justify="left",
            wraplength=720
        ).pack(
            anchor="w",
            pady=(0, 10)
        )

        self.view = EmulatorView(
            container,
            self.takeover,
            scale=3
        )

        self.view.pack()

        controls = ttk.LabelFrame(
            container,
            text="Keyboard Controls",
            padding=10
        )

        controls.pack(
            fill="x",
            pady=10
        )

        ttk.Label(
            controls,
            text=(
                "Z: A    X: B    Enter: Start    "
                "Backspace: Select\n"
                "Arrow Keys: Movement    "
                "A: L    S: R"
            ),
            justify="center"
        ).pack()

        self.finish_button = ttk.Button(
            container,
            text="Finish Manual Takeover",
            command=self.finish_takeover
        )

        self.finish_button.pack(
            fill="x",
            pady=(5, 0)
        )

    def finish_takeover(self):

        if self.finishing:

            return

        self.view.stop()

        confirmed = messagebox.askyesno(
            "Finish Manual Takeover",
            (
                "Have you saved your progress in-game?\n\n"
                "Finishing manual takeover does not "
                "automatically save your game."
            ),
            parent=self
        )

        if not confirmed:

            self.view.start()

            return

        self.finishing = True

        self.finish_button.configure(
            state="disabled"
        )

        final_frame = self.takeover.get_frame()

        self.takeover.close()

        self.grab_release()

        self.destroy()

        self.parent.grab_set()

        self.on_finished(
            self.takeover,
            final_frame
        )