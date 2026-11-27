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
            style="Heading.TLabel"
        ).pack(anchor="w")

        ttk.Label(
            self,
            text=(
                "Automated shiny hunting using "
                "computer vision and integrated emulation."
            ),
            style="Secondary.TLabel"
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

        self.create_overview()
        self.create_navigation_cards()

    def create_overview(self):

        overview = ttk.Frame(
            self,
            style="Panel.TFrame",
            padding=20
        )

        overview.pack(
            fill="x",
            pady=(0, 20)
        )

        statistics = (
            ("3", "Supported Games"),
            ("9", "Supported Starters"),
            ("10", "Concurrent Instances")
        )

        for column, (value, description) in enumerate(
                statistics
        ):

            overview.columnconfigure(
                column,
                weight=1,
                uniform="overview"
            )

            item = ttk.Frame(
                overview,
                style="Panel.TFrame"
            )

            item.grid(
                row=0,
                column=column,
                sticky="ew"
            )

            ttk.Label(
                item,
                text=value,
                style="Panel.TLabel",
                font=("Segoe UI", 28, "bold")
            ).pack()

            ttk.Label(
                item,
                text=description,
                style="Panel.TLabel"
            ).pack(
                pady=(4, 0)
            )

    def create_navigation_cards(self):

        cards = ttk.Frame(self)

        cards.pack(fill="x")

        cards.columnconfigure(
            0,
            weight=1,
            uniform="cards"
        )

        cards.columnconfigure(
            1,
            weight=1,
            uniform="cards"
        )

        self.create_navigation_card(
            cards,
            column=0,
            title="Hunting Profiles",
            description=(
                "Create permanent profiles and prepare "
                "your game before beginning a hunt."
            ),
            button_text="Manage Profiles",
            page_name="Profiles"
        )

        self.create_navigation_card(
            cards,
            column=1,
            title="Automated Hunting",
            description=(
                "Configure concurrent hunting instances "
                "and monitor encounter results."
            ),
            button_text="Configure Hunting",
            page_name="Hunting"
        )

        games_section = ttk.Frame(
            self,
            style="Panel.TFrame",
            padding=20
        )

        games_section.pack(
            fill="x",
            pady=(20, 0)
        )

        ttk.Label(
            games_section,
            text="Supported Games",
            style="Panel.TLabel",
            font=("Segoe UI", 13, "bold")
        ).pack(anchor="w")

        for game, starters in (
                (
                        "Pokemon FireRed",
                        "Bulbasaur, Charmander, Squirtle"
                ),
                (
                        "Pokemon LeafGreen",
                        "Bulbasaur, Charmander, Squirtle"
                ),
                (
                        "Pokemon Sapphire",
                        "Treecko, Torchic, Mudkip"
                )
        ):

            row = ttk.Frame(
                games_section,
                style="Panel.TFrame"
            )

            row.pack(
                fill="x",
                pady=(12, 0)
            )

            ttk.Label(
                row,
                text=game,
                style="Panel.TLabel",
                font=("Segoe UI", 10, "bold")
            ).pack(anchor="w")

            ttk.Label(
                row,
                text=starters,
                style="Panel.TLabel"
            ).pack(
                anchor="w",
                pady=(3, 0)
            )

    def create_navigation_card(
            self,
            parent,
            column,
            title,
            description,
            button_text,
            page_name
    ):

        card = ttk.Frame(
            parent,
            style="Panel.TFrame",
            padding=20
        )

        card.grid(
            row=0,
            column=column,
            sticky="nsew",
            padx=(0, 6) if column == 0 else (6, 0)
        )

        ttk.Label(
            card,
            text=title,
            style="Panel.TLabel",
            font=("Segoe UI", 14, "bold")
        ).pack(anchor="w")

        ttk.Label(
            card,
            text=description,
            style="Panel.TLabel",
            wraplength=230,
            justify="left"
        ).pack(
            anchor="w",
            pady=(10, 20)
        )

        ttk.Button(
            card,
            text=button_text,
            style="Accent.TButton",
            command=lambda: (
                self.application.show_page(page_name)
            )
        ).pack(
            anchor="w",
            side="bottom"
        )