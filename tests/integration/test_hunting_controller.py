from pathlib import Path
import sys
from unittest.mock import patch

PROJECT_DIR = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(PROJECT_DIR))

import cv2

from instances.library_manager import LibraryInstance

from instances.hunting_controller import (
    HuntingController,
    HuntingState
)


PROFILE_NAME = "FireRed Starter"

MAX_ROTATIONS = 5

FAILURE_DIR = (
        PROJECT_DIR / "docs" / "figures" / "macro"
)

FAILURE_IMAGES = [
    "nickname_failure.png",
    "selection_failure.png"
]


def test_continuous_hunting():

    profile_dir = (
            PROJECT_DIR / "saves" / PROFILE_NAME
    )

    save_path = profile_dir / "game.sav"
    metadata_path = profile_dir / "profile.json"

    original_save = save_path.read_bytes()
    original_metadata = metadata_path.read_bytes()

    instance = LibraryInstance(PROFILE_NAME)
    instance_dir = instance.instance_dir

    controller = HuntingController(instance)

    try:

        print("\n--- Continuous Hunting Verification ---")

        print("Profile:", instance.profile_name)
        print("Target:", instance.target_name)
        print("Species:", instance.target_species)
        print("Maximum rotations:", MAX_ROTATIONS)

        assert controller.state == HuntingState.READY

        print("Initial hunting state: PASS")

        final_state = controller.run(
            max_rotations=MAX_ROTATIONS
        )

        statistics = controller.get_statistics()

        assert final_state in (
            HuntingState.COMPLETED,
            HuntingState.SHINY_FOUND
        )

        if final_state == HuntingState.COMPLETED:

            assert (
                    statistics["completed_rotations"]
                    == MAX_ROTATIONS
            )

            assert statistics["shinies_found"] == 0

            print("\nRotation limit verification: PASS")

        else:

            assert statistics["shinies_found"] == 1

            assert controller.last_result["valid_summary"]
            assert controller.last_result["is_shiny"]

            print("\nNatural shiny prediction: PASS")

        assert statistics["attempts"] == (
            statistics["completed_rotations"]
        )

        assert statistics["completed_rotations"] == (
                statistics["valid_encounters"]
                + statistics["failed_rotations"]
        )

        assert statistics["elapsed_seconds"] > 0

        print("Rotation counter consistency: PASS")
        print("Elapsed time tracking: PASS")

        assert controller.last_screenshot is not None
        assert controller.last_screenshot.is_file()

        print("Final screenshot preservation: PASS")

        assert instance.core is not None
        assert instance.screen is not None
        assert instance_dir.is_dir()

        print("Emulator state preservation: PASS")

        assert save_path.read_bytes() == original_save

        assert (
                metadata_path.read_bytes()
                == original_metadata
        )

        print("Permanent profile preservation: PASS")

        print("\n--- Final Hunting Statistics ---")

        for name, value in statistics.items():

            if isinstance(value, float):

                print(f"{name}: {value:.4f}")

            else:

                print(f"{name}: {value}")

    finally:

        instance.close()

    assert not instance_dir.exists()

    assert save_path.read_bytes() == original_save
    assert metadata_path.read_bytes() == original_metadata

    print("\nTemporary instance cleanup: PASS")
    print("Permanent save unchanged: True")
    print("Permanent metadata unchanged: True")

    print("\nContinuous hunting verification: PASS")


