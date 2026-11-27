from threading import Thread, Event, Lock
from queue import Queue

from instances.library_manager import LibraryInstance
from instances.hunting_controller import HuntingController


class HuntingWorker:

    def __init__(self, profile_name):

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

    def start(self, max_rotations=None):

        with self.lock:

            if self.closed:
                raise RuntimeError("Hunting worker is closed.")

            if self.thread is not None:
                raise RuntimeError("Hunting worker already started.")

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

            controller = HuntingController(
                instance
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

            self.closed = True