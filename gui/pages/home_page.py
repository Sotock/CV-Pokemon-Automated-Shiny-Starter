from tkinter import ttk


class HomePage(ttk.Frame):

    def __init__(self, parent, application):

        super().__init__(parent)

        self.application = application

        self.create_widgets()

    def create_widgets(self):

        ttk.Label(
            self,
            text="Pokemon Shiny Hunter",
            font=("Segoe UI", 24, "bold")
        ).pack(
            anchor="w"
        )

        ttk.Label(
            self,
            text=(
                "Automated shiny hunting using "
                "computer vision and integrated emulation."
            ),
            font=("Segoe UI", 11)
        ).pack(
            anchor="w",
            pady=(5, 25)
        )

        ttk.Separator(
            self,
            orient="horizontal"
        ).pack(
            fill="x",
            pady=(0, 20)
        )

        profiles_section = ttk.LabelFrame(
            self,
            text="Hunting Profiles",
            padding=20
        )

        profiles_section.pack(
            fill="x",
            pady=(0, 15)
        )

        ttk.Label(
            profiles_section,
            text=(
                "Create and manage permanent "
                "hunting profiles."
            )
        ).pack(
            anchor="w",
            pady=(0, 10)
        )

        ttk.Button(
            profiles_section,
            text="Manage Profiles",
            command=lambda: (
                self.application.show_page("Profiles")
            )
        ).pack(
            anchor="w"
        )

        hunting_section = ttk.LabelFrame(
            self,
            text="Automated Hunting",
            padding=20
        )

        hunting_section.pack(
            fill="x",
            pady=(0, 15)
        )

        ttk.Label(
            hunting_section,
            text=(
                "Configure and monitor independent "
                "shiny hunting instances."
            )
        ).pack(
            anchor="w",
            pady=(0, 10)
        )

        ttk.Button(
            hunting_section,
            text="Configure Hunting",
            command=lambda: (
                self.application.show_page("Hunting")
            )
        ).pack(
            anchor="w"
        )