def test_automatic_fault_recovery():

    profile_dir = (
            PROJECT_DIR / "saves" / PROFILE_NAME
    )

    save_path = profile_dir / "game.sav"
    metadata_path = profile_dir / "profile.json"

    original_save = save_path.read_bytes()
    original_metadata = metadata_path.read_bytes()

    failure_frames = {}

    for rotation, filename in enumerate(
            FAILURE_IMAGES,
            start=2
    ):

        image = cv2.imread(
            str(FAILURE_DIR / filename)
        )

        assert image is not None
        assert image.shape == (160, 240, 3)

        failure_frames[rotation] = image

    instance = LibraryInstance(PROFILE_NAME)
    instance_dir = instance.instance_dir

    controller = HuntingController(instance)

    original_macro = instance.run_macro
    original_get_frame = instance.get_frame_bgr
    original_classified_attempt = (
        instance.run_classified_attempt
    )

    genuine_rotations = []
    injected_rotations = []
    rotation_history = []

    def controlled_macro(core, screen, screenshot_path):

        rotation = instance.attempts

        if rotation in failure_frames:

            print(
                f"\n--- Injecting Controlled Fault "
                f"at Rotation {rotation} ---"
            )

            print(
                "Failure sample:",
                FAILURE_IMAGES[rotation - 2]
            )

            image = failure_frames[rotation]

            if not cv2.imwrite(
                    str(screenshot_path),
                    image
            ):

                raise RuntimeError(
                    "Unable to save injected screenshot."
                )

            injected_rotations.append(rotation)

        else:

            print(
                f"\n--- Genuine Macro Rotation "
                f"{rotation} ---"
            )

            original_macro(
                core,
                screen,
                screenshot_path
            )

            genuine_rotations.append(rotation)

    def controlled_frame():

        rotation = instance.attempts

        if rotation in failure_frames:

            return failure_frames[rotation]

        return original_get_frame()

    def recorded_attempt():

        screenshot, result = (
            original_classified_attempt()
        )

        statistics = instance.get_statistics()

        rotation_history.append({
            "rotation": instance.attempts,
            "valid_summary": result["valid_summary"],
            "is_shiny": result["is_shiny"],
            "votes": result["votes"],
            "valid_encounters": statistics["valid_encounters"],
            "failed_rotations": statistics["failed_rotations"],
            "consecutive_failures": statistics[
                "consecutive_failures"
            ]
        })

        return screenshot, result

    try:

        print("\n--- Automatic Fault Recovery Verification ---")

        print("Profile:", instance.profile_name)
        print("Target:", instance.target_name)
        print("Species:", instance.target_species)

        print("\nExpected rotation sequence:")
        print("Rotation 1: Genuine macro")
        print("Rotation 2: Nickname entry fault")
        print("Rotation 3: Starter selection fault")
        print("Rotation 4: Genuine recovery macro")

        assert controller.state == HuntingState.READY

        with patch.object(
                instance,
                "run_macro",
                side_effect=controlled_macro
        ):

            with patch.object(
                    instance,
                    "get_frame_bgr",
                    side_effect=controlled_frame
            ):

                with patch.object(
                        instance,
                        "run_classified_attempt",
                        side_effect=recorded_attempt
                ):

                    final_state = controller.run(
                        max_rotations=4
                    )

        statistics = controller.get_statistics()

        print("\n--- Rotation History ---")

        for record in rotation_history:

            print(
                f"Rotation {record['rotation']}: "
                f"valid={record['valid_summary']}, "
                f"encounters={record['valid_encounters']}, "
                f"failures={record['failed_rotations']}, "
                f"consecutive="
                f"{record['consecutive_failures']}"
            )

        # If the first genuine encounter produces a shiny
        # prediction, the controller must stop immediately.
        if (
                final_state == HuntingState.SHINY_FOUND
                and statistics["completed_rotations"] == 1
        ):

            assert genuine_rotations == [1]
            assert injected_rotations == []

            print(
                "\nShiny detected before fault injection."
            )

            print(
                "Automatic fault recovery experiment "
                "incomplete. Repeat the test."
            )

        else:

            assert len(rotation_history) == 4

            assert genuine_rotations == [1, 4]
            assert injected_rotations == [2, 3]

            print("\nAutomatic rotation progression: PASS")
            print("Genuine recovery macro execution: PASS")

            first = rotation_history[0]
            second = rotation_history[1]
            third = rotation_history[2]
            fourth = rotation_history[3]

            assert first["valid_summary"]

            assert not second["valid_summary"]
            assert second["is_shiny"] is None
            assert second["votes"] is None

            assert not third["valid_summary"]
            assert third["is_shiny"] is None
            assert third["votes"] is None

            assert second["valid_encounters"] == 1
            assert third["valid_encounters"] == 1

            assert second["failed_rotations"] == 1
            assert third["failed_rotations"] == 2

            assert second["consecutive_failures"] == 1
            assert third["consecutive_failures"] == 2

            print("Invalid rotation rejection: PASS")
            print("Failed rotation tracking: PASS")
            print("Consecutive failure tracking: PASS")

            assert fourth["valid_summary"]
            assert fourth["valid_encounters"] == 2
            assert fourth["failed_rotations"] == 2
            assert fourth["consecutive_failures"] == 0

            print("Successful automatic recovery: PASS")
            print("Consecutive failure reset: PASS")

            assert final_state in (
                HuntingState.COMPLETED,
                HuntingState.SHINY_FOUND
            )

            assert statistics["attempts"] == 4
            assert statistics["completed_rotations"] == 4
            assert statistics["valid_encounters"] == 2
            assert statistics["failed_rotations"] == 2
            assert statistics["consecutive_failures"] == 0

            assert statistics["success_rate"] == 50.0

            assert statistics["shinies_found"] == int(
                fourth["is_shiny"]
            )

            assert statistics["completed_rotations"] == (
                    statistics["valid_encounters"]
                    + statistics["failed_rotations"]
            )

            print("Rotation counter consistency: PASS")

            assert controller.last_result["valid_summary"]

            assert controller.last_screenshot is not None

            assert controller.last_screenshot.is_file()

            print("Final valid summary preservation: PASS")

        assert instance.core is not None
        assert instance.screen is not None
        assert instance_dir.is_dir()

        print("Emulator state preservation: PASS")

        assert save_path.read_bytes() == original_save

        assert (
                metadata_path.read_bytes()
                == original_metadata
        )

        print("Permanent profile preservation: PASS")

        print("\n--- Final Hunting Statistics ---")

        for name, value in statistics.items():

            if isinstance(value, float):

                print(f"{name}: {value:.4f}")

            else:

                print(f"{name}: {value}")

    finally:

        instance.close()

    assert not instance_dir.exists()

    assert save_path.read_bytes() == original_save
    assert metadata_path.read_bytes() == original_metadata

    print("\nTemporary instance cleanup: PASS")
    print("Permanent save unchanged: True")
    print("Permanent metadata unchanged: True")

    if len(rotation_history) == 4:

        print("\nAutomatic fault recovery verification: PASS")

    else:

        print("\nAutomatic fault recovery verification: INCOMPLETE")

