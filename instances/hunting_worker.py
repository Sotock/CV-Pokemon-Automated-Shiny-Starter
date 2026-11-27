from threading import Thread, Event, Lock
from queue import Queue
from time import perf_counter
from math import isfinite

from instances.library_manager import LibraryInstance
from instances.hunting_controller import HuntingController


class HuntingWorker:

    def __init__(
            self,
            profile_name,
            display_fps=10
    ):

        if (
                not isinstance(display_fps, (int, float))
                or not isfinite(display_fps)
                or display_fps < 0
        ):

            raise ValueError(
                "Display FPS must be a nonnegative number."
            )

        self.profile_name = profile_name

        self.instance = None
        self.controller = None
        self.thread = None

        self.events = Queue()

        self.stop_event = Event()
        self.finished_event = Event()

        self.lock = Lock()

        self.error = None
        self.closed = False

        # Framebuffer capture configuration
        self.display_fps = display_fps

        self.frame_interval = (
            1.0 / display_fps
            if display_fps > 0
            else None
        )

        self.frame_lock = Lock()

        self.latest_frame = None

        self.frame_sequence = 0

        self.last_frame_time = None
        self.first_frame_time = None

        self.capture_seconds = 0.0

    def capture_frame(self, screen):

        if self.frame_interval is None:

            return

        now = perf_counter()

        if self.last_frame_time is not None:

            elapsed = now - self.last_frame_time

            if elapsed < self.frame_interval:

                return

        capture_started = perf_counter()

        # Copy the framebuffer while still executing
        # inside the owning emulator worker.
        frame = screen.to_pil().convert("RGB").copy()

        with self.frame_lock:

            self.latest_frame = frame

            self.frame_sequence += 1

            if self.first_frame_time is None:

                self.first_frame_time = now

            self.last_frame_time = now

            self.capture_seconds += (
                    perf_counter() - capture_started
            )

    def get_latest_frame(self, after_sequence=0):

        with self.frame_lock:

            if self.latest_frame is None:

                return None

            if self.frame_sequence <= after_sequence:

                return None

            return {
                "sequence": self.frame_sequence,
                "frame": self.latest_frame.copy(),
                "timestamp": self.last_frame_time
            }

    def get_frame_statistics(self):

        with self.frame_lock:

            measured_fps = 0.0

            if self.frame_sequence > 1:

                elapsed = (
                        self.last_frame_time
                        - self.first_frame_time
                )

                if elapsed > 0:

                    measured_fps = (
                            (self.frame_sequence - 1)
                            / elapsed
                    )

            return {
                "target_fps": self.display_fps,
                "captured_frames": self.frame_sequence,
                "measured_fps": measured_fps,
                "capture_seconds": self.capture_seconds
            }

    def start(self, max_rotations=None):

        with self.lock:

            if self.closed:

                raise RuntimeError(
                    "Hunting worker is closed."
                )

            if self.thread is not None:

                raise RuntimeError(
                    "Hunting worker already started."
                )

            self.thread = Thread(
                target=self.run,
                args=(max_rotations,),
                name=f"Hunting-{self.profile_name}",
                daemon=False
            )

            self.thread.start()

    def run(self, max_rotations):

        try:

            self.events.put({
                "type": "initializing",
                "profile": self.profile_name
            })

            instance = LibraryInstance(
                self.profile_name
            )

            if self.display_fps > 0:

                instance.on_frame = self.capture_frame

            controller = HuntingController(
                instance,
                on_rotation=self.events.put
            )

            with self.lock:

                self.instance = instance
                self.controller = controller

                if self.stop_event.is_set():

                    controller.request_stop()

            self.events.put({
                "type": "initialized",
                "instance_id": instance.instance_id,
                "profile": instance.profile_name,
                "game": instance.game,
                "trainer": instance.trainer_name,
                "target": instance.target_name
            })

            final_state = controller.run(
                max_rotations=max_rotations
            )

            self.events.put({
                "type": "finished",
                "instance_id": instance.instance_id,
                "state": final_state.value,
                "statistics": controller.get_statistics()
            })

        except Exception as error:

            self.error = str(error)

            self.events.put({
                "type": "error",
                "profile": self.profile_name,
                "message": self.error
            })

        finally:

            self.finished_event.set()

    def request_stop(self):

        self.stop_event.set()

        with self.lock:

            if self.controller is not None:

                self.controller.request_stop()

    def is_running(self):

        return (
                self.thread is not None
                and self.thread.is_alive()
        )

    def is_finished(self):

        return self.finished_event.is_set()

    def join(self, timeout=None):

        if self.thread is not None:

            self.thread.join(timeout)

        return not self.is_running()

    def close(self):

        with self.lock:

            if self.is_running():

                raise RuntimeError(
                    "Stop and join the hunting worker "
                    "before closing its emulator."
                )

            if self.closed:

                return

            if self.instance is not None:

                self.instance.close()

            with self.frame_lock:

                self.latest_frame = None

            self.closed = True