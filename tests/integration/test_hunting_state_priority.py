from pathlib import Path
import sys
from threading import Event, Thread

PROJECT_DIR = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(PROJECT_DIR))

from instances.hunting_controller import (
    HuntingController,
    HuntingState
)


class ControlledInstance:

    def __init__(self, is_shiny=False):

        self.instance_id = "controlled_test"

        self.is_shiny = is_shiny

        self.rotation_started = Event()
        self.release_rotation = Event()

        self.completed_rotations = 0
        self.valid_encounters = 0
        self.failed_rotations = 0
        self.consecutive_failures = 0
        self.shinies_found = 0

    def run_classified_attempt(self):

        self.rotation_started.set()

        if not self.release_rotation.wait(timeout=10):

            raise TimeoutError(
                "Controlled rotation was not released."
            )

        self.completed_rotations += 1
        self.valid_encounters += 1

        if self.is_shiny:

            self.shinies_found += 1

        result = {
            "valid_summary": True,
            "border": self.is_shiny,
            "star": self.is_shiny,
            "palette": self.is_shiny,
            "votes": 3 if self.is_shiny else 0,
            "is_shiny": self.is_shiny
        }

        return Path("controlled_encounter.png"), result

    def get_statistics(self):

        return {
            "attempts": self.completed_rotations,
            "completed_rotations": self.completed_rotations,
            "valid_encounters": self.valid_encounters,
            "failed_rotations": self.failed_rotations,
            "consecutive_failures": self.consecutive_failures,
            "shinies_found": self.shinies_found,
            "success_rate": (
                100.0 if self.completed_rotations else 0.0
            )
        }


def verify_state(
        name,
        is_shiny,
        request_stop,
        max_rotations,
        expected_state
):

    print(f"\n--- {name} ---")

    instance = ControlledInstance(
        is_shiny=is_shiny
    )

    events = []
    errors = []

    controller = HuntingController(
        instance,
        on_rotation=events.append
    )

    def run_controller():

        try:

            controller.run(
                max_rotations=max_rotations
            )

        except Exception as error:

            errors.append(error)

    thread = Thread(
        target=run_controller
    )

    thread.start()

    try:

        assert instance.rotation_started.wait(
            timeout=10
        )

        assert (
                controller.state
                == HuntingState.HUNTING
        )

        if request_stop:

            controller.request_stop()

            assert (
                    controller.state
                    == HuntingState.STOPPING
            )

        instance.release_rotation.set()

        thread.join(timeout=10)

        assert not thread.is_alive()
        assert not errors, errors

        assert controller.state == expected_state
        assert controller.finished_at is not None

        assert instance.completed_rotations == 1
        assert instance.valid_encounters == 1

        assert len(events) == 1

        event = events[0]

        assert event["type"] == "rotation"

        assert (
                event["statistics"]["state"]
                == expected_state.value
        )

        assert (
                event["result"]["is_shiny"]
                == is_shiny
        )

        assert (
                instance.shinies_found
                == int(is_shiny)
        )

        # A subsequent stop request must not overwrite
        # an already established terminal state.

        controller.request_stop()

        assert controller.state == expected_state

        print("Final state:", controller.state.value)
        print("Rotation event consistency: PASS")
        print("Terminal state preservation: PASS")
        print(f"{name}: PASS")

    finally:

        controller.request_stop()
        instance.release_rotation.set()
        thread.join(timeout=10)


def test_hunting_state_priority():

    verify_state(
        name="Normal encounter at rotation limit",
        is_shiny=False,
        request_stop=False,
        max_rotations=1,
        expected_state=HuntingState.COMPLETED
    )

    verify_state(
        name="Normal encounter with pending stop",
        is_shiny=False,
        request_stop=True,
        max_rotations=None,
        expected_state=HuntingState.STOPPED
    )

    verify_state(
        name="Shiny encounter without stop request",
        is_shiny=True,
        request_stop=False,
        max_rotations=None,
        expected_state=HuntingState.SHINY_FOUND
    )

    verify_state(
        name="Shiny encounter with pending stop",
        is_shiny=True,
        request_stop=True,
        max_rotations=None,
        expected_state=HuntingState.SHINY_FOUND
    )

    verify_state(
        name="Shiny encounter at rotation limit",
        is_shiny=True,
        request_stop=False,
        max_rotations=1,
        expected_state=HuntingState.SHINY_FOUND
    )

    verify_state(
        name="Shiny encounter with stop and rotation limit",
        is_shiny=True,
        request_stop=True,
        max_rotations=1,
        expected_state=HuntingState.SHINY_FOUND
    )

    print(
        "\nHunting state priority verification: PASS"
    )


if __name__ == "__main__":

    test_hunting_state_priority()