def test_automatic_shiny_stop():

    profile_dir = (
            PROJECT_DIR / "saves" / PROFILE_NAME
    )

    save_path = profile_dir / "game.sav"
    metadata_path = profile_dir / "profile.json"

    original_save = save_path.read_bytes()
    original_metadata = metadata_path.read_bytes()

    instance = LibraryInstance(PROFILE_NAME)
    instance_dir = instance.instance_dir

    controller = HuntingController(instance)

    original_macro = instance.run_macro
    original_get_frame = instance.get_frame_bgr

    genuine_rotations = []
    injected_rotations = []

    try:

        shiny_path = (
                PROJECT_DIR
                / "dataset"
                / "firered_leafgreen"
                / "evaluation"
                / "shiny"
                / f"{instance.target_species}_01.png"
        )

        shiny_image = cv2.imread(str(shiny_path))

        assert shiny_image is not None
        assert shiny_image.shape == (160, 240, 3)

        def controlled_macro(core, screen, screenshot_path):

            rotation = instance.attempts

            if rotation == 1:

                print("\n--- Genuine Macro Rotation ---")

                original_macro(
                    core,
                    screen,
                    screenshot_path
                )

                genuine_rotations.append(rotation)

            elif rotation == 2:

                print("\n--- Controlled Shiny Injection ---")
                print("Shiny sample:", shiny_path.name)

                if not cv2.imwrite(
                        str(screenshot_path),
                        shiny_image
                ):

                    raise RuntimeError(
                        "Unable to save injected screenshot."
                    )

                injected_rotations.append(rotation)

            else:

                raise AssertionError(
                    "Macro executed after shiny detection."
                )

        def controlled_frame():

            if instance.attempts == 2:

                return shiny_image

            return original_get_frame()

        print("\n--- Automatic Stop-on-Shiny Verification ---")

        print("Profile:", instance.profile_name)
        print("Target:", instance.target_name)
        print("Species:", instance.target_species)

        assert controller.state == HuntingState.READY

        with patch.object(
                instance,
                "run_macro",
                side_effect=controlled_macro
        ):

            with patch.object(
                    instance,
                    "get_frame_bgr",
                    side_effect=controlled_frame
            ):

                final_state = controller.run(
                    max_rotations=10
                )

        statistics = controller.get_statistics()

        assert final_state == HuntingState.SHINY_FOUND

        assert controller.last_result["valid_summary"]
        assert controller.last_result["is_shiny"]

        assert controller.last_result["votes"] >= 2

        assert statistics["shinies_found"] == 1

        print("\nShiny detection: PASS")
        print("Majority voting: PASS")
        print("Automatic hunting termination: PASS")

        if statistics["completed_rotations"] == 1:

            assert genuine_rotations == [1]
            assert injected_rotations == []

            print("Shiny detected during genuine rotation.")
            print("Controlled injection experiment: INCOMPLETE")

        else:

            assert genuine_rotations == [1]
            assert injected_rotations == [2]

            assert statistics["attempts"] == 2
            assert statistics["completed_rotations"] == 2

            assert statistics["valid_encounters"] == 2
            assert statistics["failed_rotations"] == 0
            assert statistics["consecutive_failures"] == 0

            print("Controlled shiny detection: PASS")
            print("Premature rotation limit termination: PASS")

        assert statistics["attempts"] < 10

        print("Subsequent macro prevention: PASS")
        print("Encounter counter consistency: PASS")

        assert controller.last_screenshot is not None
        assert controller.last_screenshot.is_file()

        final_image = cv2.imread(
            str(controller.last_screenshot)
        )

        assert final_image is not None

        if injected_rotations:

            assert (final_image == shiny_image).all()

        print("Shiny screenshot preservation: PASS")
        print("Classification result preservation: PASS")

        assert instance.core is not None
        assert instance.screen is not None
        assert instance_dir.is_dir()

        print("Emulator instance preservation: PASS")

        assert save_path.read_bytes() == original_save
        assert metadata_path.read_bytes() == original_metadata

        print("Permanent profile preservation: PASS")

        print("\n--- Final Hunting Statistics ---")

        for name, value in statistics.items():

            if isinstance(value, float):

                print(f"{name}: {value:.4f}")

            else:

                print(f"{name}: {value}")

    finally:

        instance.close()

    assert not instance_dir.exists()

    assert save_path.read_bytes() == original_save
    assert metadata_path.read_bytes() == original_metadata

    print("\nTemporary instance cleanup: PASS")
    print("Permanent save unchanged: True")
    print("Permanent metadata unchanged: True")

    if injected_rotations:

        print("\nAutomatic stop-on-shiny verification: PASS")

    else:

        print("\nAutomatic stop-on-shiny verification: INCOMPLETE")

