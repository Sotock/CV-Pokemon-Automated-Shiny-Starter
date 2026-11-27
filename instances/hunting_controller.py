from enum import Enum
from threading import Event
from time import perf_counter


class HuntingState(str, Enum):

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
        self.on_rotation = on_rotation

        self.state = HuntingState.READY

        self.stop_event = Event()

        self.started_at = None
        self.finished_at = None

        self.last_screenshot = None
        self.last_result = None

        self.error = None

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

        if self.state != HuntingState.READY:

            raise RuntimeError(
                "Hunting controller is not ready."
            )

        if max_rotations is not None:

            if (
                    not isinstance(max_rotations, int)
                    or max_rotations <= 0
            ):

                raise ValueError(
                    "Maximum rotations must be a positive integer."
                )

        self.started_at = perf_counter()

        self.state = HuntingState.HUNTING

        starting_rotations = (
            self.instance.completed_rotations
        )

        print(
            f"[{self.instance.instance_id}] "
            "Continuous hunting started."
        )

        try:

            while not self.stop_event.is_set():

                screenshot, result = (
                    self.instance.run_classified_attempt()
                )

                self.last_screenshot = screenshot
                self.last_result = result

                # Preserve the emulator immediately
                # following a successful shiny detection.
                if (
                        result["valid_summary"]
                        and result["is_shiny"]
                ):

                    self.state = HuntingState.SHINY_FOUND

                    self.publish_rotation()

                    print(
                        f"[{self.instance.instance_id}] "
                        f"Shiny {self.instance.target_name} found!"
                    )

                    break

                if self.stop_event.is_set():

                    self.state = HuntingState.STOPPED

                    self.publish_rotation()

                    break

                completed = (
                        self.instance.completed_rotations
                        - starting_rotations
                )

                # Optional limit for controlled testing.
                if (
                        max_rotations is not None
                        and completed >= max_rotations
                ):

                    self.state = HuntingState.COMPLETED

                    self.publish_rotation()

                    break

                self.publish_rotation()

                if not result["valid_summary"]:

                    print(
                        f"[{self.instance.instance_id}] "
                        "Invalid rotation. Restarting macro."
                    )

                else:

                    print(
                        f"[{self.instance.instance_id}] "
                        "Normal encounter. Continuing hunt."
                    )

            if self.state in (
                    HuntingState.HUNTING,
                    HuntingState.STOPPING
            ):

                self.state = HuntingState.STOPPED

        except Exception as error:

            self.error = str(error)
            self.state = HuntingState.ERROR

            raise

        finally:

            self.finished_at = perf_counter()

            print(
                f"[{self.instance.instance_id}] "
                f"Hunting state: {self.state.value}"
            )

            print(
                f"[{self.instance.instance_id}] "
                f"Elapsed time: {self.get_elapsed_time():.2f} seconds"
            )

        return self.state

    def request_stop(self):

        self.stop_event.set()

        if self.state == HuntingState.HUNTING:

            self.state = HuntingState.STOPPING

    def get_elapsed_time(self):

        if self.started_at is None:

            return 0.0

        end_time = (
            self.finished_at
            if self.finished_at is not None
            else perf_counter()
        )

        return end_time - self.started_at

    def get_statistics(self):

        statistics = self.instance.get_statistics()

        elapsed = self.get_elapsed_time()

        encounters_per_minute = 0.0

        if elapsed > 0:

            encounters_per_minute = (
                    statistics["valid_encounters"]
                    / elapsed
                    * 60
            )

        return {
            **statistics,
            "state": self.state.value,
            "elapsed_seconds": elapsed,
            "encounters_per_minute": encounters_per_minute,
            "error": self.error
        }