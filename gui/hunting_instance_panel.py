import tkinter as tk
from tkinter import ttk

from PIL import Image, ImageTk


class HuntingInstancePanel(ttk.LabelFrame):

    def __init__(
            self,
            parent,
            profile_name,
            target,
            on_stop=None,
            on_takeover=None,
            on_export=None
    ):

        super().__init__(
            parent,
            text=profile_name,
            padding=10
        )

        self.profile_name = profile_name
        self.target = target

        self.on_stop = on_stop
        self.on_takeover = on_takeover
        self.on_export = on_export

        self.photo = None

        self.instance_id_var = tk.StringVar(
            value="Pending"
        )

        self.status_var = tk.StringVar(
            value="Ready"
        )

        self.statistics = {
            "completed_rotations": tk.StringVar(value="0"),
            "valid_encounters": tk.StringVar(value="0"),
            "failed_rotations": tk.StringVar(value="0"),
            "encounters_per_minute": tk.StringVar(value="0.00"),
            "success_rate": tk.StringVar(value="0.00%"),
            "shinies_found": tk.StringVar(value="0")
        }

        self.classifier_vars = {
            "border": tk.StringVar(value="Pending"),
            "star": tk.StringVar(value="Pending"),
            "palette": tk.StringVar(value="Pending")
        }

        self.create_widgets()

        self.update_status("Ready")

    def create_widgets(self):

        self.create_header()
        self.create_framebuffer()
        self.create_statistics()
        self.create_classifiers()
        self.create_controls()

    def create_header(self):

        header = ttk.Frame(self)

        header.pack(
            fill="x",
            pady=(0, 8)
        )

        ttk.Label(
            header,
            text=f"Target: {self.target}",
            font=("Segoe UI", 10, "bold")
        ).pack(
            side="left"
        )

        ttk.Label(
            header,
            textvariable=self.status_var
        ).pack(
            side="right"
        )

        ttk.Label(
            self,
            textvariable=self.instance_id_var
        ).pack(
            anchor="w",
            pady=(0, 8)
        )

    def create_framebuffer(self):

        self.display = ttk.Label(
            self,
            anchor="center"
        )

        self.display.pack(
            fill="x",
            pady=(0, 10)
        )

        blank_frame = Image.new(
            "RGB",
            (240, 160),
            "black"
        )

        self.update_framebuffer(blank_frame)

    def create_statistics(self):

        section = ttk.Frame(self)

        section.pack(
            fill="x",
            pady=(0, 10)
        )

        labels = (
            ("Rotations", "completed_rotations"),
            ("Encounters", "valid_encounters"),
            ("Failures", "failed_rotations"),
            ("Encounters/min", "encounters_per_minute"),
            ("Success Rate", "success_rate"),
            ("Shinies", "shinies_found")
        )

        for index, (label, key) in enumerate(labels):

            row = index // 3
            column = index % 3

            section.columnconfigure(
                column,
                weight=1
            )

            cell = ttk.Frame(
                section,
                padding=4
            )

            cell.grid(
                row=row,
                column=column,
                sticky="nsew"
            )

            ttk.Label(
                cell,
                text=label
            ).pack()

            ttk.Label(
                cell,
                textvariable=self.statistics[key],
                font=("Segoe UI", 12, "bold")
            ).pack()

    def create_classifiers(self):

        section = ttk.LabelFrame(
            self,
            text="Classification",
            padding=5
        )

        section.pack(
            fill="x",
            pady=(0, 10)
        )

        classifiers = (
            ("Border", "border"),
            ("Star", "star"),
            ("Palette", "palette")
        )

        for column, (label, key) in enumerate(classifiers):

            section.columnconfigure(
                column,
                weight=1
            )

            cell = ttk.Frame(
                section,
                padding=3
            )

            cell.grid(
                row=0,
                column=column,
                sticky="ew"
            )

            ttk.Label(
                cell,
                text=label
            ).pack()

            ttk.Label(
                cell,
                textvariable=self.classifier_vars[key]
            ).pack()

    def create_controls(self):

        section = ttk.Frame(self)

        section.pack(
            fill="x"
        )

        self.stop_button = ttk.Button(
            section,
            text="Stop",
            command=self.stop_hunting
        )

        self.stop_button.pack(
            fill="x",
            pady=2
        )

        self.takeover_button = ttk.Button(
            section,
            text="Manual Takeover",
            command=self.manual_takeover
        )

        self.takeover_button.pack(
            fill="x",
            pady=2
        )

        self.export_button = ttk.Button(
            section,
            text="Export Save",
            command=self.export_save
        )

        self.export_button.pack(
            fill="x",
            pady=2
        )

    def update_instance_id(self, instance_id):

        self.instance_id_var.set(
            f"Instance: {instance_id}"
        )

    def update_status(self, status):

        self.status_var.set(status)

        self.stop_button.configure(
            state=(
                "normal"
                if status in (
                    "Initializing",
                    "Hunting"
                ) and self.on_stop is not None
                else "disabled"
            )
        )

        self.takeover_button.configure(
            state=(
                "normal"
                if status == "Shiny Found"
                   and self.on_takeover is not None
                else "disabled"
            )
        )

        self.export_button.configure(
            state=(
                "normal"
                if status == "Ready to Export"
                   and self.on_export is not None
                else "disabled"
            )
        )

    def update_framebuffer(self, frame):

        frame = frame.convert("RGB")

        self.photo = ImageTk.PhotoImage(
            frame,
            master=self
        )

        self.display.configure(
            image=self.photo
        )

    def update_statistics(self, statistics):

        for key, variable in self.statistics.items():

            if key not in statistics:
                continue

            value = statistics[key]

            if key == "encounters_per_minute":

                variable.set(f"{value:.2f}")

            elif key == "success_rate":

                variable.set(f"{value:.2f}%")

            else:

                variable.set(str(value))

    def update_classification(self, result):

        for key, variable in self.classifier_vars.items():

            if result is None:

                variable.set("Pending")

                continue

            if not result.get("valid_summary", False):

                variable.set("Invalid")

                continue

            prediction = result.get(key)

            if prediction is None:

                variable.set("Pending")

            elif prediction:

                variable.set("Shiny")

            else:

                variable.set("Normal")

    def stop_hunting(self):

        if self.on_stop is not None:

            self.on_stop()

    def manual_takeover(self):

        if self.on_takeover is not None:

            self.on_takeover()

    def export_save(self):

        if self.on_export is not None:

            self.on_export()