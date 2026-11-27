from pathlib import Path
import sys
from unittest.mock import patch

PROJECT_DIR = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(PROJECT_DIR))

import cv2
import numpy as np

from instances.library_manager import LibraryInstance
from instances.hunting_controller import (
    HuntingController,
    HuntingState
)
from instances.manual_takeover import ManualTakeover


PROFILE_NAME = "FireRed Starter"


def test_manual_takeover():

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

    original_core_id = id(instance.core)
    original_screen_id = id(instance.screen)

    takeover = None

    try:

        print("\n--- Manual Takeover Verification ---")

        print("Profile:", instance.profile_name)
        print("Target:", instance.target_name)

        try:

            ManualTakeover(controller)

        except RuntimeError:

            print("Premature takeover rejection: PASS")

        else:

            raise AssertionError(
                "Premature manual takeover was accepted."
            )

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

        original_macro = instance.run_macro

        def controlled_macro(
                core,
                screen,
                screenshot_path
        ):

            original_macro(
                core,
                screen,
                screenshot_path
            )

            assert controller.state == HuntingState.HUNTING

            try:

                ManualTakeover(controller)

            except RuntimeError:

                print("Active hunting takeover rejection: PASS")

            else:

                raise AssertionError(
                    "Takeover was allowed during hunting."
                )

        with (
            patch.object(
                instance,
                "run_macro",
                side_effect=controlled_macro
            ),
            patch.object(
                instance,
                "get_frame_bgr",
                return_value=shiny_image
            )
        ):

            final_state = controller.run(
                max_rotations=1
            )

        assert final_state == HuntingState.SHINY_FOUND

        assert controller.finished_at is not None
        assert controller.last_result["is_shiny"]

        print("Controlled shiny termination: PASS")

        takeover = ManualTakeover(controller)

        assert takeover.active

        assert takeover.instance is instance

        assert id(instance.core) == original_core_id
        assert id(instance.screen) == original_screen_id

        assert instance.instance_dir == instance_dir
        assert instance_dir.is_dir()

        print("\n--- Manual Emulator Access ---")
        print("Manual takeover initialization: PASS")
        print("Original emulator core retained: PASS")
        print("Original framebuffer retained: PASS")
        print("Original temporary instance retained: PASS")

        frame = takeover.get_frame()

        assert frame.size == (240, 160)
        assert frame.mode == "RGB"

        print("Framebuffer retrieval: PASS")
        print("Target FPS:", takeover.target_fps)

        original_frame = frame.tobytes()

        # Verify the actual emulator is displaying
        # a valid summary before manual input.
        actual_image = cv2.cvtColor(
            np.asarray(frame),
            cv2.COLOR_RGB2BGR
        )

        assert instance.detector.validate_summary(
            actual_image,
            instance.target_species
        ), "Genuine macro did not reach a valid summary."

        print("Initial live summary verification: PASS")

        # B exits the Pokemon summary interface.
        takeover.press_key(1)

        assert 1 in takeover.pressed_keys

        for _ in range(5):

            takeover.run_frame()

        takeover.release_key(1)

        assert 1 not in takeover.pressed_keys

        for _ in range(120):

            takeover.run_frame()

        updated_frame = takeover.get_frame()

        assert updated_frame.tobytes() != original_frame

        updated_image = cv2.cvtColor(
            np.asarray(updated_frame),
            cv2.COLOR_RGB2BGR
        )

        assert not instance.detector.validate_summary(
            updated_image,
            instance.target_species
        ), "B button did not exit the summary interface."

        print("Manual button input: PASS")
        print("Manual frame advancement: PASS")
        print("Framebuffer update: PASS")
        print("Summary exit verification: PASS")

        # Verify simultaneous key tracking and release.
        takeover.press_key(4)
        takeover.press_key(6)

        assert takeover.pressed_keys == {4, 6}

        takeover.release_all_keys()

        assert not takeover.pressed_keys

        print("Multiple key tracking: PASS")
        print("Key release: PASS")

        # End manual control without destroying the emulator.
        takeover.close()

        assert not takeover.active

        assert id(instance.core) == original_core_id
        assert id(instance.screen) == original_screen_id

        assert instance_dir.is_dir()

        print("\nManual takeover termination: PASS")
        print("Emulator preservation: PASS")

        try:

            takeover.run_frame()

        except RuntimeError:

            print("Inactive frame advancement rejection: PASS")

        else:

            raise AssertionError(
                "Inactive takeover advanced the emulator."
            )

        assert save_path.read_bytes() == original_save
        assert metadata_path.read_bytes() == original_metadata

        print("Permanent profile preservation: PASS")

    finally:

        if takeover is not None and takeover.active:

            takeover.close()

        instance.close()

    assert not instance_dir.exists()

    assert save_path.read_bytes() == original_save
    assert metadata_path.read_bytes() == original_metadata

    print("\nTemporary instance cleanup: PASS")
    print("Permanent save unchanged: True")
    print("Permanent metadata unchanged: True")

    print("\nManual takeover verification: PASS")

