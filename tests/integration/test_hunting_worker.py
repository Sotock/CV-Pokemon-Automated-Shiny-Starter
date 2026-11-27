from pathlib import Path
import sys
from time import perf_counter
from queue import Empty

PROJECT_DIR = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(PROJECT_DIR))

from instances.hunting_worker import HuntingWorker
from instances.hunting_controller import HuntingState


PROFILE_NAMES = (
    "FireRed Starter",
    "FireRed ASH Bulbasaur"
)

MAX_ROTATIONS = 3


def test_concurrent_hunting_workers():

    print("\n--- Concurrent Hunting Worker Verification ---")

    original_profiles = {}

    for name in PROFILE_NAMES:

        profile_dir = PROJECT_DIR / "saves" / name

        original_profiles[name] = {
            "save": (
                    profile_dir / "game.sav"
            ).read_bytes(),
            "metadata": (
                    profile_dir / "profile.json"
            ).read_bytes()
        }

    workers = [
        HuntingWorker(name)
        for name in PROFILE_NAMES
    ]

    instance_directories = []

    received_events = {
        worker.profile_name: []
        for worker in workers
    }

    live_updates = {
        worker.profile_name: 0
        for worker in workers
    }

    started_at = perf_counter()

    try:

        for worker in workers:

            worker.start(
                max_rotations=MAX_ROTATIONS
            )

        print("Background worker launch: PASS")

        print("\n--- Live Rotation Events ---")

        while not all(
                worker.is_finished()
                for worker in workers
        ):

            assert (
                    perf_counter() - started_at < 120
            ), "Worker execution timeout."

            for worker in workers:

                try:

                    event = worker.events.get(
                        timeout=0.05
                    )

                except Empty:

                    continue

                received_events[
                    worker.profile_name
                ].append(event)

                if event["type"] == "rotation":

                    statistics = event["statistics"]
                    result = event["result"]

                    if worker.is_running():

                        live_updates[
                            worker.profile_name
                        ] += 1

                    print(
                        f"[{event['instance_id']}] "
                        f"Rotations: "
                        f"{statistics['completed_rotations']} | "
                        f"Encounters: "
                        f"{statistics['valid_encounters']} | "
                        f"Failures: "
                        f"{statistics['failed_rotations']} | "
                        f"Votes: {result['votes']} | "
                        f"State: {statistics['state']}"
                    )

        for worker in workers:

            assert worker.join(timeout=120), (
                "Worker failed to finish."
            )

            while True:

                try:

                    event = worker.events.get_nowait()

                except Empty:

                    break

                received_events[
                    worker.profile_name
                ].append(event)

        elapsed = perf_counter() - started_at

        print("\n--- Worker Execution Results ---")

        for worker in workers:

            assert worker.is_finished()
            assert not worker.is_running()
            assert worker.error is None, worker.error

            assert worker.instance is not None
            assert worker.controller is not None

            instance = worker.instance
            controller = worker.controller

            assert controller.state in (
                HuntingState.COMPLETED,
                HuntingState.SHINY_FOUND
            )

            if controller.state == HuntingState.COMPLETED:

                assert (
                        instance.completed_rotations
                        == MAX_ROTATIONS
                )

            assert instance.valid_encounters > 0

            assert instance.core is not None
            assert instance.screen is not None

            assert instance.instance_dir.is_dir()

            instance_directories.append(
                instance.instance_dir
            )

            print("\nProfile:", worker.profile_name)
            print("Instance ID:", instance.instance_id)
            print("Target:", instance.target_name)
            print("Species:", instance.target_species)
            print("State:", controller.state.value)

            statistics = controller.get_statistics()

            for key, value in statistics.items():

                print(f"{key}: {value}")

            events = received_events[
                worker.profile_name
            ]

            event_types = [
                event["type"]
                for event in events
            ]

            expected_event_types = (
                    ["initializing", "initialized"]
                    + ["rotation"] * instance.completed_rotations
                    + ["finished"]
            )

            assert (
                    event_types == expected_event_types
            )

            print("Worker event ordering: PASS")

            rotation_events = [
                event
                for event in events
                if event["type"] == "rotation"
            ]

            assert (
                    len(rotation_events)
                    == instance.completed_rotations
            )

            print("Rotation event count: PASS")

            previous_valid = 0
            previous_failed = 0

            for number, event in enumerate(
                    rotation_events,
                    start=1
            ):

                assert (
                        event["instance_id"]
                        == instance.instance_id
                )

                snapshot = event["statistics"]
                result = event["result"]

                assert (
                        snapshot["completed_rotations"]
                        == number
                )

                assert (
                        snapshot["valid_encounters"]
                        + snapshot["failed_rotations"]
                        == number
                )

                assert (
                        snapshot["valid_encounters"]
                        >= previous_valid
                )

                assert (
                        snapshot["failed_rotations"]
                        >= previous_failed
                )

                if result["valid_summary"]:

                    assert (
                            snapshot["valid_encounters"]
                            == previous_valid + 1
                    )

                    assert (
                            snapshot["failed_rotations"]
                            == previous_failed
                    )

                    assert result["votes"] in (
                        0, 1, 2, 3
                    )

                    assert (
                            result["is_shiny"]
                            == (result["votes"] >= 2)
                    )

                else:

                    assert (
                            snapshot["failed_rotations"]
                            == previous_failed + 1
                    )

                    assert (
                            snapshot["valid_encounters"]
                            == previous_valid
                    )

                    assert result["is_shiny"] is None
                    assert result["votes"] is None

                assert event["screenshot"].is_file()

                assert (
                        event["screenshot"].parent
                        == instance.picture_dir
                )

                previous_valid = (
                    snapshot["valid_encounters"]
                )

                previous_failed = (
                    snapshot["failed_rotations"]
                )

            print("Progressive rotation statistics: PASS")
            print("Classification event consistency: PASS")
            print("Screenshot event ownership: PASS")

            # Each event must retain its original
            # statistics rather than reference mutable
            # counters from subsequent rotations.

            assert (
                    rotation_events[0]["statistics"][
                        "completed_rotations"
                    ] == 1
            )

            assert (
                    rotation_events[-1]["statistics"][
                        "completed_rotations"
                    ] == instance.completed_rotations
            )

            print("Independent event snapshots: PASS")

            if instance.completed_rotations > 1:

                assert (
                        live_updates[worker.profile_name] > 0
                )

                print("Live event delivery: PASS")

            else:

                print(
                    "Live event delivery: "
                    "Not required for single-rotation completion."
                )

            final_event = events[-1]

            assert (
                    final_event["statistics"]
                    == controller.get_statistics()
            )

            assert (
                    final_event["state"]
                    == controller.state.value
            )

            print("Final statistics consistency: PASS")
            print("Worker completion: PASS")
            print("Emulator preservation: PASS")

        first = workers[0].instance
        second = workers[1].instance

        assert first.instance_id != second.instance_id

        assert first.instance_dir != second.instance_dir

        assert first.core is not second.core
        assert first.screen is not second.screen

        assert first.target_species == "004"
        assert second.target_species == "001"

        print("\n--- Instance Independence ---")

        print("Unique instance identifiers: PASS")
        print("Independent temporary directories: PASS")
        print("Independent emulator cores: PASS")
        print("Independent framebuffers: PASS")
        print("Profile-specific target selection: PASS")

        print(
            f"Concurrent execution time: "
            f"{elapsed:.4f} seconds"
        )

    finally:

        for worker in workers:

            worker.request_stop()

        for worker in workers:

            worker.join()

            worker.close()

    for directory in instance_directories:

        assert not directory.exists()

    print("\n--- Resource Preservation ---")

    print("Temporary instance cleanup: PASS")

    for name, contents in original_profiles.items():

        profile_dir = PROJECT_DIR / "saves" / name

        assert (
                (profile_dir / "game.sav").read_bytes()
                == contents["save"]
        )

        assert (
                (profile_dir / "profile.json").read_bytes()
                == contents["metadata"]
        )

        print(f"{name}: Permanent profile unchanged")

    print("\nConcurrent hunting worker verification: PASS")


if __name__ == "__main__":

    test_concurrent_hunting_workers()