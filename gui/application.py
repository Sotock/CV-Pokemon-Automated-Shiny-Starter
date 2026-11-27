import tkinter as tk
from tkinter import ttk, messagebox

from gui.pages.home_page import HomePage
from gui.pages.profiles_page import ProfilesPage
from gui.pages.hunting_page import HuntingPage
from gui.preparation_window import PreparationWindow


class Application(tk.Tk):

    SHUTDOWN_POLL_INTERVAL = 100

    def __init__(self):

        super().__init__()

        self.title("Pokemon Shiny Hunter")

        self.geometry("1200x800")
        self.minsize(960, 640)

        self.pages = {}
        self.current_page = None

        self.closing = False
        self.shutdown_poll_id = None

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

        if self.closing:

            return

        if page_name not in self.pages:

            raise ValueError(
                f"Unknown application page: {page_name}"
            )

        page = self.pages[page_name]

        page.tkraise()

        self.current_page = page_name

    def get_preparation_window(self):

        profiles_page = self.pages.get(
            "Profiles"
        )

        if profiles_page is None:

            return None

        for child in profiles_page.winfo_children():

            if (
                    isinstance(child, PreparationWindow)
                    and child.winfo_exists()
            ):

                return child

        return None

    def get_hunting_dashboard(self):

        hunting_page = self.pages.get(
            "Hunting"
        )

        if hunting_page is None:

            return None

        dashboard = hunting_page.dashboard

        if (
                dashboard is not None
                and dashboard.winfo_exists()
        ):

            return dashboard

        return None

    def close_application(self):

        if self.closing:

            return

        self.closing = True

        self.continue_shutdown()

    def continue_shutdown(self):

        preparation = self.get_preparation_window()

        if preparation is not None:

            preparation.lift()

            try:

                preparation.cancel_preparation()

            except Exception as error:

                self.closing = False

                messagebox.showerror(
                    "Application Shutdown Failed",
                    str(error),
                    parent=self
                )

                return

            if preparation.winfo_exists():

                self.closing = False

                return

        dashboard = self.get_hunting_dashboard()

        if dashboard is not None:

            dashboard.lift()

            if dashboard.takeover_window is not None:

                dashboard.takeover_window.lift()

                self.closing = False

                return

            if dashboard.exporting:

                self.closing = False

                return

            try:

                dashboard.request_close()

            except Exception as error:

                self.closing = False

                messagebox.showerror(
                    "Application Shutdown Failed",
                    str(error),
                    parent=self
                )

                return

            if not dashboard.winfo_exists():

                self.continue_shutdown()

                return

            if not dashboard.closing:

                self.closing = False

                return

            self.shutdown_poll_id = self.after(
                self.SHUTDOWN_POLL_INTERVAL,
                self.wait_for_dashboard_shutdown
            )

            return

        self.finish_shutdown()

    def wait_for_dashboard_shutdown(self):

        self.shutdown_poll_id = None

        dashboard = self.get_hunting_dashboard()

        if dashboard is None:

            self.continue_shutdown()

            return

        if not dashboard.closing:

            self.closing = False

            return

        self.shutdown_poll_id = self.after(
            self.SHUTDOWN_POLL_INTERVAL,
            self.wait_for_dashboard_shutdown
        )

    def finish_shutdown(self):

        if self.shutdown_poll_id is not None:

            self.after_cancel(
                self.shutdown_poll_id
            )

            self.shutdown_poll_id = None

        self.destroy()