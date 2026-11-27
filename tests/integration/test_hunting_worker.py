from pathlib import Path
import sys
from time import perf_counter

PROJECT_DIR = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(PROJECT_DIR))

from instances.hunting_worker import HuntingWorker
from instances.hunting_controller import HuntingState


PROFILE_NAMES = (
    "FireRed Starter",
    "FireRed ASH Bulbasaur"
)

MAX_ROTATIONS = 2


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

    started_at = perf_counter()

    try:

        for worker in workers:

            worker.start(
                max_rotations=MAX_ROTATIONS
            )

        print("Background worker launch: PASS")

        for worker in workers:

            assert worker.join(timeout=120), (
                "Worker failed to finish."
            )

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

            event_types = []

            while not worker.events.empty():

                event = worker.events.get_nowait()

                event_types.append(
                    event["type"]
                )

            assert event_types == [
                "initializing",
                "initialized",
                "finished"
            ]

            print("Worker event delivery: PASS")
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