import tkinter as tk
from tkinter import ttk

from PIL import Image, ImageTk

from gui.theme import Colors
from gui.grass_background import create_ball_watermark


class HuntingInstancePanel(tk.Canvas):

    PANEL_WIDTH = 320
    PANEL_HEIGHT = 490

    SHINY_STATUSES = (
        "Shiny Found",
        "Manual Takeover",
        "Ready to Export",
        "Exporting",
        "Export Retry",
        "Save Exported"
    )

    def __init__(
            self,
            parent,
            profile_name,
            target,
            on_stop=None,
            on_takeover=None,
            on_export=None,
            vision_config="firered_leafgreen"
    ):

        super().__init__(
            parent,
            width=self.PANEL_WIDTH,
            height=self.PANEL_HEIGHT,
            background=Colors.PANEL,
            highlightbackground=Colors.BORDER,
            highlightcolor=Colors.BORDER,
            highlightthickness=2,
            borderwidth=0
        )

        self.profile_name = profile_name
        self.target = target
        self.vision_config = vision_config

        self.on_stop = on_stop
        self.on_takeover = on_takeover
        self.on_export = on_export

        self.photo = None
        self.background_photo = None
        self.background_state = None
        self.shiny_found = False

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

        if self.vision_config == "ruby_sapphire":

            self.classifiers = (
                ("Battle", "valid_battle"),
                ("Sprite", "valid_sprite"),
                ("Palette", "palette")
            )

        else:

            self.classifiers = (
                ("Border", "border"),
                ("Star", "star"),
                ("Palette", "palette")
            )

        self.classifier_vars = {
            key: tk.StringVar(value="Pending")
            for _, key in self.classifiers
        }

        self.create_widgets()

        self.update_status("Ready")

    def create_widgets(self):

        self.background_item = self.create_image(
            0,
            0,
            anchor="nw"
        )

        self.create_header()
        self.create_framebuffer()
        self.create_statistics()
        self.create_classifiers()
        self.create_controls()

    def create_bound_text(
            self,
            x,
            y,
            variable,
            font=("Segoe UI", 10),
            fill=Colors.TEXT,
            anchor="center"
    ):

        item = self.create_text(
            x,
            y,
            text=variable.get(),
            font=font,
            fill=fill,
            anchor=anchor
        )

        def update_text(*args):

            self.itemconfigure(
                item,
                text=variable.get()
            )

        variable.trace_add(
            "write",
            update_text
        )

        return item

    def create_header(self):

        self.create_text(
            12,
            14,
            text=self.profile_name,
            font=("Segoe UI", 10, "bold"),
            fill=Colors.SECONDARY_TEXT,
            anchor="nw"
        )

        self.create_text(
            12,
            39,
            text=self.target,
            font=("Segoe UI", 14, "bold"),
            fill=Colors.TEXT,
            anchor="w"
        )

        self.status_item = self.create_bound_text(
            self.PANEL_WIDTH - 12,
            39,
            self.status_var,
            font=("Segoe UI", 10, "bold"),
            anchor="e"
        )

        self.create_bound_text(
            12,
            62,
            self.instance_id_var,
            font=("Segoe UI", 9),
            fill=Colors.SECONDARY_TEXT,
            anchor="w"
        )

    def create_framebuffer(self):

        center = self.PANEL_WIDTH // 2

        self.create_rectangle(
            center - 121,
            77,
            center + 121,
            239,
            outline=Colors.BORDER,
            fill=Colors.BLACK
        )

        self.display = self.create_image(
            center,
            78,
            anchor="n"
        )

        blank_frame = Image.new(
            "RGB",
            (240, 160),
            "black"
        )

        self.update_framebuffer(blank_frame)

    def create_statistics(self):

        labels = (
            ("Rotations", "completed_rotations"),
            ("Encounters", "valid_encounters"),
            ("Failures", "failed_rotations"),
            ("Encounters/min", "encounters_per_minute"),
            ("Success Rate", "success_rate"),
            ("Shinies", "shinies_found")
        )

        column_width = self.PANEL_WIDTH / 3

        for index, (label, key) in enumerate(labels):

            row = index // 3
            column = index % 3

            x = column_width * (column + 0.5)
            y = 254 + row * 46

            self.create_text(
                x,
                y,
                text=label,
                font=("Segoe UI", 9),
                fill=Colors.SECONDARY_TEXT
            )

            self.create_bound_text(
                x,
                y + 20,
                self.statistics[key],
                font=("Segoe UI", 13, "bold"),
                fill=(
                    Colors.SHINY
                    if key == "shinies_found"
                    else Colors.TEXT
                )
            )

    def create_classifiers(self):

        self.create_line(
            12,
            338,
            self.PANEL_WIDTH - 12,
            338,
            fill=Colors.BORDER
        )

        self.create_text(
            12,
            351,
            text="Classification",
            font=("Segoe UI", 10, "bold"),
            fill=Colors.TEXT,
            anchor="w"
        )

        self.classifier_items = {}

        column_width = self.PANEL_WIDTH / 3

        for column, (label, key) in enumerate(
                self.classifiers
        ):

            x = column_width * (column + 0.5)

            self.create_text(
                x,
                372,
                text=label,
                font=("Segoe UI", 9),
                fill=Colors.SECONDARY_TEXT
            )

            self.classifier_items[key] = (
                self.create_bound_text(
                    x,
                    390,
                    self.classifier_vars[key],
                    font=("Segoe UI", 10, "bold")
                )
            )

    def create_controls(self):

        self.stop_button = ttk.Button(
            self,
            text="Stop",
            command=self.stop_hunting
        )

        self.takeover_button = ttk.Button(
            self,
            text="Manual Takeover",
            command=self.manual_takeover
        )

        self.export_button = ttk.Button(
            self,
            text="Export Save",
            command=self.export_save
        )

        for index, button in enumerate(
                (
                        self.stop_button,
                        self.takeover_button,
                        self.export_button
                )
        ):

            self.create_window(
                12,
                405 + index * 27,
                window=button,
                anchor="nw",
                width=self.PANEL_WIDTH - 24,
                height=24
            )

    def update_background(self, status):

        muted = status in (
            "Stopped",
            "Completed",
            "Error"
        )

        state = (
            self.shiny_found,
            muted
        )

        if state == self.background_state:

            return

        texture = create_ball_watermark(
            self.PANEL_WIDTH,
            self.PANEL_HEIGHT,
            ultra=self.shiny_found,
            muted=muted,
            background=Colors.PANEL
        )

        self.background_photo = ImageTk.PhotoImage(
            texture,
            master=self
        )

        self.itemconfigure(
            self.background_item,
            image=self.background_photo
        )

        self.tag_lower(
            self.background_item
        )

        border_color = (
            Colors.SHINY
            if self.shiny_found
            else Colors.BORDER
        )

        self.configure(
            highlightbackground=border_color,
            highlightcolor=border_color
        )

        self.background_state = state

    def update_instance_id(self, instance_id):

        self.instance_id_var.set(
            f"Instance: {instance_id}"
        )

    def update_status(self, status):

        self.status_var.set(status)

        if status in self.SHINY_STATUSES:

            self.shiny_found = True

        if self.shiny_found:

            status_color = Colors.SHINY

        elif status == "Hunting":

            status_color = Colors.SUCCESS

        elif status == "Stopping":

            status_color = Colors.WARNING

        elif status == "Error":

            status_color = Colors.ERROR

        else:

            status_color = Colors.SECONDARY_TEXT

        self.itemconfigure(
            self.status_item,
            fill=status_color
        )

        self.update_background(status)

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
                if status in (
                    "Shiny Found",
                    "Ready to Export"
                ) and self.on_takeover is not None
                else "disabled"
            )
        )

        self.export_button.configure(
            state=(
                "normal"
                if status in (
                    "Ready to Export",
                    "Export Retry"
                ) and self.on_export is not None
                else "disabled"
            )
        )

    def update_framebuffer(self, frame):

        frame = frame.convert("RGB")

        self.photo = ImageTk.PhotoImage(
            frame,
            master=self
        )

        self.itemconfigure(
            self.display,
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

            if key == "valid_battle":

                variable.set(
                    "Valid"
                    if result.get("valid_battle")
                    else "Invalid"
                )

                continue

            if key == "valid_sprite":

                if not result.get("valid_battle"):

                    variable.set("Not Checked")

                else:

                    variable.set(
                        "Valid"
                        if result.get("valid_sprite")
                        else "Invalid"
                    )

                continue

            if not result.get(
                    "valid_encounter",
                    result.get("valid_summary", False)
            ):

                variable.set("Invalid")

                continue

            prediction = result.get(key)

            if prediction is None:

                variable.set("Pending")

            elif prediction:

                variable.set("Shiny")

            else:

                variable.set("Normal")

        self.update_classifier_colors()

    def update_classifier_colors(self):

        colors = {
            "Valid": Colors.SUCCESS,
            "Normal": Colors.TEXT,
            "Shiny": Colors.SHINY,
            "Invalid": Colors.ERROR,
            "Pending": Colors.SECONDARY_TEXT,
            "Not Checked": Colors.SECONDARY_TEXT
        }

        for key, variable in self.classifier_vars.items():

            self.itemconfigure(
                self.classifier_items[key],
                fill=colors.get(
                    variable.get(),
                    Colors.TEXT
                )
            )

    def stop_hunting(self):

        if self.on_stop is not None:

            self.on_stop()

    def manual_takeover(self):

        if self.on_takeover is not None:

            self.on_takeover()

    def export_save(self):

        if self.on_export is not None:

            self.on_export()