def test_user_cancellation():

    from threading import Event, Thread

    profile_dir = (
            PROJECT_DIR / "saves" / PROFILE_NAME
    )

    save_path = profile_dir / "game.sav"
    metadata_path = profile_dir / "profile.json"

    original_save = save_path.read_bytes()
    original_metadata = metadata_path.read_bytes()

    instance = LibraryInstance(PROFILE_NAME)
    instance_dir = instance.instance_dir

    controller = HuntingController(instance)

    original_macro = instance.run_macro

    rotation_started = Event()
    cancellation_requested = Event()

    executed_rotations = []
    worker_errors = []
    worker = None

    def controlled_macro(core, screen, screenshot_path):

        rotation = instance.attempts

        executed_rotations.append(rotation)

        if rotation > 1:

            raise AssertionError(
                "Macro executed after cancellation."
            )

        rotation_started.set()

        if not cancellation_requested.wait(timeout=30):

            raise TimeoutError(
                "Cancellation request was not received."
            )

        original_macro(
            core,
            screen,
            screenshot_path
        )

    def hunting_worker():

        try:

            controller.run(max_rotations=10)

        except Exception as error:

            worker_errors.append(error)

    try:

        print("\n--- User Cancellation Verification ---")

        print("Profile:", instance.profile_name)
        print("Target:", instance.target_name)

        assert controller.state == HuntingState.READY

        with patch.object(
                instance,
                "run_macro",
                side_effect=controlled_macro
        ):

            worker = Thread(
                target=hunting_worker
            )

            worker.start()

            try:

                assert rotation_started.wait(timeout=30)

                assert controller.state == HuntingState.HUNTING

                print("Active hunting state: PASS")

                print("\nRequesting cancellation.")

                controller.request_stop()

                assert controller.stop_event.is_set()

                assert controller.state == HuntingState.STOPPING

                print("Cancellation request: PASS")
                print("Stopping state transition: PASS")

                assert instance.core is not None
                assert instance.screen is not None

                print("Active emulator protection: PASS")

            finally:

                cancellation_requested.set()
                worker.join()

        if worker_errors:

            raise worker_errors[0]

        statistics = controller.get_statistics()

        assert not worker.is_alive()

        print("\nHunting worker termination: PASS")

        assert controller.state in (
            HuntingState.STOPPED,
            HuntingState.SHINY_FOUND
        )

        if controller.state == HuntingState.SHINY_FOUND:

            assert statistics["shinies_found"] == 1

            print("Shiny detection priority: PASS")

        else:

            assert controller.state == HuntingState.STOPPED

            print("Stopped state transition: PASS")

        assert executed_rotations == [1]

        assert statistics["attempts"] == 1
        assert statistics["completed_rotations"] == 1

        assert statistics["completed_rotations"] == (
                statistics["valid_encounters"]
                + statistics["failed_rotations"]
        )

        print("Current rotation completion: PASS")
        print("Subsequent macro prevention: PASS")
        print("Rotation counter consistency: PASS")

        assert controller.last_screenshot is not None
        assert controller.last_screenshot.is_file()

        print("Final screenshot preservation: PASS")

        assert instance.core is not None
        assert instance.screen is not None
        assert instance_dir.is_dir()

        print("Emulator state preservation: PASS")

        assert save_path.read_bytes() == original_save

        assert (
                metadata_path.read_bytes()
                == original_metadata
        )

        print("Permanent profile preservation: PASS")

        print("\n--- Final Hunting Statistics ---")

        for name, value in statistics.items():

            if isinstance(value, float):

                print(f"{name}: {value:.4f}")

            else:

                print(f"{name}: {value}")

    finally:

        cancellation_requested.set()

        if worker is not None and worker.is_alive():

            controller.request_stop()
            worker.join()

        instance.close()

    assert not instance_dir.exists()

    assert save_path.read_bytes() == original_save

    assert metadata_path.read_bytes() == original_metadata

    print("\nTemporary instance cleanup: PASS")
    print("Permanent save unchanged: True")
    print("Permanent metadata unchanged: True")

    print("\nUser cancellation verification: PASS")

