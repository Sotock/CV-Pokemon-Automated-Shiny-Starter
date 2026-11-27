import tkinter as tk
from tkinter import ttk, messagebox
from queue import Empty

from PIL import Image

from instances.hunting_worker import HuntingWorker
from instances.hunting_controller import HuntingState
from gui.hunting_instance_panel import HuntingInstancePanel


class HuntingDashboard(tk.Toplevel):

    POLL_INTERVAL = 100
    PANEL_PADDING = 6

    def __init__(self, parent, configurations):

        super().__init__(parent)

        self.withdraw()

        self.title("Shiny Hunting Dashboard")
        self.geometry("1200x850")
        self.minsize(450, 500)

        self.transient(parent.winfo_toplevel())

        self.entries = []
        self.column_count = 0
        self.panel_width = 0
        self.poll_id = None
        self.closing = False

        self.status_var = tk.StringVar(
            value="Initializing hunting instances..."
        )

        self.protocol(
            "WM_DELETE_WINDOW",
            self.request_close
        )

        self.create_widgets()
        self.create_instances(configurations)

        self.measure_panels()

        self.arrange_panels(1)

        self.deiconify()

        self.update_idletasks()

        self.resize_dashboard()

        self.grab_set()

        self.after(0, self.start_workers)

    def create_widgets(self):

        header = ttk.Frame(
            self,
            padding=15
        )

        header.pack(fill="x")

        ttk.Label(
            header,
            text="Shiny Hunting Dashboard",
            font=("Segoe UI", 20, "bold")
        ).pack(anchor="w")

        ttk.Label(
            header,
            textvariable=self.status_var
        ).pack(
            anchor="w",
            pady=(5, 10)
        )

        controls = ttk.Frame(header)

        controls.pack(fill="x")

        self.stop_all_button = ttk.Button(
            controls,
            text="Stop All",
            command=self.stop_all
        )

        self.stop_all_button.pack(side="left")

        ttk.Button(
            controls,
            text="Close Dashboard",
            command=self.request_close
        ).pack(side="right")

        # Scrollable instance display.

        container = ttk.Frame(self)

        container.pack(
            fill="both",
            expand=True,
            padx=15,
            pady=(0, 15)
        )

        container.columnconfigure(0, weight=1)
        container.rowconfigure(0, weight=1)

        self.canvas = tk.Canvas(
            container,
            highlightthickness=0,
            borderwidth=0
        )

        self.canvas.grid(
            row=0,
            column=0,
            sticky="nsew"
        )

        self.scrollbar = ttk.Scrollbar(
            container,
            orient="vertical",
            command=self.canvas.yview
        )

        self.scrollbar.grid(
            row=0,
            column=1,
            sticky="ns"
        )

        self.canvas.configure(
            yscrollcommand=self.scrollbar.set
        )

        # The outer frame follows the canvas width.
        # The inner frame retains its natural dimensions.

        self.canvas_content = ttk.Frame(
            self.canvas
        )

        self.canvas_window = self.canvas.create_window(
            (0, 0),
            window=self.canvas_content,
            anchor="nw"
        )

        self.panel_container = ttk.Frame(
            self.canvas_content
        )

        self.panel_container.pack(
            anchor="n"
        )

        self.canvas_content.bind(
            "<Configure>",
            self.update_scroll_region
        )

        self.panel_container.bind(
            "<Configure>",
            self.update_scroll_region
        )

        self.canvas.bind(
            "<Configure>",
            self.resize_dashboard
        )

        self.bind(
            "<MouseWheel>",
            self.scroll_dashboard
        )

    def create_instances(self, configurations):

        for profile_name, configuration in (
                configurations.items()
        ):

            profile = configuration["profile"]
            count = configuration["count"]

            for _ in range(count):

                worker = HuntingWorker(
                    profile_name
                )

                panel = HuntingInstancePanel(
                    self.panel_container,
                    profile_name=profile_name,
                    target=profile["target_name"],
                    on_stop=lambda w=worker: (
                        self.stop_worker(w)
                    )
                )

                self.entries.append({
                    "worker": worker,
                    "panel": panel,
                    "handled": False,
                    "launch_failed": False
                })

    def measure_panels(self):

        self.update_idletasks()

        self.panel_width = max(
            (
                entry["panel"].winfo_reqwidth()
                for entry in self.entries
            ),
            default=240
        )

        # Account for panel padding, canvas margins,
        # scrollbar width, and a small safety margin.

        minimum_width = (
                self.panel_width
                + self.PANEL_PADDING * 2
                + self.scrollbar.winfo_reqwidth()
                + 50
        )

        self.minsize(
            max(450, minimum_width),
            500
        )

    def arrange_panels(self, columns):

        if not self.entries:
            return

        columns = max(
            1,
            min(columns, len(self.entries))
        )

        if columns == self.column_count:
            return

        # Remove panels from their previous grid positions.

        for entry in self.entries:

            entry["panel"].grid_forget()

        # Clear all previous column settings.

        for column in range(self.column_count):

            self.panel_container.columnconfigure(
                column,
                weight=0,
                minsize=0,
                pad=0,
                uniform=""
            )

        self.column_count = columns

        # Columns retain their measured minimum width.
        # They do not expand into unused canvas space.

        for column in range(columns):

            self.panel_container.columnconfigure(
                column,
                weight=0,
                minsize=(
                        self.panel_width
                        + self.PANEL_PADDING * 2
                ),
                uniform=""
            )

        for index, entry in enumerate(self.entries):

            panel = entry["panel"]

            panel.grid(
                row=index // columns,
                column=index % columns,
                sticky="nsew",
                padx=self.PANEL_PADDING,
                pady=self.PANEL_PADDING
            )

    def resize_dashboard(self, event=None):

        if self.panel_width == 0:
            return

        available_width = (
            event.width
            if event is not None
            else self.canvas.winfo_width()
        )

        if available_width <= 1:
            return

        self.canvas.itemconfigure(
            self.canvas_window,
            width=available_width
        )

        required_width = (
                self.panel_width
                + self.PANEL_PADDING * 2
        )

        columns = max(
            1,
            available_width // required_width
        )

        self.arrange_panels(columns)

        self.update_scroll_region()

    def update_scroll_region(self, event=None):

        bounds = self.canvas.bbox(
            self.canvas_window
        )

        if bounds is not None:

            self.canvas.configure(
                scrollregion=bounds
            )

    def scroll_dashboard(self, event):

        if event.delta:

            direction = (
                -1 if event.delta > 0 else 1
            )

            steps = max(
                1,
                abs(event.delta) // 120
            )

            self.canvas.yview_scroll(
                direction * steps,
                "units"
            )

    def start_workers(self):

        for entry in self.entries:

            worker = entry["worker"]
            panel = entry["panel"]

            panel.update_status("Initializing")

            try:

                worker.start()

            except Exception as error:

                entry["launch_failed"] = True

                panel.update_status("Error")

                print(
                    f"Worker launch failed: {error}"
                )

        self.poll_workers()

    def poll_workers(self):

        self.poll_id = None

        for entry in self.entries:

            worker = entry["worker"]
            panel = entry["panel"]

            while True:

                try:

                    event = worker.events.get_nowait()

                except Empty:

                    break

                self.handle_event(
                    entry,
                    event
                )

            # Access final emulator information only
            # after the worker has completely terminated.

            if (
                    worker.is_finished()
                    and not worker.is_running()
                    and not entry["handled"]
            ):

                worker.join()

                self.handle_completion(entry)

                entry["handled"] = True

        self.update_session_status()

        if self.closing:

            if not any(
                    entry["worker"].is_running()
                    for entry in self.entries
            ):

                self.finish_close()

                return

        self.poll_id = self.after(
            self.POLL_INTERVAL,
            self.poll_workers
        )

    def handle_event(self, entry, event):

        worker = entry["worker"]
        panel = entry["panel"]

        event_type = event["type"]

        if event_type == "initializing":

            panel.update_status(
                "Stopping"
                if worker.stop_event.is_set()
                else "Initializing"
            )

        elif event_type == "initialized":

            panel.update_instance_id(
                event["instance_id"]
            )

            panel.update_status(
                "Stopping"
                if worker.stop_event.is_set()
                else "Hunting"
            )

        elif event_type == "finished":

            panel.update_statistics(
                event["statistics"]
            )

        elif event_type == "error":

            panel.update_status("Error")

            print(
                f"Hunting worker error: "
                f"{event['message']}"
            )

    def handle_completion(self, entry):

        worker = entry["worker"]
        panel = entry["panel"]

        if worker.error is not None:

            panel.update_status("Error")

            return

        controller = worker.controller

        if controller is None:

            panel.update_status("Error")

            return

        panel.update_statistics(
            controller.get_statistics()
        )

        panel.update_classification(
            controller.last_result
        )

        screenshot = controller.last_screenshot

        if screenshot is not None:

            try:

                with Image.open(screenshot) as image:

                    panel.update_framebuffer(
                        image.convert("RGB")
                    )

            except Exception as error:

                print(
                    f"Unable to display screenshot: "
                    f"{error}"
                )

        panel.update_status(
            controller.state.value
        )

        if controller.state == HuntingState.SHINY_FOUND:

            print(
                f"Shiny instance preserved: "
                f"{worker.instance.instance_id}"
            )

    def stop_worker(self, worker):

        worker.request_stop()

        for entry in self.entries:

            if entry["worker"] is worker:

                if worker.is_running():

                    entry["panel"].update_status(
                        "Stopping"
                    )

                break

    def stop_all(self):

        for entry in self.entries:

            worker = entry["worker"]

            if worker.is_running():

                self.stop_worker(worker)

        self.stop_all_button.configure(
            state="disabled"
        )

    def update_session_status(self):

        total = len(self.entries)

        active = sum(
            entry["worker"].is_running()
            for entry in self.entries
        )

        finished = sum(
            entry["handled"]
            or entry["launch_failed"]
            for entry in self.entries
        )

        if self.closing:

            self.status_var.set(
                "Stopping workers before cleanup..."
            )

        else:

            self.status_var.set(
                f"Configured: {total}    "
                f"Active: {active}    "
                f"Finished: {finished}"
            )

        self.stop_all_button.configure(
            state=(
                "normal"
                if active and not self.closing
                else "disabled"
            )
        )

    def request_close(self):

        if self.closing:
            return

        active = any(
            entry["worker"].is_running()
            for entry in self.entries
        )

        if active:

            confirmed = messagebox.askyesno(
                "Close Hunting Dashboard",
                (
                    "Stop all hunting instances "
                    "and close the dashboard?"
                ),
                parent=self
            )

            if not confirmed:
                return

        self.closing = True

        self.stop_all()

        self.update_session_status()

    def finish_close(self):

        shiny_workers = [
            entry["worker"]
            for entry in self.entries
            if (
                    entry["worker"].controller is not None
                    and entry["worker"].controller.state
                    == HuntingState.SHINY_FOUND
            )
        ]

        if shiny_workers:

            confirmed = messagebox.askyesno(
                "Discard Preserved Shiny Encounters",
                (
                    f"{len(shiny_workers)} shiny "
                    "encounter(s) remain preserved.\n\n"
                    "Closing this dashboard will discard "
                    "their temporary emulator states.\n\n"
                    "Continue?"
                ),
                parent=self
            )

            if not confirmed:

                self.closing = False

                self.update_session_status()

                self.poll_id = self.after(
                    self.POLL_INTERVAL,
                    self.poll_workers
                )

                return

        try:

            for entry in self.entries:

                worker = entry["worker"]

                worker.join()
                worker.close()

        except Exception as error:

            self.closing = False

            messagebox.showerror(
                "Cleanup Failed",
                str(error),
                parent=self
            )

            self.poll_id = self.after(
                self.POLL_INTERVAL,
                self.poll_workers
            )

            return

        if self.poll_id is not None:

            self.after_cancel(self.poll_id)

            self.poll_id = None

        self.grab_release()

        self.destroy()