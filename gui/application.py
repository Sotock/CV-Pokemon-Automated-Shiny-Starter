import tkinter as tk
from tkinter import ttk

from gui.pages.home_page import HomePage
from gui.pages.profiles_page import ProfilesPage
from gui.pages.hunting_page import HuntingPage


class Application(tk.Tk):

    def __init__(self):

        super().__init__()

        self.title("Pokemon Shiny Hunter")

        self.geometry("1200x800")
        self.minsize(960, 640)

        self.pages = {}
        self.current_page = None

        self.create_layout()
        self.create_pages()

        self.show_page("Home")

        self.protocol(
            "WM_DELETE_WINDOW",
            self.close_application
        )

    def create_layout(self):

        self.columnconfigure(1, weight=1)
        self.rowconfigure(0, weight=1)

        # Navigation sidebar

        self.sidebar = ttk.Frame(
            self,
            width=200,
            padding=15
        )

        self.sidebar.grid(
            row=0,
            column=0,
            sticky="ns"
        )

        self.sidebar.grid_propagate(False)

        ttk.Label(
            self.sidebar,
            text="Pokemon\nShiny Hunter",
            font=("Segoe UI", 16, "bold")
        ).pack(
            anchor="w",
            pady=(0, 20)
        )

        ttk.Separator(
            self.sidebar,
            orient="horizontal"
        ).pack(
            fill="x",
            pady=(0, 15)
        )

        for page_name in (
                "Home",
                "Profiles",
                "Hunting"
        ):

            ttk.Button(
                self.sidebar,
                text=page_name,
                command=lambda name=page_name: (
                    self.show_page(name)
                )
            ).pack(
                fill="x",
                pady=4
            )

        # Main content area

        self.content = ttk.Frame(
            self,
            padding=20
        )

        self.content.grid(
            row=0,
            column=1,
            sticky="nsew"
        )

        self.content.rowconfigure(
            0,
            weight=1
        )

        self.content.columnconfigure(
            0,
            weight=1
        )

    def create_pages(self):

        page_classes = {
            "Home": HomePage,
            "Profiles": ProfilesPage,
            "Hunting": HuntingPage
        }

        for name, page_class in page_classes.items():

            page = page_class(
                self.content,
                self
            )

            self.pages[name] = page

            page.grid(
                row=0,
                column=0,
                sticky="nsew"
            )

    def show_page(self, page_name):

        if page_name not in self.pages:

            raise ValueError(
                f"Unknown application page: {page_name}"
            )

        page = self.pages[page_name]

        page.tkraise()

        self.current_page = page_name

    def close_application(self):

        self.destroy()