def test_manual_gameplay_integration():

    import tkinter as tk
    from time import perf_counter
    from gui.emulator_view import EmulatorView

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

    original_core_id = id(instance.core)
    original_screen_id = id(instance.screen)

    takeover = None
    root = None
    view = None

    frame_count = 0
    started_at = None
    finished_at = None

    try:

        print("\n--- Manual Gameplay Integration ---")

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

        with patch.object(
                instance,
                "get_frame_bgr",
                return_value=shiny_image
        ):

            final_state = controller.run(
                max_rotations=1
            )

        assert final_state == HuntingState.SHINY_FOUND

        takeover = ManualTakeover(controller)

        assert id(instance.core) == original_core_id
        assert id(instance.screen) == original_screen_id

        print("Hunting instance preservation: PASS")

        original_run_frame = takeover.run_frame

        def counted_frame():

            nonlocal frame_count

            original_run_frame()

            frame_count += 1

        takeover.run_frame = counted_frame

        root = tk.Tk()

        root.title(
            f"Manual Takeover - {instance.target_name}"
        )

        root.resizable(False, False)

        view = EmulatorView(root, takeover)

        view.pack()

        def finish_gameplay():

            nonlocal finished_at

            view.stop()

            takeover.close()

            finished_at = perf_counter()

            root.quit()

        root.protocol(
            "WM_DELETE_WINDOW",
            finish_gameplay
        )

        tk.Button(
            root,
            text="Finish Manual Gameplay",
            command=finish_gameplay
        ).pack(pady=8)

        print("\n--- Manual Gameplay Controls ---")
        print("Z: A")
        print("X: B")
        print("Enter: Start")
        print("Backspace: Select")
        print("Arrow keys: Movement")
        print("A: L")
        print("S: R")

        print("\nExit the summary screen.")
        print("Return to the overworld and move around.")
        print("Open and close the Start menu.")
        print("Select Finish Manual Gameplay when done.")

        started_at = perf_counter()
        view.start()

        root.mainloop()

        assert finished_at is not None

        elapsed = finished_at - started_at

        assert frame_count > 0
        assert elapsed > 0

        measured_fps = frame_count / elapsed

        print("\n--- Manual Gameplay Performance ---")

        print("Frames executed:", frame_count)
        print(f"Elapsed time: {elapsed:.4f} seconds")
        print(f"Target FPS: {takeover.target_fps:.4f}")
        print(f"Measured FPS: {measured_fps:.4f}")

        fps_error = (
                abs(measured_fps - takeover.target_fps)
                / takeover.target_fps
                * 100
        )

        print(f"FPS deviation: {fps_error:.2f}%")

        assert id(instance.core) == original_core_id
        assert id(instance.screen) == original_screen_id

        assert instance_dir.is_dir()

        assert not takeover.active
        assert not takeover.pressed_keys

        print("\nOriginal emulator preservation: PASS")
        print("Manual gameplay frame advancement: PASS")
        print("Manual gameplay termination: PASS")
        print("Key release: PASS")

        assert save_path.read_bytes() == original_save
        assert metadata_path.read_bytes() == original_metadata

        print("Permanent profile preservation: PASS")

    finally:

        if view is not None:

            view.stop()

        if takeover is not None and takeover.active:

            takeover.close()

        if root is not None:

            root.destroy()

        instance.close()

    assert not instance_dir.exists()
    assert save_path.read_bytes() == original_save
    assert metadata_path.read_bytes() == original_metadata

    print("\nTemporary instance cleanup: PASS")
    print("Permanent save unchanged: True")
    print("Permanent metadata unchanged: True")

    print("\nManual gameplay integration: PASS")

