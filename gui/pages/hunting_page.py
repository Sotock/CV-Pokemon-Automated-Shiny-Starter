import tkinter as tk
from tkinter import ttk, messagebox

from profiles.profile_manager import (
    SAVES_DIR,
    load_profile
)

from gui.hunting_dashboard import HuntingDashboard


MAX_INSTANCES = 10


class HuntingPage(ttk.Frame):

    def __init__(self, parent, application):

        super().__init__(parent)

        self.application = application

        self.available_profiles = {}
        self.hunting_queue = {}

        self.dashboard = None

        self.profile_var = tk.StringVar()
        self.instance_count_var = tk.StringVar(value="1")
        self.profile_info_var = tk.StringVar()
        self.total_var = tk.StringVar()
        self.status_var = tk.StringVar()

        self.create_widgets()
        self.refresh_profiles()
        self.update_queue()

        self.profile_var.trace_add(
            "write", self.update_profile_info
        )

    def create_widgets(self):

        ttk.Label(
            self,
            text="Automated Hunting",
            font=("Segoe UI", 24, "bold")
        ).pack(anchor="w")

        ttk.Label(
            self,
            text=(
                "Configure and monitor concurrent "
                "shiny hunting instances."
            ),
            font=("Segoe UI", 11)
        ).pack(
            anchor="w",
            pady=(5, 20)
        )

        ttk.Separator(
            self,
            orient="horizontal"
        ).pack(
            fill="x",
            pady=(0, 20)
        )

        self.create_configuration_form()
        self.create_queue_table()
        self.create_session_controls()

    def create_configuration_form(self):

        section = ttk.LabelFrame(
            self,
            text="Hunting Configuration",
            padding=15
        )

        section.pack(
            fill="x",
            pady=(0, 15)
        )

        section.columnconfigure(1, weight=1)

        ttk.Label(
            section,
            text="Hunting Profile:"
        ).grid(
            row=0,
            column=0,
            sticky="w",
            padx=(0, 15),
            pady=8
        )

        self.profile_dropdown = ttk.Combobox(
            section,
            textvariable=self.profile_var,
            state="readonly",
            postcommand=self.refresh_profiles
        )

        self.profile_dropdown.grid(
            row=0,
            column=1,
            sticky="ew",
            pady=8
        )

        ttk.Button(
            section,
            text="Refresh",
            command=self.refresh_profiles
        ).grid(
            row=0,
            column=2,
            padx=(10, 0)
        )

        ttk.Label(
            section,
            textvariable=self.profile_info_var,
            justify="left"
        ).grid(
            row=1,
            column=1,
            sticky="w",
            pady=(0, 10)
        )

        ttk.Label(
            section,
            text="Number of Instances:"
        ).grid(
            row=2,
            column=0,
            sticky="w",
            padx=(0, 15),
            pady=8
        )

        self.instance_spinbox = ttk.Spinbox(
            section,
            from_=1,
            to=MAX_INSTANCES,
            textvariable=self.instance_count_var,
            width=8,
            state="readonly"
        )

        self.instance_spinbox.grid(
            row=2,
            column=1,
            sticky="w",
            pady=8
        )

        ttk.Button(
            section,
            text="Add to Hunting Queue",
            command=self.add_configuration
        ).grid(
            row=3,
            column=1,
            sticky="e",
            pady=(10, 0)
        )

    def create_queue_table(self):

        section = ttk.LabelFrame(
            self,
            text="Hunting Queue",
            padding=15
        )

        section.pack(
            fill="both",
            expand=True,
            pady=(0, 15)
        )

        section.columnconfigure(0, weight=1)
        section.rowconfigure(0, weight=1)

        columns = (
            "profile",
            "game",
            "starter",
            "instances"
        )

        self.queue_table = ttk.Treeview(
            section,
            columns=columns,
            show="headings",
            selectmode="browse",
            height=5
        )

        headings = {
            "profile": "Profile Name",
            "game": "Game",
            "starter": "Target",
            "instances": "Instances"
        }

        for column in columns:

            self.queue_table.heading(
                column,
                text=headings[column]
            )

        self.queue_table.column(
            "profile",
            width=200,
            minwidth=120
        )

        self.queue_table.column(
            "game",
            width=180,
            minwidth=120
        )

        self.queue_table.column(
            "starter",
            width=100,
            minwidth=70
        )

        self.queue_table.column(
            "instances",
            width=80,
            minwidth=60,
            anchor="center",
            stretch=False
        )

        self.queue_table.grid(
            row=0,
            column=0,
            sticky="nsew"
        )

        scrollbar = ttk.Scrollbar(
            section,
            orient="vertical",
            command=self.queue_table.yview
        )

        scrollbar.grid(
            row=0,
            column=1,
            sticky="ns"
        )

        self.queue_table.configure(
            yscrollcommand=scrollbar.set
        )

        buttons = ttk.Frame(section)

        buttons.grid(
            row=1,
            column=0,
            sticky="ew",
            pady=(10, 0)
        )

        ttk.Button(
            buttons,
            text="Remove Selected",
            command=self.remove_configuration
        ).pack(side="left")

        ttk.Button(
            buttons,
            text="Clear Queue",
            command=self.clear_queue
        ).pack(
            side="left",
            padx=8
        )

    def create_session_controls(self):

        section = ttk.LabelFrame(
            self,
            text="Session Summary",
            padding=15
        )

        section.pack(fill="x")

        ttk.Label(
            section,
            textvariable=self.total_var,
            font=("Segoe UI", 12, "bold")
        ).pack(anchor="w")

        ttk.Label(
            section,
            textvariable=self.status_var
        ).pack(
            anchor="w",
            pady=(8, 10)
        )

        self.start_button = ttk.Button(
            section,
            text="Start Hunting",
            command=self.start_hunting,
            state="disabled"
        )

        self.start_button.pack(anchor="e")

    def refresh_profiles(self):

        self.available_profiles.clear()

        if SAVES_DIR.is_dir():

            for directory in sorted(SAVES_DIR.iterdir()):

                if not directory.is_dir():
                    continue

                try:

                    profile = load_profile(
                        directory.name
                    )

                except (
                        OSError,
                        ValueError,
                        KeyError
                ) as error:

                    print(
                        f"Invalid profile "
                        f"{directory.name}: {error}"
                    )

                    continue

                self.available_profiles[
                    profile["name"]
                ] = profile

        self.profile_dropdown.configure(
            values=list(self.available_profiles)
        )

        if (
                self.profile_var.get()
                not in self.available_profiles
        ):

            self.profile_var.set("")

        self.update_profile_info()

    def update_profile_info(self, *args):

        profile_name = self.profile_var.get()

        profile = self.available_profiles.get(
            profile_name
        )

        if profile is None:

            self.profile_info_var.set(
                "Select an existing hunting profile."
            )

            return

        self.profile_info_var.set(
            f"Game: {profile['game']}\n"
            f"Trainer: {profile['trainer_name']}\n"
            f"Target: {profile['target_name']}\n"
            f"Emulator: {profile['emulator']}"
        )

    def add_configuration(self):

        self.refresh_profiles()

        profile_name = self.profile_var.get()

        if profile_name not in self.available_profiles:

            messagebox.showwarning(
                "Profile Required",
                "Select a valid hunting profile.",
                parent=self
            )

            return

        try:

            count = int(
                self.instance_count_var.get()
            )

        except ValueError:

            messagebox.showerror(
                "Invalid Instance Count",
                "Enter a valid instance count.",
                parent=self
            )

            return

        if not 1 <= count <= MAX_INSTANCES:

            messagebox.showerror(
                "Invalid Instance Count",
                (
                    f"Select between 1 and "
                    f"{MAX_INSTANCES} instances."
                ),
                parent=self
            )

            return

        current_total = sum(
            item["count"]
            for item in self.hunting_queue.values()
        )

        if current_total + count > MAX_INSTANCES:

            messagebox.showwarning(
                "Instance Limit",
                (
                    f"A hunting session supports a maximum "
                    f"of {MAX_INSTANCES} configured instances."
                ),
                parent=self
            )

            return

        if profile_name in self.hunting_queue:

            self.hunting_queue[
                profile_name
            ]["count"] += count

        else:

            self.hunting_queue[profile_name] = {
                "profile": self.available_profiles[
                    profile_name
                ].copy(),
                "count": count
            }

        self.update_queue()

    def remove_configuration(self):

        selected = self.queue_table.selection()

        if not selected:

            messagebox.showwarning(
                "Selection Required",
                "Select a queued profile to remove.",
                parent=self
            )

            return

        profile_name = selected[0]

        self.hunting_queue.pop(
            profile_name,
            None
        )

        self.update_queue()

    def clear_queue(self):

        self.hunting_queue.clear()

        self.update_queue()

    def update_queue(self):

        for item in self.queue_table.get_children():

            self.queue_table.delete(item)

        total = 0

        for name, configuration in (
                self.hunting_queue.items()
        ):

            profile = configuration["profile"]
            count = configuration["count"]

            total += count

            self.queue_table.insert(
                "",
                "end",
                iid=name,
                values=(
                    name,
                    profile["game"],
                    profile["target_name"],
                    count
                )
            )

        self.total_var.set(
            f"Total Instances: {total} / {MAX_INSTANCES}"
        )

        if total == 0:

            self.status_var.set(
                "Add a profile to configure a hunting session."
            )

            self.start_button.configure(
                state="disabled"
            )

        else:

            self.status_var.set(
                "Hunting configuration is ready."
            )

            self.start_button.configure(
                state="normal"
            )

    def validate_configuration(self):

        if not self.hunting_queue:

            raise ValueError(
                "The hunting queue is empty."
            )

        total = 0

        for name, configuration in (
                self.hunting_queue.items()
        ):

            count = configuration["count"]

            if not isinstance(count, int) or count < 1:

                raise ValueError(
                    f"Invalid instance count for {name}."
                )

            configuration["profile"] = load_profile(
                name
            )

            total += count

        if total > MAX_INSTANCES:

            raise ValueError(
                "Maximum instance count exceeded."
            )

        return total

    def start_hunting(self):

        if (
                self.dashboard is not None
                and self.dashboard.winfo_exists()
        ):

            self.dashboard.lift()

            return

        try:

            self.validate_configuration()

            configurations = {
                name: {
                    "profile": configuration["profile"].copy(),
                    "count": configuration["count"]
                }
                for name, configuration
                in self.hunting_queue.items()
            }

            self.dashboard = HuntingDashboard(
                self,
                configurations
            )

        except Exception as error:

            messagebox.showerror(
                "Hunting Initialization Failed",
                str(error),
                parent=self
            )