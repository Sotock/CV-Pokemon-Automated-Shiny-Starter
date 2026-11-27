from tkinter import ttk


class HuntingPage(ttk.Frame):

    def __init__(self, parent, application):

        super().__init__(parent)

        self.application = application

        self.create_widgets()

    def create_widgets(self):

        ttk.Label(
            self,
            text="Automated Hunting",
            font=("Segoe UI", 24, "bold")
        ).pack(
            anchor="w"
        )

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