def test_live_shiny_preservation():

    import tkinter as tk
    import shutil

    from tempfile import TemporaryDirectory
    from profiles.game_registry import get_game_config
    from gui.emulator_view import EmulatorView

    controlled_save = (
            PROJECT_DIR
            / "temp"
            / "shiny_preservation"
            / "game.sav"
    )

    profile_dir = (
            PROJECT_DIR / "saves" / PROFILE_NAME
    )

    save_path = profile_dir / "game.sav"
    metadata_path = profile_dir / "profile.json"

    assert controlled_save.is_file()
    assert controlled_save.stat().st_size == 131072

    original_save = save_path.read_bytes()
    original_metadata = metadata_path.read_bytes()
    original_controlled_save = controlled_save.read_bytes()

    # Substitute the controlled save without modifying
    # the permanent hunting profile.

    with TemporaryDirectory(
            dir=PROJECT_DIR / "temp"
    ) as staging_dir:

        staging_path = Path(staging_dir)

        staged_profile = staging_path / PROFILE_NAME
        staged_profile.mkdir()

        shutil.copy2(
            controlled_save,
            staged_profile / "game.sav"
        )

        shutil.copy2(
            metadata_path,
            staged_profile / "profile.json"
        )

        with patch(
                "instances.library_manager.SAVES_DIR",
                staging_path
        ):

            instance = LibraryInstance(PROFILE_NAME)

    instance_dir = instance.instance_dir

    controller = HuntingController(instance)

    original_core_id = id(instance.core)
    original_screen_id = id(instance.screen)

    root = None
    view = None
    takeover = None

    class PreparationSession:

        def __init__(self, instance):

            self.instance = instance

            config = get_game_config(instance.game)

            self.target_fps = config["target_fps"]
            self.frame_interval = 1 / self.target_fps

            self.pressed_keys = set()

        def run_frame(self):

            self.instance.core.run_frame()

        def get_frame(self):

            return self.instance.screen.to_pil().convert("RGB")

        def press_key(self, key):

            self.instance.core.add_keys(key)
            self.pressed_keys.add(key)

        def release_key(self, key):

            self.instance.core.clear_keys(key)
            self.pressed_keys.discard(key)

        def release_all_keys(self):

            for key in tuple(self.pressed_keys):

                self.release_key(key)

    try:

        print("\n--- Live Shiny Preservation ---")

        print("Profile:", instance.profile_name)
        print("Target:", instance.target_name)
        print("Controlled save loaded: PASS")

        assert instance.save_path.read_bytes() == original_controlled_save

        print("Controlled save copy verification: PASS")

        # Initialize the emulator from the controlled save.

        instance.core.reset()

        preparation = PreparationSession(instance)

        root = tk.Tk()

        root.title("Prepare Live Shiny Summary")

        root.resizable(False, False)

        view = EmulatorView(root, preparation)
        view.pack()

        ready = False

        def classify_summary():

            nonlocal ready

            view.stop()

            ready = True

            root.quit()

        def cancel_preparation():

            view.stop()

            root.quit()

        button = tk.Button(
            root,
            text="Classify Live Summary",
            command=classify_summary
        )

        button.pack(pady=8)

        root.protocol(
            "WM_DELETE_WINDOW",
            cancel_preparation
        )

        print("\nNavigate to the shiny Charmander summary.")
        print("Select Classify Live Summary when ready.")

        view.start()

        root.mainloop()

        if not ready:

            print("Live shiny experiment cancelled.")

            return

        view.destroy()
        view = None

        button.destroy()

        # Preserve the exact framebuffer selected
        # by the user before classification.

        prepared_frame = instance.get_frame_bgr().copy()

        # Test-specific capture macro.
        # No reset, simulated result, or frame injection.

        def capture_live_summary(
                core,
                screen,
                screenshot_path
        ):

            screen.to_pil().convert("RGB").save(
                screenshot_path
            )

            print("Actual live summary captured.")

        with patch.object(
                instance,
                "run_macro",
                side_effect=capture_live_summary
        ):

            final_state = controller.run(
                max_rotations=1
            )

        result = controller.last_result

        assert result["valid_summary"], (
            "The selected screen is not a valid target summary."
        )

        assert result["is_shiny"], (
            "The selected Pokemon was not classified as shiny."
        )

        assert result["votes"] >= 2

        assert final_state == HuntingState.SHINY_FOUND

        assert np.array_equal(
            prepared_frame,
            instance.get_frame_bgr()
        )

        print("\n--- Live Classification Verification ---")

        print("Actual live summary validation: PASS")
        print("Actual shiny classification: PASS")
        print("Shiny votes:", result["votes"])
        print("Automatic hunting termination: PASS")
        print("Live framebuffer preservation: PASS")

        # Transfer control to the production takeover adapter.

        takeover = ManualTakeover(controller)

        assert id(instance.core) == original_core_id
        assert id(instance.screen) == original_screen_id

        assert np.array_equal(
            prepared_frame,
            instance.get_frame_bgr()
        )

        print("Original emulator core retained: PASS")
        print("Original framebuffer retained: PASS")
        print("Shiny summary retained during takeover: PASS")

        root.title("Live Shiny - Manual Takeover")

        view = EmulatorView(root, takeover)
        view.pack()

        finished = False

        def finish_takeover():

            nonlocal finished

            view.stop()

            takeover.close()

            finished = True

            root.quit()

        tk.Button(
            root,
            text="Verify Preserved Shiny",
            command=finish_takeover
        ).pack(pady=8)

        root.protocol(
            "WM_DELETE_WINDOW",
            finish_takeover
        )

        print("\n--- Live Shiny Manual Gameplay ---")
        print("Exit the shiny Pokemon summary.")
        print("Return to the overworld.")
        print("Move around and open the party menu.")
        print("Return to the same shiny Charmander summary.")
        print("Select Verify Preserved Shiny.")

        view.start()

        root.mainloop()

        assert finished

        # Reclassify the genuine framebuffer after gameplay.

        final_frame = instance.get_frame_bgr()

        assert instance.detector.validate_summary(
            final_frame,
            instance.target_species
        )

        final_result = instance.detector.predict(
            final_frame,
            instance.target_species
        )

        assert final_result["is_shiny"]
        assert final_result["votes"] >= 2

        print("\n--- Post-Gameplay Verification ---")

        print("Final shiny votes:", final_result["votes"])
        print("Shiny preservation after gameplay: PASS")

        assert id(instance.core) == original_core_id
        assert id(instance.screen) == original_screen_id

        assert instance.completed_rotations == 1
        assert instance.shinies_found == 1

        assert not takeover.active
        assert not takeover.pressed_keys

        print("Original emulator preservation: PASS")
        print("Hunting statistics unchanged: PASS")
        print("Manual takeover termination: PASS")

        final_screenshot = (
                instance.picture_dir
                / "preserved_shiny.png"
        )

        cv2.imwrite(
            str(final_screenshot),
            final_frame
        )

        print("Preserved shiny screenshot:", final_screenshot)

    finally:

        if view is not None:

            view.stop()

        if takeover is not None and takeover.active:

            takeover.close()

        if root is not None:

            root.destroy()

        instance.close()

    assert not instance_dir.exists()

    assert save_path.read_bytes() == original_save
    assert metadata_path.read_bytes() == original_metadata

    assert (
            controlled_save.read_bytes()
            == original_controlled_save
    )

    print("\nTemporary instance cleanup: PASS")
    print("Permanent save unchanged: True")
    print("Permanent metadata unchanged: True")
    print("Controlled shiny save unchanged: True")

    print("\nLive shiny preservation: PASS")

