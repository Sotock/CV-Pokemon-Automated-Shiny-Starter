import tkinter as tk
from tkinter import ttk, messagebox

from profiles.game_registry import (
    get_supported_games,
    get_supported_starters,
    get_game_config
)

from profiles.profile_manager import (
    PROJECT_DIR,
    SAVES_DIR,
    generate_profile_name,
    generate_unique_profile_name,
    load_profile
)

from gui.preparation_window import PreparationWindow


class ProfilesPage(ttk.Frame):

    def __init__(self, parent, application):

        super().__init__(parent)

        self.application = application

        self.game_var = tk.StringVar()
        self.starter_var = tk.StringVar()
        self.trainer_var = tk.StringVar()
        self.profile_name_var = tk.StringVar()
        self.status_var = tk.StringVar()

        self.create_widgets()
        self.refresh_profiles()

        self.game_var.trace_add(
            "write", self.update_starters
        )

        self.starter_var.trace_add(
            "write", self.update_profile_name
        )

        self.trainer_var.trace_add(
            "write", self.update_profile_name
        )

        self.update_profile_name()

    def create_widgets(self):

        ttk.Label(
            self,
            text="Hunting Profiles",
            font=("Segoe UI", 24, "bold")
        ).pack(
            anchor="w"
        )

        ttk.Label(
            self,
            text=(
                "Create and manage permanent "
                "game and starter profiles."
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

        self.create_profile_list()
        self.create_profile_form()

    def create_profile_list(self):

        section = ttk.LabelFrame(
            self,
            text="Existing Profiles",
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
            "name",
            "game",
            "trainer",
            "starter"
        )

        self.profile_table = ttk.Treeview(
            section,
            columns=columns,
            show="headings",
            selectmode="browse",
            height=5
        )

        headings = {
            "name": "Profile Name",
            "game": "Game",
            "trainer": "Trainer",
            "starter": "Starter"
        }

        for column in columns:

            self.profile_table.heading(
                column,
                text=headings[column]
            )

        self.profile_table.column(
            "name", width=180, minwidth=120
        )

        self.profile_table.column(
            "game", width=180, minwidth=120
        )

        self.profile_table.column(
            "trainer", width=90, minwidth=70
        )

        self.profile_table.column(
            "starter", width=90, minwidth=70
        )

        self.profile_table.grid(
            row=0,
            column=0,
            sticky="nsew"
        )

        scrollbar = ttk.Scrollbar(
            section,
            orient="vertical",
            command=self.profile_table.yview
        )

        scrollbar.grid(
            row=0,
            column=1,
            sticky="ns"
        )

        self.profile_table.configure(
            yscrollcommand=scrollbar.set
        )

        ttk.Button(
            section,
            text="Refresh Profiles",
            command=self.refresh_profiles
        ).grid(
            row=1,
            column=0,
            sticky="w",
            pady=(10, 0)
        )

    def create_profile_form(self):

        section = ttk.LabelFrame(
            self,
            text="Create New Profile",
            padding=15
        )

        section.pack(
            fill="x"
        )

        section.columnconfigure(
            1,
            weight=1
        )

        ttk.Label(
            section,
            text="Game:"
        ).grid(
            row=0,
            column=0,
            sticky="w",
            padx=(0, 15),
            pady=8
        )

        self.game_dropdown = ttk.Combobox(
            section,
            textvariable=self.game_var,
            values=list(get_supported_games()),
            state="readonly"
        )

        self.game_dropdown.grid(
            row=0,
            column=1,
            sticky="ew",
            pady=8
        )

        ttk.Label(
            section,
            text="Starter Pokemon:"
        ).grid(
            row=1,
            column=0,
            sticky="w",
            padx=(0, 15),
            pady=8
        )

        self.starter_dropdown = ttk.Combobox(
            section,
            textvariable=self.starter_var,
            state="disabled"
        )

        self.starter_dropdown.grid(
            row=1,
            column=1,
            sticky="ew",
            pady=8
        )

        ttk.Label(
            section,
            text="Trainer Name:"
        ).grid(
            row=2,
            column=0,
            sticky="w",
            padx=(0, 15),
            pady=8
        )

        ttk.Entry(
            section,
            textvariable=self.trainer_var
        ).grid(
            row=2,
            column=1,
            sticky="ew",
            pady=8
        )

        ttk.Label(
            section,
            text="Profile Name:"
        ).grid(
            row=3,
            column=0,
            sticky="w",
            padx=(0, 15),
            pady=8
        )

        ttk.Entry(
            section,
            textvariable=self.profile_name_var,
            state="readonly"
        ).grid(
            row=3,
            column=1,
            sticky="ew",
            pady=8
        )

        ttk.Label(
            section,
            textvariable=self.status_var
        ).grid(
            row=4,
            column=0,
            columnspan=2,
            sticky="w",
            pady=8
        )

        self.prepare_button = ttk.Button(
            section,
            text="Begin Game Preparation",
            command=self.begin_preparation,
            state="disabled"
        )

        self.prepare_button.grid(
            row=5,
            column=1,
            sticky="e",
            pady=(10, 0)
        )

    def refresh_profiles(self):

        for item in self.profile_table.get_children():

            self.profile_table.delete(item)

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

                self.profile_table.insert(
                    "",
                    "end",
                    values=(
                        profile["name"],
                        profile["game"],
                        profile["trainer_name"],
                        profile["target_name"]
                    )
                )

        self.update_profile_name()

    def update_starters(self, *args):

        game = self.game_var.get()

        self.starter_var.set("")

        if not game:

            self.starter_dropdown.configure(
                values=[],
                state="disabled"
            )

        else:

            starters = get_supported_starters(
                game
            )

            self.starter_dropdown.configure(
                values=list(starters),
                state="readonly"
            )

        self.update_profile_name()

    def update_profile_name(self, *args):

        game = self.game_var.get()
        starter = self.starter_var.get()
        trainer = self.trainer_var.get().strip()

        self.profile_name_var.set("")

        self.prepare_button.configure(
            state="disabled"
        )

        if not game or not starter or not trainer:

            self.status_var.set(
                "Complete all fields to prepare a profile."
            )

            return

        try:

            base_name = generate_profile_name(
                game,
                starter,
                trainer
            )

            profile_name = generate_unique_profile_name(
                game,
                starter,
                trainer
            )

        except ValueError as error:

            self.status_var.set(str(error))

            return

        self.profile_name_var.set(profile_name)

        config = get_game_config(game)

        rom_path = PROJECT_DIR / config["rom_path"]

        if not rom_path.is_file():

            self.status_var.set(
                "The required game ROM is missing."
            )

            return

        if profile_name != base_name:

            self.status_var.set(
                "Existing profile detected. "
                "A unique profile name was generated."
            )

        else:

            self.status_var.set(
                "Profile configuration is ready."
            )

        self.prepare_button.configure(
            state="normal"
        )

    def begin_preparation(self):

        self.update_profile_name()

        if self.prepare_button.instate(["disabled"]):

            return

        try:

            PreparationWindow(
                parent=self,
                game=self.game_var.get(),
                starter=self.starter_var.get(),
                trainer_name=self.trainer_var.get().strip(),
                on_finalized=self.profile_finalized
            )

        except Exception as error:

            messagebox.showerror(
                "Game Preparation Failed",
                str(error),
                parent=self
            )

    def profile_finalized(self, profile_name):

        self.refresh_profiles()

        for item in self.profile_table.get_children():

            values = self.profile_table.item(
                item,
                "values"
            )

            if values[0] == profile_name:

                self.profile_table.selection_set(item)

                self.profile_table.focus(item)

                self.profile_table.see(item)

                break

        messagebox.showinfo(
            "Profile Created",
            (
                "Hunting profile successfully created:\n\n"
                f"{profile_name}"
            ),
            parent=self
        )