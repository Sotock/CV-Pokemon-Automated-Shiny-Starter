from pathlib import Path
import sys
import random
from time import perf_counter, sleep

PROJECT_DIR = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(PROJECT_DIR))

from instances.hunting_worker import HuntingWorker
from instances.hunting_controller import HuntingState


PROFILE_NAME = "FireRed Starter"

MAX_ROTATIONS = 20
RANDOM_SEED = 604
DISPLAY_FPS = 10

CONFIGURATIONS = (
    ("Baseline", 0, False),
    ("Capture only", DISPLAY_FPS, False),
    ("Capture and retrieval", DISPLAY_FPS, True)
)


def run_experiment(name, display_fps, retrieve_frames):

    print(f"\n--- {name} ---")

    random.seed(RANDOM_SEED)

    worker = HuntingWorker(
        PROFILE_NAME,
        display_fps=display_fps
    )

    sequence = 0
    retrieved_frames = 0
    retrieval_seconds = 0.0

    instance_directory = None

    started_at = perf_counter()

    try:

        worker.start(
            max_rotations=MAX_ROTATIONS
        )

        while not worker.is_finished():

            assert (
                    perf_counter() - started_at < 300
            ), "Performance experiment timed out."

            if retrieve_frames:

                retrieval_started = perf_counter()

                snapshot = worker.get_latest_frame(
                    after_sequence=sequence
                )

                retrieval_seconds += (
                        perf_counter() - retrieval_started
                )

                if snapshot is not None:

                    sequence = snapshot["sequence"]

                    assert snapshot["frame"].size == (
                        240, 160
                    )

                    assert snapshot["frame"].mode == "RGB"

                    retrieved_frames += 1

            sleep(0.1)

        assert worker.join(timeout=120)

        elapsed = perf_counter() - started_at

        assert worker.error is None, worker.error

        instance = worker.instance
        controller = worker.controller

        instance_directory = instance.instance_dir

        if controller.state == HuntingState.SHINY_FOUND:

            raise RuntimeError(
                "Shiny encounter detected during benchmark. "
                "The fixed-rotation experiment cannot "
                "be compared."
            )

        assert (
                controller.state
                == HuntingState.COMPLETED
        )

        assert (
                instance.completed_rotations
                == MAX_ROTATIONS
        )

        hunting_statistics = (
            controller.get_statistics()
        )

        frame_statistics = (
            worker.get_frame_statistics()
        )

        results = {
            "name": name,
            "display_fps": display_fps,
            "rotations": (
                hunting_statistics["completed_rotations"]
            ),
            "encounters": (
                hunting_statistics["valid_encounters"]
            ),
            "failures": (
                hunting_statistics["failed_rotations"]
            ),
            "success_rate": (
                hunting_statistics["success_rate"]
            ),
            "hunting_seconds": (
                hunting_statistics["elapsed_seconds"]
            ),
            "total_seconds": elapsed,
            "encounters_per_minute": (
                hunting_statistics["encounters_per_minute"]
            ),
            "captured_frames": (
                frame_statistics["captured_frames"]
            ),
            "measured_fps": (
                frame_statistics["measured_fps"]
            ),
            "capture_seconds": (
                frame_statistics["capture_seconds"]
            ),
            "retrieved_frames": retrieved_frames,
            "retrieval_seconds": retrieval_seconds
        }

        if display_fps == 0:

            assert results["captured_frames"] == 0

        else:

            assert results["captured_frames"] > 0

            assert (
                    results["measured_fps"]
                    <= display_fps + 0.001
            )

        if retrieve_frames:

            assert retrieved_frames > 0

            assert (
                    retrieved_frames
                    <= results["captured_frames"]
            )

        print(f"\n--- {name} Results ---")

        for key, value in results.items():

            if isinstance(value, float):

                print(f"{key}: {value:.6f}")

            else:

                print(f"{key}: {value}")

        return results

    finally:

        worker.request_stop()

        worker.join()

        worker.close()

        if instance_directory is not None:

            assert not instance_directory.exists()

        print("Temporary instance cleanup: PASS")


def test_framebuffer_performance():

    print("\n--- Controlled Framebuffer Performance ---")

    print("Profile:", PROFILE_NAME)
    print("Rotations per experiment:", MAX_ROTATIONS)
    print("Random seed:", RANDOM_SEED)

    profile_directory = (
            PROJECT_DIR / "saves" / PROFILE_NAME
    )

    original_save = (
            profile_directory / "game.sav"
    ).read_bytes()

    original_metadata = (
            profile_directory / "profile.json"
    ).read_bytes()

    results = []

    original_random_state = random.getstate()

    try:

        for configuration in CONFIGURATIONS:

            result = run_experiment(
                *configuration
            )

            results.append(result)

    finally:

        random.setstate(original_random_state)

    baseline = results[0]

    print("\n--- Performance Comparison ---")

    print(
        f"{'Configuration':<24}"
        f"{'Time (s)':>12}"
        f"{'Enc/min':>12}"
        f"{'Overhead':>12}"
        f"{'Success':>12}"
    )

    print("-" * 72)

    for result in results:

        overhead = (
                (
                        result["hunting_seconds"]
                        - baseline["hunting_seconds"]
                )
                / baseline["hunting_seconds"]
                * 100
        )

        result["overhead_percent"] = overhead

        print(
            f"{result['name']:<24}"
            f"{result['hunting_seconds']:>12.4f}"
            f"{result['encounters_per_minute']:>12.2f}"
            f"{overhead:>11.2f}%"
            f"{result['success_rate']:>11.2f}%"
        )

    print("\n--- Framebuffer Measurements ---")

    for result in results:

        print("\nConfiguration:", result["name"])

        print(
            "Captured frames:",
            result["captured_frames"]
        )

        print(
            "Retrieved frames:",
            result["retrieved_frames"]
        )

        print(
            f"Measured capture FPS: "
            f"{result['measured_fps']:.4f}"
        )

        if result["captured_frames"] > 0:

            capture_ms = (
                    result["capture_seconds"]
                    / result["captured_frames"]
                    * 1000
            )

            print(
                f"Average capture time: "
                f"{capture_ms:.4f} ms"
            )

        if result["retrieved_frames"] > 0:

            print(
                f"Total retrieval time: "
                f"{result['retrieval_seconds']:.6f} seconds"
            )

    print("\n--- Permanent Profile Verification ---")

    assert (
            (profile_directory / "game.sav").read_bytes()
            == original_save
    )

    assert (
            (profile_directory / "profile.json").read_bytes()
            == original_metadata
    )

    print("Permanent save unchanged: PASS")
    print("Profile metadata unchanged: PASS")

    print(
        "\nControlled framebuffer performance "
        "verification: PASS"
    )


if __name__ == "__main__":

    test_framebuffer_performance()