def test_battery_save_export():

    import tkinter as tk
    import shutil

    from tempfile import TemporaryDirectory
    from profiles.game_registry import get_game_config
    from instances.save_export import export_battery_save
    from gui.emulator_view import EmulatorView

    controlled_save = (
            PROJECT_DIR
            / "temp"
            / "shiny_preservation"
            / "game.sav"
    )

    profile_dir = (
            PROJECT_DIR / "saves" / PROFILE_NAME
    )

    save_path = profile_dir / "game.sav"
    metadata_path = profile_dir / "profile.json"

    assert controlled_save.is_file()

    original_save = save_path.read_bytes()
    original_metadata = metadata_path.read_bytes()
    original_controlled_save = controlled_save.read_bytes()

    with TemporaryDirectory(
            dir=PROJECT_DIR / "temp"
    ) as staging_dir:

        staging_path = Path(staging_dir)

        staged_profile = staging_path / PROFILE_NAME

        staged_profile.mkdir()

        shutil.copy2(
            controlled_save,
            staged_profile / "game.sav"
        )

        shutil.copy2(
            metadata_path,
            staged_profile / "profile.json"
        )

        with patch(
                "instances.library_manager.SAVES_DIR",
                staging_path
        ):

            instance = LibraryInstance(PROFILE_NAME)

    instance_dir = instance.instance_dir

    controller = HuntingController(instance)

    export_path = (
            PROJECT_DIR
            / "exports"
            / f"FireRed_Shiny_{instance.instance_id}.sav"
    )

    root = None
    view = None
    takeover = None

    export_attempted = False
    export_completed = False

    class PreparationSession:

        def __init__(self, instance):

            self.instance = instance

            config = get_game_config(instance.game)

            self.target_fps = config["target_fps"]
            self.frame_interval = 1 / self.target_fps

            self.pressed_keys = set()

        def run_frame(self):

            self.instance.core.run_frame()

        def get_frame(self):

            return self.instance.screen.to_pil().convert("RGB")

        def press_key(self, key):

            self.instance.core.add_keys(key)

            self.pressed_keys.add(key)

        def release_key(self, key):

            self.instance.core.clear_keys(key)

            self.pressed_keys.discard(key)

        def release_all_keys(self):

            for key in tuple(self.pressed_keys):

                self.release_key(key)

    try:

        print("\n--- Battery Save Export Verification ---")

        instance.core.reset()

        preparation = PreparationSession(instance)

        root = tk.Tk()

        root.title("Prepare Shiny for Export")

        root.resizable(False, False)

        view = EmulatorView(root, preparation)

        view.pack()

        ready = False

        def classify_summary():

            nonlocal ready

            view.stop()

            ready = True

            root.quit()

        def cancel():

            view.stop()

            root.quit()

        button = tk.Button(
            root,
            text="Classify Live Summary",
            command=classify_summary
        )

        button.pack(pady=8)

        root.protocol("WM_DELETE_WINDOW", cancel)

        print("Navigate to the shiny Charmander summary.")

        view.start()

        root.mainloop()

        if not ready:

            print("Export experiment cancelled.")

            return

        view.destroy()

        view = None

        button.destroy()

        def capture_live_summary(
                core,
                screen,
                screenshot_path
        ):

            screen.to_pil().convert("RGB").save(
                screenshot_path
            )

        with patch.object(
                instance,
                "run_macro",
                side_effect=capture_live_summary
        ):

            final_state = controller.run(
                max_rotations=1
            )

        assert final_state == HuntingState.SHINY_FOUND

        assert controller.last_result["valid_summary"]
        assert controller.last_result["is_shiny"]

        print("Live shiny detection: PASS")

        takeover = ManualTakeover(controller)

        # Reject export while manual gameplay is active.

        try:

            export_battery_save(
                takeover,
                export_path
            )

        except RuntimeError:

            print("Active gameplay export rejection: PASS")

        else:

            raise AssertionError(
                "Export allowed during active gameplay."
            )

        root.title("Save Shiny Pokemon")

        view = EmulatorView(root, takeover)

        view.pack()

        ready_to_export = False

        def finish_gameplay():

            nonlocal ready_to_export

            view.stop()

            takeover.close()

            ready_to_export = True

            root.quit()

        tk.Button(
            root,
            text="Export Battery Save",
            command=finish_gameplay
        ).pack(pady=8)

        root.protocol("WM_DELETE_WINDOW", cancel)

        print("\n--- In-Game Saving Instructions ---")
        print("Return to the overworld.")
        print("Move to a different location.")
        print("Open the Start menu.")
        print("Select SAVE and confirm.")
        print("Wait until saving has completed.")
        print("Return to the overworld.")
        print("Select Export Battery Save.")

        view.start()

        root.mainloop()

        if not ready_to_export:

            print("Export experiment cancelled.")

            return

        # Reject invalid destinations without
        # destroying the live emulator.

        original_core_id = id(instance.core)

        try:

            export_battery_save(
                takeover,
                save_path
            )

        except ValueError:

            print("Permanent profile overwrite rejection: PASS")

        else:

            raise AssertionError(
                "Permanent profile export was allowed."
            )

        assert id(instance.core) == original_core_id

        try:

            export_battery_save(
                takeover,
                export_path.with_suffix(".txt")
            )

        except ValueError:

            print("Invalid file extension rejection: PASS")

        else:

            raise AssertionError(
                "Invalid export extension was accepted."
            )

        assert id(instance.core) == original_core_id

        # Perform the actual battery save export.

        export_attempted = True

        exported_file = export_battery_save(
            takeover,
            export_path
        )

        export_completed = True

        assert instance.core is None
        assert instance.screen is None

        assert exported_file.is_file()

        exported_data = exported_file.read_bytes()

        assert len(exported_data) == 131072

        assert (
                exported_data
                == instance.save_path.read_bytes()
        )

        assert (
                exported_data != original_controlled_save
        ), "No new in-game save changes were detected."

        print("Native emulator resource release: PASS")
        print("Battery save export: PASS")
        print("Exported save size verification: PASS")
        print("Exported save byte comparison: PASS")
        print("Updated in-game save data: PASS")

        # Reject overwriting an existing export.

        try:

            export_battery_save(
                takeover,
                exported_file
            )

        except FileExistsError:

            print("Existing export overwrite rejection: PASS")

        else:

            raise AssertionError(
                "Existing export was overwritten."
            )

        assert exported_file.read_bytes() == exported_data

        print("Existing export preservation: PASS")

    finally:

        if view is not None:

            view.stop()

        if takeover is not None and takeover.active:

            takeover.close()

        if root is not None:

            root.destroy()

        if not export_attempted or export_completed:

            instance.close()

        else:

            print(
                "Export failed. Temporary save retained:",
                instance.save_path
            )

    assert not instance_dir.exists()

    assert exported_file.is_file()

    assert exported_file.read_bytes() == exported_data

    assert save_path.read_bytes() == original_save

    assert metadata_path.read_bytes() == original_metadata

    assert (
            controlled_save.read_bytes()
            == original_controlled_save
    )

    print("\n--- Final Export Verification ---")

    print("Temporary instance cleanup: PASS")
    print("Export persisted after cleanup: PASS")
    print("Permanent save unchanged: True")
    print("Permanent metadata unchanged: True")
    print("Controlled shiny save unchanged: True")

    print("Exported save:", exported_file)

    print("\nBattery save export verification: PASS")

