from tkinter import ttk

from profiles.game_registry import (
    get_supported_games,
    get_supported_starters,
    get_game_config
)

from gui.pages.hunting_page import MAX_INSTANCES

# Displays the application overview, supported games, and navigation shortcuts.
class HomePage(ttk.Frame):
    # Initializes the home page.
    def __init__(self, parent, application):
        super().__init__(parent)
        self.application = application
        self.create_widgets()

    # Creates the home page heading and content sections.
    def create_widgets(self):
        ttk.Label(
            self,
            text="Pokemon Shiny Hunter",
            font=("Segoe UI", 20, "bold")
        ).pack(anchor="w")

        ttk.Label(
            self,
            text=(
                "Automated shiny hunting using "
                "computer vision and integrated emulation."
            ),
            style="Secondary.TLabel"
        ).pack(anchor="w", pady=(5, 20))

        ttk.Separator(
            self,
            orient="horizontal"
        ).pack(fill="x", pady=(0, 20))

        self.create_overview()
        self.create_navigation_cards()
        self.create_supported_games()

    # Displays dynamically calculated application capability statistics.
    def create_overview(self):
        overview = ttk.Frame(
            self,
            style="Panel.TFrame",
            padding=20
        )
        overview.pack(fill="x", pady=(0, 20))

        games = get_supported_games()

        # Count distinct species rather than duplicated starters across games.
        unique_starters = {
            species
            for game in games
            for species in get_game_config(game)["starters"].values()
        }

        statistics = (
            (str(len(games)), "Supported Games"),
            (str(len(unique_starters)), "Unique Starters"),
            (str(MAX_INSTANCES), "Concurrent Instances")
        )

        for column, (value, description) in enumerate(statistics):
            overview.columnconfigure(
                column,
                weight=1,
                uniform="overview"
            )

            item = ttk.Frame(overview, style="Panel.TFrame")
            item.grid(row=0, column=column, sticky="ew")

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
            ).pack(pady=(4, 0))

    # Creates navigation shortcuts for profile management and hunting.
    def create_navigation_cards(self):
        cards = ttk.Frame(self)
        cards.pack(fill="x")

        cards.columnconfigure(0, weight=1, uniform="cards")
        cards.columnconfigure(1, weight=1, uniform="cards")

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

    # Displays supported games and their available starter Pokemon.
    def create_supported_games(self):
        section = ttk.Frame(
            self,
            style="Panel.TFrame",
            padding=20
        )
        section.pack(fill="x", pady=(20, 0))

        ttk.Label(
            section,
            text="Supported Games",
            style="Panel.TLabel",
            font=("Segoe UI", 13, "bold")
        ).grid(
            row=0,
            column=0,
            columnspan=2,
            sticky="w",
            pady=(0, 8)
        )

        for column in range(2):
            section.columnconfigure(column, weight=1, uniform="games")

        for index, game in enumerate(get_supported_games()):
            config = get_game_config(game)
            starters = ", ".join(get_supported_starters(game))

            item = ttk.Frame(section, style="Panel.TFrame")
            item.grid(
                row=1 + index // 2,
                column=index % 2,
                sticky="ew",
                pady=(10, 0)
            )

            ttk.Label(
                item,
                text=f"Pokemon {config['short_name']}",
                style="Panel.TLabel",
                font=("Segoe UI", 10, "bold")
            ).pack(anchor="w")

            ttk.Label(
                item,
                text=starters,
                style="Panel.TLabel"
            ).pack(anchor="w", pady=(3, 0))

    # Creates an individual navigation card with a page shortcut.
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
        ).pack(anchor="w", pady=(10, 20))

        ttk.Button(
            card,
            text=button_text,
            style="Accent.TButton",
            command=lambda: self.application.show_page(page_name)
        ).pack(anchor="w", side="bottom")