def test_concurrent_hunting():

    from threading import Event, Thread

    profile_dir = (
            PROJECT_DIR / "saves" / PROFILE_NAME
    )

    save_path = profile_dir / "game.sav"
    metadata_path = profile_dir / "profile.json"

    original_save = save_path.read_bytes()
    original_metadata = metadata_path.read_bytes()

    instances = {}
    controllers = {}
    workers = []

    worker_errors = []

    instance_a_finished = Event()
    instance_b_started = Event()

    rotations_a = []
    rotations_b = []

    continued_after_shiny = []

    try:

        instances["A"] = LibraryInstance(PROFILE_NAME)
        instances["B"] = LibraryInstance(PROFILE_NAME)

        instance_a = instances["A"]
        instance_b = instances["B"]

        controller_a = HuntingController(instance_a)
        controller_b = HuntingController(instance_b)

        controllers["A"] = controller_a
        controllers["B"] = controller_b

        directory_a = instance_a.instance_dir
        directory_b = instance_b.instance_dir

        print("\n--- Concurrent Hunting Verification ---")

        print("Profile:", PROFILE_NAME)
        print("Instance A:", instance_a.instance_id)
        print("Instance B:", instance_b.instance_id)

        assert (
                instance_a.instance_id
                != instance_b.instance_id
        )

        assert directory_a != directory_b

        assert instance_a.core is not instance_b.core
        assert instance_a.screen is not instance_b.screen

        assert instance_a.rom_path != instance_b.rom_path
        assert instance_a.save_path != instance_b.save_path

        print("Independent emulator instances: PASS")
        print("Isolated ROM and save copies: PASS")

        shiny_path = (
                PROJECT_DIR
                / "dataset"
                / "firered_leafgreen"
                / "evaluation"
                / "shiny"
                / f"{instance_a.target_species}_01.png"
        )

        shiny_image = cv2.imread(str(shiny_path))

        assert shiny_image is not None
        assert shiny_image.shape == (160, 240, 3)

        original_macro_a = instance_a.run_macro
        original_macro_b = instance_b.run_macro

        original_frame_a = instance_a.get_frame_bgr

        def controlled_macro_a(
                core,
                screen,
                screenshot_path
        ):

            rotation = instance_a.attempts

            rotations_a.append(rotation)

            if rotation == 1:

                if not instance_b_started.wait(timeout=60):

                    raise TimeoutError(
                        "Instance B did not start."
                    )

                original_macro_a(
                    core,
                    screen,
                    screenshot_path
                )

            elif rotation == 2:

                print(
                    "\n--- Instance A: "
                    "Controlled Shiny Injection ---"
                )

                if not cv2.imwrite(
                        str(screenshot_path),
                        shiny_image
                ):

                    raise RuntimeError(
                        "Unable to save shiny screenshot."
                    )

            else:

                raise AssertionError(
                    "Instance A continued after shiny detection."
                )

        def controlled_frame_a():

            if instance_a.attempts == 2:

                return shiny_image

            return original_frame_a()

        def controlled_macro_b(
                core,
                screen,
                screenshot_path
        ):

            rotation = instance_b.attempts

            rotations_b.append(rotation)

            if rotation == 1:

                instance_b_started.set()

            if rotation == 2:

                if not instance_a_finished.wait(timeout=120):

                    raise TimeoutError(
                        "Instance A did not terminate."
                    )

                assert (
                        controller_a.state
                        == HuntingState.SHINY_FOUND
                )

                assert instance_a.core is not None

                print(
                    "\nInstance B continued after "
                    "Instance A detected a shiny."
                )

            if instance_a_finished.is_set():

                assert (
                        controller_a.state
                        == HuntingState.SHINY_FOUND
                )

                assert instance_a.core is not None

                continued_after_shiny.append(rotation)

            original_macro_b(
                core,
                screen,
                screenshot_path
            )

        def hunting_worker(
                name,
                controller,
                max_rotations
        ):

            try:

                controller.run(
                    max_rotations=max_rotations
                )

            except Exception as error:

                worker_errors.append(
                    (name, error)
                )

            finally:

                if name == "A":

                    instance_a_finished.set()

        with (
            patch.object(
                instance_a,
                "run_macro",
                side_effect=controlled_macro_a
            ),
            patch.object(
                instance_a,
                "get_frame_bgr",
                side_effect=controlled_frame_a
            ),
            patch.object(
                instance_b,
                "run_macro",
                side_effect=controlled_macro_b
            )
        ):

            worker_a = Thread(
                target=hunting_worker,
                args=("A", controller_a, 10)
            )

            worker_b = Thread(
                target=hunting_worker,
                args=("B", controller_b, 5)
            )

            workers.extend([
                worker_a,
                worker_b
            ])

            worker_b.start()
            worker_a.start()

            for worker in workers:

                worker.join()

        if worker_errors:

            name, error = worker_errors[0]

            raise RuntimeError(
                f"Instance {name} encountered an error."
            ) from error

        assert not worker_a.is_alive()
        assert not worker_b.is_alive()

        print("\nConcurrent worker termination: PASS")

        statistics_a = controller_a.get_statistics()
        statistics_b = controller_b.get_statistics()

        assert (
                controller_a.state
                == HuntingState.SHINY_FOUND
        )

        assert statistics_a["shinies_found"] == 1

        assert controller_a.last_result["valid_summary"]
        assert controller_a.last_result["is_shiny"]

        assert controller_a.last_result["votes"] >= 2

        assert rotations_a in (
            [1],
            [1, 2]
        )

        assert statistics_a["completed_rotations"] in (
            1,
            2
        )

        if rotations_a == [1, 2]:

            print("Controlled shiny detection: PASS")

        else:

            print(
                "Instance A produced a shiny prediction "
                "during genuine macro execution."
            )

        print("Instance A automatic termination: PASS")

        assert controller_b.state in (
            HuntingState.COMPLETED,
            HuntingState.SHINY_FOUND
        )

        if controller_b.state == HuntingState.COMPLETED:

            assert (
                    statistics_b["completed_rotations"]
                    == 5
            )

            assert rotations_b == [1, 2, 3, 4, 5]

            assert statistics_b["shinies_found"] == 0

            assert continued_after_shiny

            print("Instance B continued hunting: PASS")
            print("Independent rotation limit: PASS")

        else:

            assert statistics_b["shinies_found"] == 1

            if continued_after_shiny:

                print(
                    "Instance B continued hunting "
                    "before its own shiny detection: PASS"
                )

            else:

                print(
                    "Concurrent continuation experiment: "
                    "INCOMPLETE"
                )

        assert instance_a.detector is not None
        assert instance_b.detector is not None

        assert (
                instance_a.detector
                is not instance_b.detector
        )

        print("Independent computer vision detectors: PASS")

        for statistics in (
                statistics_a,
                statistics_b
        ):

            assert statistics["attempts"] == (
                statistics["completed_rotations"]
            )

            assert statistics["completed_rotations"] == (
                    statistics["valid_encounters"]
                    + statistics["failed_rotations"]
            )

        print("Independent encounter tracking: PASS")
        print("Rotation counter consistency: PASS")

        assert instance_a.core is not None
        assert instance_a.screen is not None

        assert instance_b.core is not None
        assert instance_b.screen is not None

        assert directory_a.is_dir()
        assert directory_b.is_dir()

        assert controller_a.last_screenshot.is_file()
        assert controller_b.last_screenshot.is_file()

        if rotations_a == [1, 2]:

            preserved_image = cv2.imread(
                str(controller_a.last_screenshot)
            )

            assert preserved_image is not None

            assert (
                    preserved_image == shiny_image
            ).all()

        print("Instance A detection preservation: PASS")
        print("Independent emulator preservation: PASS")

        assert save_path.read_bytes() == original_save

        assert (
                metadata_path.read_bytes()
                == original_metadata
        )

        print("Permanent profile preservation: PASS")

        for name, statistics in (
                ("A", statistics_a),
                ("B", statistics_b)
        ):

            print(
                f"\n--- Instance {name} "
                "Final Hunting Statistics ---"
            )

            for key, value in statistics.items():

                if isinstance(value, float):

                    print(f"{key}: {value:.4f}")

                else:

                    print(f"{key}: {value}")

        print("\n--- Concurrent Aggregate Statistics ---")

        print(
            "Completed rotations:",
            statistics_a["completed_rotations"]
            + statistics_b["completed_rotations"]
        )

        print(
            "Valid encounters:",
            statistics_a["valid_encounters"]
            + statistics_b["valid_encounters"]
        )

        print(
            "Failed rotations:",
            statistics_a["failed_rotations"]
            + statistics_b["failed_rotations"]
        )

        print(
            "Shinies detected:",
            statistics_a["shinies_found"]
            + statistics_b["shinies_found"]
        )

        print(
            "Instance B rotations after Instance A stopped:",
            continued_after_shiny
        )

        instance_a.close()

        assert not directory_a.exists()

        assert directory_b.is_dir()
        assert instance_b.core is not None
        assert instance_b.screen is not None

        print("\nIndependent instance cleanup: PASS")

    finally:

        for controller in controllers.values():

            controller.request_stop()

        instance_a_finished.set()
        instance_b_started.set()

        for worker in workers:

            if worker.is_alive():

                worker.join()

        for instance in instances.values():

            if instance.core is not None:

                instance.close()

    for instance in instances.values():

        assert not instance.instance_dir.exists()

    assert save_path.read_bytes() == original_save

    assert metadata_path.read_bytes() == original_metadata

    print("Temporary instance cleanup: PASS")
    print("Permanent save unchanged: True")
    print("Permanent metadata unchanged: True")

    if continued_after_shiny:

        print("\nConcurrent hunting verification: PASS")

    else:

        print("\nConcurrent hunting verification: INCOMPLETE")


if __name__ == "__main__":
    # test_continuous_hunting()
    # test_automatic_fault_recovery()
    # test_automatic_shiny_stop()
    #test_user_cancellation()
    test_concurrent_hunting()