from tkinter import ttk


class Colors:

    BACKGROUND = "#121419"
    SIDEBAR = "#0D0F13"
    PANEL = "#1C2027"
    SURFACE = "#252A33"
    INPUT = "#181B21"
    BORDER = "#363C46"

    TEXT = "#F0F1F3"
    SECONDARY_TEXT = "#A9B0BC"
    DISABLED_TEXT = "#666D78"

    ACCENT = "#C93640"
    ACCENT_HOVER = "#E0444E"
    ACCENT_PRESSED = "#A62932"

    HOVER = "#343B46"
    PRESSED = "#414956"

    SUCCESS = "#62D49A"
    WARNING = "#E9C34B"
    ERROR = "#F06464"
    SHINY = "#F4CF48"

    BLACK = "#080A0D"
    WHITE = "#FFFFFF"


def apply_theme(root):

    root.configure(
        background=Colors.BACKGROUND
    )

    root.option_add(
        "*Font",
        ("Segoe UI", 10)
    )

    root.option_add(
        "*Background",
        Colors.BACKGROUND
    )

    root.option_add(
        "*Foreground",
        Colors.TEXT
    )

    root.option_add(
        "*TCombobox*Listbox.background",
        Colors.INPUT
    )

    root.option_add(
        "*TCombobox*Listbox.foreground",
        Colors.TEXT
    )

    root.option_add(
        "*TCombobox*Listbox.selectBackground",
        Colors.ACCENT
    )

    root.option_add(
        "*TCombobox*Listbox.selectForeground",
        Colors.WHITE
    )

    style = ttk.Style(root)

    style.theme_use("clam")

    style.configure(
        ".",
        background=Colors.BACKGROUND,
        foreground=Colors.TEXT,
        font=("Segoe UI", 10),
        bordercolor=Colors.BORDER,
        lightcolor=Colors.BORDER,
        darkcolor=Colors.BORDER,
        focuscolor=Colors.ACCENT,
        troughcolor=Colors.INPUT
    )

    style.configure(
        "TFrame",
        background=Colors.BACKGROUND
    )

    style.configure(
        "TLabel",
        background=Colors.BACKGROUND,
        foreground=Colors.TEXT
    )

    style.configure(
        "TLabelframe",
        background=Colors.BACKGROUND,
        bordercolor=Colors.BORDER,
        relief="solid"
    )

    style.configure(
        "TLabelframe.Label",
        background=Colors.BACKGROUND,
        foreground=Colors.TEXT,
        font=("Segoe UI", 10, "bold")
    )

    style.configure(
        "TButton",
        background=Colors.SURFACE,
        foreground=Colors.TEXT,
        bordercolor=Colors.BORDER,
        padding=(12, 8),
        relief="flat"
    )

    style.map(
        "TButton",
        background=[
            ("disabled", Colors.PANEL),
            ("pressed", Colors.PRESSED),
            ("active", Colors.HOVER)
        ],
        foreground=[
            ("disabled", Colors.DISABLED_TEXT)
        ]
    )

    style.configure(
        "Accent.TButton",
        background=Colors.ACCENT,
        foreground=Colors.WHITE,
        bordercolor=Colors.ACCENT
    )

    style.map(
        "Accent.TButton",
        background=[
            ("disabled", Colors.PANEL),
            ("pressed", Colors.ACCENT_PRESSED),
            ("active", Colors.ACCENT_HOVER)
        ],
        foreground=[
            ("disabled", Colors.DISABLED_TEXT)
        ]
    )

    style.configure(
        "TEntry",
        fieldbackground=Colors.INPUT,
        foreground=Colors.TEXT,
        insertcolor=Colors.TEXT,
        selectbackground=Colors.ACCENT,
        selectforeground=Colors.WHITE,
        padding=6
    )

    style.map(
        "TEntry",
        fieldbackground=[
            ("disabled", Colors.PANEL),
            ("readonly", Colors.PANEL)
        ],
        foreground=[
            ("disabled", Colors.DISABLED_TEXT)
        ],
        bordercolor=[
            ("focus", Colors.ACCENT)
        ]
    )

    style.configure(
        "TCombobox",
        background=Colors.SURFACE,
        fieldbackground=Colors.INPUT,
        foreground=Colors.TEXT,
        arrowcolor=Colors.TEXT,
        selectbackground=Colors.ACCENT,
        selectforeground=Colors.WHITE,
        padding=6
    )

    style.map(
        "TCombobox",
        fieldbackground=[
            ("disabled", Colors.PANEL),
            ("readonly", Colors.INPUT)
        ],
        foreground=[
            ("disabled", Colors.DISABLED_TEXT),
            ("readonly", Colors.TEXT)
        ],
        selectbackground=[
            ("readonly", Colors.INPUT)
        ],
        selectforeground=[
            ("readonly", Colors.TEXT)
        ]
    )

    style.configure(
        "TSpinbox",
        background=Colors.SURFACE,
        fieldbackground=Colors.INPUT,
        foreground=Colors.TEXT,
        arrowcolor=Colors.TEXT,
        insertcolor=Colors.TEXT,
        padding=6
    )

    style.map(
        "TSpinbox",
        fieldbackground=[
            ("disabled", Colors.PANEL),
            ("readonly", Colors.INPUT)
        ],
        foreground=[
            ("disabled", Colors.DISABLED_TEXT)
        ]
    )

    for widget_style in (
            "TCheckbutton",
            "TRadiobutton"
    ):

        style.configure(
            widget_style,
            background=Colors.BACKGROUND,
            foreground=Colors.TEXT,
            indicatorcolor=Colors.INPUT
        )

        style.map(
            widget_style,
            background=[
                ("active", Colors.BACKGROUND)
            ],
            foreground=[
                ("disabled", Colors.DISABLED_TEXT)
            ],
            indicatorcolor=[
                ("selected", Colors.ACCENT)
            ]
        )

    style.configure(
        "Treeview",
        background=Colors.PANEL,
        fieldbackground=Colors.PANEL,
        foreground=Colors.TEXT,
        bordercolor=Colors.BORDER,
        rowheight=28
    )

    style.map(
        "Treeview",
        background=[
            ("selected", Colors.ACCENT)
        ],
        foreground=[
            ("selected", Colors.WHITE)
        ]
    )

    style.configure(
        "Treeview.Heading",
        background=Colors.SURFACE,
        foreground=Colors.TEXT,
        font=("Segoe UI", 10, "bold"),
        relief="flat"
    )

    style.map(
        "Treeview.Heading",
        background=[
            ("active", Colors.HOVER)
        ]
    )

    for orientation in (
            "Vertical",
            "Horizontal"
    ):

        scrollbar_style = (
            f"{orientation}.TScrollbar"
        )

        style.configure(
            scrollbar_style,
            background=Colors.SURFACE,
            troughcolor=Colors.INPUT,
            arrowcolor=Colors.SECONDARY_TEXT,
            bordercolor=Colors.INPUT,
            relief="flat"
        )

        style.map(
            scrollbar_style,
            background=[
                ("pressed", Colors.PRESSED),
                ("active", Colors.HOVER)
            ]
        )

    style.configure(
        "TSeparator",
        background=Colors.BORDER
    )

    style.configure(
        "Sidebar.TFrame",
        background=Colors.SIDEBAR
    )

    style.configure(
        "Sidebar.TLabel",
        background=Colors.SIDEBAR,
        foreground=Colors.TEXT
    )

    style.configure(
        "Panel.TFrame",
        background=Colors.PANEL
    )

    style.configure(
        "Panel.TLabel",
        background=Colors.PANEL,
        foreground=Colors.TEXT
    )

    style.configure(
        "Heading.TLabel",
        font=("Segoe UI", 20, "bold")
    )

    style.configure(
        "Secondary.TLabel",
        foreground=Colors.SECONDARY_TEXT
    )

    style.configure(
        "Navigation.TButton",
        background=Colors.SIDEBAR,
        foreground=Colors.SECONDARY_TEXT,
        bordercolor=Colors.SIDEBAR,
        anchor="w",
        padding=(14, 10)
    )

    style.map(
        "Navigation.TButton",
        background=[
            ("pressed", Colors.PRESSED),
            ("active", Colors.HOVER)
        ],
        foreground=[
            ("active", Colors.TEXT)
        ]
    )

    style.configure(
        "Selected.Navigation.TButton",
        background=Colors.ACCENT,
        foreground=Colors.WHITE,
        bordercolor=Colors.ACCENT
    )

    style.map(
        "Selected.Navigation.TButton",
        background=[
            ("pressed", Colors.ACCENT_PRESSED),
            ("active", Colors.ACCENT_HOVER)
        ],
        foreground=[
            ("active", Colors.WHITE)
        ]
    )

    return style