from pathlib import Path
import sys
from time import perf_counter, sleep

PROJECT_DIR = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(PROJECT_DIR))

from instances.hunting_worker import HuntingWorker
from instances.hunting_controller import HuntingState


PROFILE_NAMES = (
    "FireRed Starter",
    "FireRed ASH Bulbasaur"
)

MAX_ROTATIONS = 3
DISPLAY_FPS = 10


def test_live_framebuffer_capture():

    print("\n--- Live Framebuffer Capture Verification ---")

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
        HuntingWorker(
            name,
            display_fps=DISPLAY_FPS
        )
        for name in PROFILE_NAMES
    ]

    sequences = [0] * len(workers)
    received_frames = [0] * len(workers)
    changed_frames = [0] * len(workers)
    previous_frames = [None] * len(workers)
    previous_times = [None] * len(workers)

    instance_directories = []

    started_at = perf_counter()

    def consume_frame(index, worker):

        snapshot = worker.get_latest_frame(
            after_sequence=sequences[index]
        )

        if snapshot is None:

            return

        frame = snapshot["frame"]
        sequence = snapshot["sequence"]
        timestamp = snapshot["timestamp"]

        assert frame.size == (240, 160)
        assert frame.mode == "RGB"

        assert sequence > sequences[index]

        if previous_times[index] is not None:

            assert (
                    timestamp - previous_times[index]
                    >= 1.0 / DISPLAY_FPS - 0.000001
            ), "Framebuffer capture exceeded its limit."

        frame_bytes = frame.tobytes()

        if previous_frames[index] is not None:

            if frame_bytes != previous_frames[index]:

                changed_frames[index] += 1

        sequences[index] = sequence

        received_frames[index] += 1

        previous_frames[index] = frame_bytes
        previous_times[index] = timestamp

    try:

        for worker in workers:

            worker.start(
                max_rotations=MAX_ROTATIONS
            )

        print("Concurrent worker initialization: PASS")

        while not all(
                worker.is_finished()
                for worker in workers
        ):

            assert (
                    perf_counter() - started_at < 120
            ), "Framebuffer experiment timed out."

            for index, worker in enumerate(workers):

                consume_frame(index, worker)

            sleep(0.025)

        for index, worker in enumerate(workers):

            assert worker.join(timeout=120)

            consume_frame(index, worker)

        elapsed = perf_counter() - started_at

        print("\n--- Framebuffer Capture Results ---")

        for index, worker in enumerate(workers):

            assert worker.error is None, worker.error

            assert worker.instance is not None

            instance = worker.instance

            instance_directories.append(
                instance.instance_dir
            )

            assert worker.controller.state in (
                HuntingState.COMPLETED,
                HuntingState.SHINY_FOUND
            )

            if (
                    worker.controller.state
                    == HuntingState.COMPLETED
            ):

                assert (
                        instance.completed_rotations
                        == MAX_ROTATIONS
                )

            assert instance.valid_encounters > 0

            statistics = worker.get_frame_statistics()

            assert statistics["captured_frames"] > 1

            assert received_frames[index] > 1
            assert changed_frames[index] > 0

            assert (
                    statistics["measured_fps"]
                    <= DISPLAY_FPS + 0.001
            )

            assert (
                    statistics["captured_frames"]
                    >= received_frames[index]
            )

            print("\nProfile:", worker.profile_name)
            print("Instance:", instance.instance_id)

            print(
                "Completed rotations:",
                instance.completed_rotations
            )

            print(
                "Valid encounters:",
                instance.valid_encounters
            )

            print(
                "Failed rotations:",
                instance.failed_rotations
            )

            print(
                "Target display FPS:",
                statistics["target_fps"]
            )

            print(
                "Captured frames:",
                statistics["captured_frames"]
            )

            print(
                "Received frames:",
                received_frames[index]
            )

            print(
                "Changed frame observations:",
                changed_frames[index]
            )

            print(
                f"Measured capture FPS: "
                f"{statistics['measured_fps']:.4f}"
            )

            print(
                f"Total capture time: "
                f"{statistics['capture_seconds']:.6f} seconds"
            )

            capture_time_ms = (
                    statistics["capture_seconds"]
                    / statistics["captured_frames"]
                    * 1000
            )

            print(
                f"Average capture time: "
                f"{capture_time_ms:.4f} ms"
            )

            # Check that requesting the same sequence
            # again does not return an unnecessary image.

            assert worker.get_latest_frame(
                after_sequence=sequences[index]
            ) is None

            print("Duplicate frame suppression: PASS")

            # Verify that modifying a retrieved image
            # does not modify the stored framebuffer.

            snapshot = worker.get_latest_frame()

            original_pixels = snapshot["frame"].tobytes()

            original_pixel = snapshot["frame"].getpixel(
                (0, 0)
            )

            changed_pixel = tuple(
                255 - value
                for value in original_pixel
            )

            snapshot["frame"].putpixel(
                (0, 0),
                changed_pixel
            )

            assert (
                    snapshot["frame"].tobytes()
                    != original_pixels
            )

            assert (
                    worker.get_latest_frame()["frame"].tobytes()
                    == original_pixels
            )

            print("Detached framebuffer copies: PASS")
            print("Framebuffer resolution: PASS")
            print("Framebuffer color format: PASS")
            print("Progressive framebuffer updates: PASS")
            print("Framebuffer capture throttling: PASS")
            print("Hunting execution preservation: PASS")

        assert (
                workers[0].instance.instance_id
                != workers[1].instance.instance_id
        )

        print("\nIndependent framebuffer workers: PASS")

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

    for worker in workers:

        assert worker.get_latest_frame() is None

    print("\n--- Resource Preservation ---")

    print("Temporary instance cleanup: PASS")
    print("Framebuffer resource cleanup: PASS")

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

    print("\nLive framebuffer capture verification: PASS")


if __name__ == "__main__":

    test_live_framebuffer_capture()