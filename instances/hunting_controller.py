from enum import Enum
from threading import Event, Lock
from time import perf_counter


class HuntingState(Enum):

    READY = "Ready"
    HUNTING = "Hunting"
    STOPPING = "Stopping"
    STOPPED = "Stopped"
    SHINY_FOUND = "Shiny Found"
    COMPLETED = "Completed"
    ERROR = "Error"


class HuntingController:

    def __init__(self, instance, on_rotation=None):

        self.instance = instance
        self.state = HuntingState.READY

        self.stop_event = Event()
        self.state_lock = Lock()

        self.started_at = None
        self.finished_at = None

        self.last_screenshot = None
        self.last_result = None

        self.error = None
        self.on_rotation = on_rotation

    def publish_rotation(self):

        if self.on_rotation is None:

            return

        self.on_rotation({
            "type": "rotation",
            "instance_id": self.instance.instance_id,
            "statistics": self.get_statistics(),
            "result": self.last_result.copy(),
            "screenshot": self.last_screenshot
        })

    def run(self, max_rotations=None):

        if max_rotations is not None:

            if (
                    not isinstance(max_rotations, int)
                    or max_rotations <= 0
            ):

                raise ValueError(
                    "Maximum rotations must be a positive integer."
                )

        with self.state_lock:

            if self.state != HuntingState.READY:

                raise RuntimeError(
                    "Hunting controller is not ready."
                )

            self.started_at = perf_counter()
            self.state = HuntingState.HUNTING

        instance_id = self.instance.instance_id

        print(
            f"[{instance_id}] Continuous hunting started."
        )

        try:

            while not self.stop_event.is_set():

                screenshot, result = (
                    self.instance.run_classified_attempt()
                )

                self.last_screenshot = screenshot
                self.last_result = result

                valid_encounter = result["valid_encounter"]

                # Determine the next state atomically.
                # Successful shiny detection takes precedence
                # over stop requests and rotation limits.

                with self.state_lock:

                    if valid_encounter and result["is_shiny"]:

                        self.state = HuntingState.SHINY_FOUND

                    elif self.stop_event.is_set():

                        self.state = HuntingState.STOPPED

                    elif (
                            max_rotations is not None
                            and self.instance.completed_rotations
                            >= max_rotations
                    ):

                        self.state = HuntingState.COMPLETED

                    next_state = self.state

                if next_state == HuntingState.SHINY_FOUND:

                    print(
                        f"[{instance_id}] Shiny encounter detected!"
                    )

                self.publish_rotation()

                if next_state in (
                        HuntingState.SHINY_FOUND,
                        HuntingState.STOPPED,
                        HuntingState.COMPLETED
                ):

                    break

                if not valid_encounter:

                    print(
                        f"[{instance_id}] Invalid encounter. "
                        "Retrying hunt."
                    )

                else:

                    print(
                        f"[{instance_id}] Normal encounter. "
                        "Continuing hunt."
                    )

            with self.state_lock:

                if self.state in (
                        HuntingState.HUNTING,
                        HuntingState.STOPPING
                ):

                    self.state = HuntingState.STOPPED

        except Exception as error:

            with self.state_lock:

                self.state = HuntingState.ERROR
                self.error = str(error)

            raise

        finally:

            with self.state_lock:

                self.finished_at = perf_counter()
                final_state = self.state

            print(
                f"[{instance_id}] Hunting state: "
                f"{final_state.value}"
            )

            print(
                f"[{instance_id}] Elapsed time: "
                f"{self.get_elapsed_time():.2f} seconds"
            )

        return self.state

    def request_stop(self):

        with self.state_lock:

            self.stop_event.set()

            if self.state == HuntingState.HUNTING:

                self.state = HuntingState.STOPPING

    def get_elapsed_time(self):

        with self.state_lock:

            started_at = self.started_at
            finished_at = self.finished_at

        if started_at is None:

            return 0.0

        end_time = (
            finished_at
            if finished_at is not None
            else perf_counter()
        )

        return end_time - started_at

    def get_statistics(self):

        statistics = self.instance.get_statistics()

        elapsed = self.get_elapsed_time()

        encounters_per_minute = (
            statistics["valid_encounters"] / elapsed * 60
            if elapsed > 0
            else 0.0
        )

        with self.state_lock:

            state = self.state.value
            error = self.error

        statistics.update({
            "state": state,
            "elapsed_seconds": elapsed,
            "encounters_per_minute": encounters_per_minute,
            "error": error
        })

        return statistics