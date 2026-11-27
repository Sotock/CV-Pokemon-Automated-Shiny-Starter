import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from pathlib import Path
from queue import Empty

from PIL import Image, ImageTk

from instances.hunting_worker import HuntingWorker
from instances.hunting_controller import HuntingState
from gui.hunting_instance_panel import HuntingInstancePanel
from gui.manual_takeover_window import ManualTakeoverWindow
from instances.save_export import export_battery_save
from profiles.game_registry import get_game_config
from gui.grass_background import GrassBackground, create_grass_texture
from gui.theme import Colors
from gui.window_style import apply_window_style

from gui.shiny_audio import play_shiny_sound


class HuntingDashboard(tk.Toplevel):

    POLL_INTERVAL = 100
    PANEL_PADDING = 6
    DISPLAY_FPS = 10

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
        self.panel_height = 0
        self.content_height = 0
        self.poll_id = None
        self.closing = False
        self.takeover_window = None
        self.exporting = False

        self.shiny_notifications = []

        self.background_photo = None
        self.background_size = None

        self.status_var = tk.StringVar(
            value="Initializing hunting instances..."
        )

        self.notification_var = tk.StringVar()

        self.protocol(
            "WM_DELETE_WINDOW",
            self.request_close
        )

        self.create_widgets()
        self.create_instances(configurations)
        self.measure_panels()

        self.deiconify()
        self.update_idletasks()

        apply_window_style(self)

        self.resize_dashboard()

        self.grab_set()

        self.after(0, self.start_workers)

    def create_widgets(self):

        self.background = GrassBackground(self)

        self.background.place(
            x=0,
            y=0,
            relwidth=1,
            relheight=1
        )

        header = ttk.Frame(
            self,
            padding=10
        )

        header.pack(
            fill="x",
            padx=12,
            pady=(12, 8)
        )

        title = GrassBackground(
            header,
            height=76,
            shaded=True,
            watermark=True
        )

        title.pack(
            fill="x",
            pady=(0, 8)
        )

        title.create_text(
            12,
            8,
            text="Shiny Hunting Dashboard",
            font=("Segoe UI", 20, "bold"),
            fill=Colors.TEXT,
            anchor="nw"
        )

        status_item = title.create_text(
            12,
            45,
            text=self.status_var.get(),
            font=("Segoe UI", 10),
            fill=Colors.SECONDARY_TEXT,
            anchor="nw"
        )

        def update_header_status(*args):

            title.itemconfigure(
                status_item,
                text=self.status_var.get()
            )

        self.status_var.trace_add(
            "write",
            update_header_status
        )

        self.notification_frame = tk.Frame(
            header,
            background="#FFF2B3",
            relief="solid",
            borderwidth=1
        )

        tk.Label(
            self.notification_frame,
            text="Shiny Pokemon Found!",
            font=("Segoe UI", 14, "bold"),
            background="#FFF2B3",
            foreground="#634900"
        ).pack(
            anchor="w",
            padx=12,
            pady=(8, 2)
        )

        self.notification_label = tk.Label(
            self.notification_frame,
            textvariable=self.notification_var,
            background="#FFF2B3",
            foreground="#634900",
            justify="left",
            anchor="w",
            wraplength=350
        )

        self.notification_label.pack(
            fill="x",
            padx=12,
            pady=(0, 8)
        )

        self.notification_frame.bind(
            "<Configure>",
            self.resize_notification
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

        self.canvas = tk.Canvas(
            self,
            background="#15221B",
            highlightthickness=0,
            borderwidth=0
        )

        self.scrollbar = ttk.Scrollbar(
            self,
            orient="vertical",
            command=self.canvas.yview
        )

        self.scrollbar.pack(
            side="right",
            fill="y",
            padx=(0, 12),
            pady=(0, 12)
        )

        self.canvas.pack(
            fill="both",
            expand=True,
            padx=(12, 4),
            pady=(0, 12)
        )

        self.background_item = self.canvas.create_image(
            0,
            0,
            anchor="nw"
        )

        self.canvas.configure(
            yscrollcommand=self.update_scrollbar
        )

        self.canvas.bind(
            "<Configure>",
            self.resize_dashboard
        )

        self.bind(
            "<MouseWheel>",
            self.scroll_dashboard
        )

    def resize_notification(self, event):

        self.notification_label.configure(
            wraplength=max(100, event.width - 26)
        )

    def create_instances(self, configurations):

        for profile_name, configuration in (
                configurations.items()
        ):

            profile = configuration["profile"]
            count = configuration["count"]

            game_config = get_game_config(
                profile["game"]
            )

            for _ in range(count):

                worker = HuntingWorker(
                    profile_name,
                    display_fps=self.DISPLAY_FPS
                )

                panel = HuntingInstancePanel(
                    self.canvas,
                    profile_name=profile_name,
                    target=profile["target_name"],
                    on_stop=lambda w=worker: (
                        self.stop_worker(w)
                    ),
                    on_takeover=lambda w=worker: (
                        self.start_manual_takeover(w)
                    ),
                    on_export=lambda w=worker: (
                        self.export_worker_save(w)
                    ),
                    vision_config=game_config["vision_config"]
                )

                canvas_item = self.canvas.create_window(
                    0,
                    0,
                    window=panel,
                    anchor="nw"
                )

                self.entries.append({
                    "worker": worker,
                    "panel": panel,
                    "canvas_item": canvas_item,
                    "handled": False,
                    "launch_failed": False,
                    "frame_sequence": 0,
                    "shiny_notified": False,
                    "takeover": None,
                    "exported_path": None
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

        self.panel_height = max(
            (
                entry["panel"].winfo_reqheight()
                for entry in self.entries
            ),
            default=490
        )

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

            self.content_height = 0
            self.update_scroll_region()

            return

        columns = max(
            1,
            min(columns, len(self.entries))
        )

        self.column_count = columns

        available_width = self.canvas.winfo_width()

        cell_width = (
                self.panel_width
                + self.PANEL_PADDING * 2
        )

        cell_height = (
                self.panel_height
                + self.PANEL_PADDING * 2
        )

        grid_width = columns * cell_width

        offset = max(
            0,
            (available_width - grid_width) // 2
        )

        for index, entry in enumerate(self.entries):

            x = (
                    offset
                    + (index % columns) * cell_width
                    + self.PANEL_PADDING
            )

            y = (
                    (index // columns) * cell_height
                    + self.PANEL_PADDING
            )

            self.canvas.coords(
                entry["canvas_item"],
                x,
                y
            )

        rows = (
                       len(self.entries) + columns - 1
               ) // columns

        self.content_height = rows * cell_height

        self.update_scroll_region()

    def resize_dashboard(self, event=None):

        if self.panel_width == 0:
            return

        width = (
            event.width
            if event is not None
            else self.canvas.winfo_width()
        )

        height = (
            event.height
            if event is not None
            else self.canvas.winfo_height()
        )

        if width <= 1 or height <= 1:
            return

        size = (width, height)

        if size != self.background_size:

            texture = create_grass_texture(
                width,
                height
            )

            self.background_photo = ImageTk.PhotoImage(
                texture,
                master=self.canvas
            )

            self.canvas.itemconfigure(
                self.background_item,
                image=self.background_photo
            )

            self.canvas.tag_lower(
                self.background_item
            )

            self.background_size = size

        required_width = (
                self.panel_width
                + self.PANEL_PADDING * 2
        )

        columns = max(
            1,
            width // required_width
        )

        self.arrange_panels(columns)

    def update_scroll_region(self, event=None):

        width = self.canvas.winfo_width()
        height = self.canvas.winfo_height()

        self.canvas.configure(
            scrollregion=(
                0,
                0,
                width,
                max(height, self.content_height)
            )
        )

        self.position_background()

    def position_background(self):

        self.canvas.coords(
            self.background_item,
            self.canvas.canvasx(0),
            self.canvas.canvasy(0)
        )

    def update_scrollbar(self, first, last):

        self.scrollbar.set(first, last)

        self.position_background()

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

    def update_live_framebuffer(self, entry):

        worker = entry["worker"]
        panel = entry["panel"]

        snapshot = worker.get_latest_frame(
            after_sequence=entry["frame_sequence"]
        )

        if snapshot is None:
            return

        panel.update_framebuffer(
            snapshot["frame"]
        )

        entry["frame_sequence"] = (
            snapshot["sequence"]
        )

    def poll_workers(self):

        self.poll_id = None

        for entry in self.entries:

            worker = entry["worker"]

            while True:

                try:

                    event = worker.events.get_nowait()

                except Empty:

                    break

                self.handle_event(
                    entry,
                    event
                )

            if entry["handled"]:
                continue

            if (
                    worker.is_finished()
                    and not worker.is_running()
            ):

                worker.join()

                self.handle_completion(entry)

                entry["handled"] = True

            elif (
                    worker.is_running()
                    and not entry["launch_failed"]
            ):

                self.update_live_framebuffer(entry)

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

        elif event_type == "rotation":

            panel.update_statistics(
                event["statistics"]
            )

            panel.update_classification(
                event["result"]
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

                self.update_live_framebuffer(entry)

        else:

            self.update_live_framebuffer(entry)

        panel.update_status(
            controller.state.value
        )

        if controller.state == HuntingState.SHINY_FOUND:

            self.notify_shiny(entry)

        frame_statistics = (
            worker.get_frame_statistics()
        )

        print(
            f"[{worker.instance.instance_id}] "
            "Framebuffer capture results:"
        )

        print(
            "Captured frames:",
            frame_statistics["captured_frames"]
        )

        print(
            f"Measured capture FPS: "
            f"{frame_statistics['measured_fps']:.4f}"
        )

        print(
            f"Total capture time: "
            f"{frame_statistics['capture_seconds']:.6f} seconds"
        )

    def notify_shiny(self, entry):

        if entry["shiny_notified"]:
            return

        worker = entry["worker"]
        instance = worker.instance
        controller = worker.controller

        if worker.is_running():
            return

        if controller is None or instance is None:
            return

        if controller.state != HuntingState.SHINY_FOUND:
            return

        result = controller.last_result

        if "votes" in result:

            detection = f"Votes: {result['votes']}/3"

        else:

            detection = "Palette: Shiny"

        notification = {
            "instance_id": instance.instance_id,
            "profile_name": instance.profile_name,
            "target_name": instance.target_name,
            "encounters": instance.valid_encounters,
            "votes": result.get("votes"),
            "detection": detection,
            "screenshot": controller.last_screenshot
        }

        self.shiny_notifications.append(
            notification
        )

        entry["shiny_notified"] = True

        self.update_shiny_notification()

        try:

            play_shiny_sound()

        except tk.TclError as error:

            print(
                f"Unable to play shiny notification: {error}"
            )

        print(
            f"[{instance.instance_id}] "
            f"Shiny notification delivered."
        )

        print(
            f"Profile: {instance.profile_name}"
        )

        print(
            f"Target: {instance.target_name}"
        )

        print(
            f"Encounters: {instance.valid_encounters}"
        )

        print(
            notification["detection"]
        )

        print(
            f"Shiny instance preserved: "
            f"{instance.instance_id}"
        )

    def update_shiny_notification(self):

        if not self.shiny_notifications:
            return

        latest = self.shiny_notifications[-1]

        total = len(
            self.shiny_notifications
        )

        self.notification_var.set(
            f"Shiny encounters found: {total}\n"
            f"Latest: {latest['target_name']} | "
            f"{latest['profile_name']}\n"
            f"Instance: {latest['instance_id']} | "
            f"Encounters: {latest['encounters']} | "
            f"{latest['detection']}"
        )

        if not self.notification_frame.winfo_ismapped():

            self.notification_frame.pack(
                fill="x",
                pady=(0, 10)
            )

    def get_worker_entry(self, worker):

        return next(
            entry for entry in self.entries
            if entry["worker"] is worker
        )

    def start_manual_takeover(self, worker):

        if self.closing or self.exporting:
            return

        if self.takeover_window is not None:

            self.takeover_window.lift()

            return

        entry = self.get_worker_entry(worker)
        panel = entry["panel"]
        controller = worker.controller

        if (
                not entry["handled"]
                or worker.is_running()
                or worker.closed
                or controller is None
                or controller.state != HuntingState.SHINY_FOUND
                or worker.instance is None
                or worker.instance.core is None
                or entry["exported_path"] is not None
        ):
            return

        previous_status = panel.status_var.get()

        panel.update_status("Manual Takeover")

        try:

            self.takeover_window = ManualTakeoverWindow(
                self,
                controller,
                on_finished=lambda takeover, frame: (
                    self.finish_manual_takeover(
                        entry,
                        takeover,
                        frame
                    )
                )
            )

        except Exception as error:

            self.takeover_window = None

            panel.update_status(previous_status)

            messagebox.showerror(
                "Manual Takeover Failed",
                str(error),
                parent=self
            )

    def finish_manual_takeover(self, entry, takeover, frame):

        self.takeover_window = None
        entry["takeover"] = takeover

        panel = entry["panel"]

        panel.update_framebuffer(frame)
        panel.update_status("Ready to Export")

    def export_worker_save(self, worker):

        if (
                self.closing
                or self.exporting
                or self.takeover_window is not None
        ):
            return

        entry = self.get_worker_entry(worker)
        panel = entry["panel"]
        takeover = entry["takeover"]

        if (
                not entry["handled"]
                or worker.is_running()
                or worker.closed
                or takeover is None
                or takeover.active
                or entry["exported_path"] is not None
        ):
            return

        instance = worker.instance

        previous_status = panel.status_var.get()

        self.exporting = True

        panel.update_status("Exporting")

        try:

            exports_dir = (
                    Path(__file__).resolve().parents[1]
                    / "exports"
            )

            exports_dir.mkdir(
                parents=True,
                exist_ok=True
            )

            destination = filedialog.asksaveasfilename(
                parent=self,
                title="Export Shiny Save",
                initialdir=str(exports_dir),
                initialfile=(
                    f"{instance.profile_name}_"
                    f"{instance.instance_id}.sav"
                ),
                defaultextension=".sav",
                filetypes=[("Game Boy Save", "*.sav")]
            )

            if not destination:

                panel.update_status(previous_status)

                return

            exported_path = export_battery_save(
                takeover,
                destination
            )

            entry["exported_path"] = exported_path
            entry["takeover"] = None

            panel.update_status("Save Exported")

            print(
                f"[{instance.instance_id}] "
                f"Save exported: {exported_path}"
            )

            messagebox.showinfo(
                "Save Exported",
                f"Your save was exported to:\n{exported_path}",
                parent=self
            )

        except Exception as error:

            if entry["exported_path"] is None:

                panel.update_status(
                    "Ready to Export"
                    if instance.core is not None
                    else "Export Retry"
                )

            messagebox.showerror(
                "Save Export Failed",
                str(error),
                parent=self
            )

        finally:

            self.exporting = False

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

        shinies = len(
            self.shiny_notifications
        )

        if self.closing:

            self.status_var.set(
                "Stopping workers before cleanup..."
            )

        else:

            self.status_var.set(
                f"Configured: {total}    "
                f"Active: {active}    "
                f"Finished: {finished}    "
                f"Shinies: {shinies}"
            )

        self.stop_all_button.configure(
            state=(
                "normal"
                if active and not self.closing
                else "disabled"
            )
        )

    def request_close(self):

        if self.closing or self.exporting:
            return

        if self.takeover_window is not None:

            self.takeover_window.lift()

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
                    entry["exported_path"] is None
                    and entry["worker"].controller is not None
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