def test_exported_save_reload():

    import tkinter as tk
    import shutil

    from tempfile import TemporaryDirectory
    from profiles.game_registry import get_game_config
    from gui.emulator_view import EmulatorView

    exported_save = (
            PROJECT_DIR
            / "exports"
            / "FireRed_Shiny_ffed5c98.sav"
    )

    controlled_save = (
            PROJECT_DIR
            / "temp"
            / "shiny_preservation"
            / "game.sav"
    )

    profile_dir = (
            PROJECT_DIR / "saves" / PROFILE_NAME
    )

    save_path = profile_dir / "game.sav"
    metadata_path = profile_dir / "profile.json"

    assert exported_save.is_file()
    assert exported_save.stat().st_size == 131072

    original_export = exported_save.read_bytes()
    original_save = save_path.read_bytes()
    original_metadata = metadata_path.read_bytes()
    original_controlled_save = controlled_save.read_bytes()

    assert original_export != original_controlled_save

    print("\n--- Exported Save Reload Verification ---")

    print("Exported save:", exported_save.name)
    print("Exported save size:", len(original_export))
    print("Updated battery save data: PASS")

    # Create an independent instance using the exported save.

    with TemporaryDirectory(
            dir=PROJECT_DIR / "temp"
    ) as staging_dir:

        staging_path = Path(staging_dir)

        staged_profile = staging_path / PROFILE_NAME

        staged_profile.mkdir()

        shutil.copy2(
            exported_save,
            staged_profile / "game.sav"
        )

        shutil.copy2(
            metadata_path,
            staged_profile / "profile.json"
        )

        with patch(
                "instances.library_manager.SAVES_DIR",
                staging_path
        ):

            instance = LibraryInstance(PROFILE_NAME)

    instance_dir = instance.instance_dir

    root = None
    view = None

    class ReloadSession:

        def __init__(self, instance):

            self.instance = instance

            config = get_game_config(instance.game)

            self.target_fps = config["target_fps"]
            self.frame_interval = 1 / self.target_fps

            self.pressed_keys = set()

        def run_frame(self):

            self.instance.core.run_frame()

        def get_frame(self):

            return self.instance.screen.to_pil().convert("RGB")

        def press_key(self, key):

            self.instance.core.add_keys(key)
            self.pressed_keys.add(key)

        def release_key(self, key):

            self.instance.core.clear_keys(key)
            self.pressed_keys.discard(key)

        def release_all_keys(self):

            for key in tuple(self.pressed_keys):

                self.release_key(key)

    try:

        assert instance.instance_id != "ffed5c98"

        assert not (
                PROJECT_DIR / "temp" / "ffed5c98"
        ).exists()

        assert instance.save_path.read_bytes() == original_export

        print("Independent emulator initialization: PASS")
        print("Previous emulator removed: PASS")
        print("Exported save copy verification: PASS")

        instance.core.reset()

        session = ReloadSession(instance)

        root = tk.Tk()

        root.title("Exported Save Reload Verification")

        root.resizable(False, False)

        view = EmulatorView(root, session)

        view.pack()

        ready = False

        def verify_summary():

            nonlocal ready

            view.stop()

            ready = True

            root.quit()

        def cancel():

            view.stop()

            root.quit()

        tk.Button(
            root,
            text="Verify Reloaded Shiny",
            command=verify_summary
        ).pack(pady=8)

        root.protocol(
            "WM_DELETE_WINDOW",
            cancel
        )

        print("\n--- Manual Reload Verification ---")

        print("Verify saved playtime is 0:04.")
        print("Continue the saved game.")
        print("Verify the saved player location.")
        print("Open the shiny Charmander summary.")
        print("Select Verify Reloaded Shiny.")

        view.start()

        root.mainloop()

        if not ready:

            print("Reload experiment cancelled.")

            return

        # Classify the actual framebuffer from
        # the newly initialized emulator.

        result = instance.classify_frame()

        assert result["valid_summary"], (
            "Reloaded summary validation failed."
        )

        assert result["is_shiny"], (
            "Reloaded Pokemon was not classified as shiny."
        )

        assert result["votes"] >= 2

        print("\n--- Reloaded Shiny Classification ---")

        print("Border:", result["border"])
        print("Star:", result["star"])
        print("Palette:", result["palette"])
        print("Shiny votes:", result["votes"])
        print("Shiny prediction:", result["is_shiny"])

        print("\nReloaded summary validation: PASS")
        print("Reloaded shiny classification: PASS")
        print("Shiny persistence after export: PASS")

        screenshot_path = (
                instance.picture_dir
                / "reloaded_shiny.png"
        )

        assert cv2.imwrite(
            str(screenshot_path),
            instance.get_frame_bgr()
        )

        print("Reloaded shiny screenshot:", screenshot_path)

    finally:

        if view is not None:

            view.stop()

        if root is not None:

            root.destroy()

        instance.close()

    assert not instance_dir.exists()

    assert exported_save.read_bytes() == original_export
    assert save_path.read_bytes() == original_save
    assert metadata_path.read_bytes() == original_metadata

    assert (
            controlled_save.read_bytes()
            == original_controlled_save
    )

    print("\n--- Final Reload Verification ---")

    print("Temporary instance cleanup: PASS")
    print("Exported save unchanged: True")
    print("Permanent save unchanged: True")
    print("Permanent metadata unchanged: True")
    print("Controlled shiny save unchanged: True")

    print("\nExported save reload verification: PASS")


if __name__ == "__main__":
    #test_manual_takeover()
    #test_manual_gameplay_integration()
    #test_live_shiny_preservation()
    #test_battery_save_export()
    test_exported_save_reload()