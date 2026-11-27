from pathlib import Path
import sys
import shutil
import tkinter as tk

from tkinter import ttk, messagebox
from tempfile import TemporaryDirectory
from unittest.mock import patch

PROJECT_DIR = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(PROJECT_DIR))

from profiles.profile_manager import load_profile
from profiles.game_registry import get_game_config
from instances.library_manager import LibraryInstance
from instances.hunting_controller import HuntingState
from gui.emulator_view import EmulatorView
from gui.hunting_dashboard import HuntingDashboard


SHINY_PROFILE = "FireRed Starter"
NORMAL_PROFILE = "FireRed ASH Bulbasaur"

SAVES_DIR = PROJECT_DIR / "saves"

CONTROLLED_SAVE = (
        PROJECT_DIR
        / "temp"
        / "shiny_preservation"
        / "game.sav"
)


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

        return (
            self.instance.screen
            .to_pil()
            .convert("RGB")
        )

    def press_key(self, key):

        self.instance.core.add_keys(key)
        self.pressed_keys.add(key)

    def release_key(self, key):

        if key in self.pressed_keys:

            self.instance.core.clear_keys(key)
            self.pressed_keys.discard(key)

    def release_all_keys(self):

        for key in tuple(self.pressed_keys):

            self.release_key(key)


def capture_live_summary(
        core,
        screen,
        screenshot_path,
        on_frame=None
):

    screen.to_pil().convert("RGB").save(
        screenshot_path
    )

    if on_frame is not None:

        on_frame(screen)

    print("Actual live shiny summary captured.")


def prepare_shiny_summary(root, instance):

    print("\n--- Controlled Shiny Preparation ---")

    instance.core.reset()

    session = PreparationSession(instance)

    container = ttk.Frame(
        root,
        padding=15
    )

    container.pack(
        fill="both",
        expand=True
    )

    ttk.Label(
        container,
        text="Navigate to the shiny Charmander summary.",
        font=("Segoe UI", 14, "bold")
    ).pack(pady=(0, 10))

    view = EmulatorView(
        container,
        session,
        scale=3
    )

    view.pack()

    ttk.Label(
        container,
        text="Z: A | X: B | Enter: Start | Arrow Keys: Movement"
    ).pack(pady=10)

    prepared = False

    def confirm_summary():

        nonlocal prepared

        view.stop()

        result = instance.classify_frame()

        if not (
                result["valid_summary"]
                and result["is_shiny"]
        ):

            messagebox.showerror(
                "Invalid Preparation",
                "Navigate to the actual shiny Charmander summary.",
                parent=root
            )

            view.start()

            return

        print("Valid summary:", result["valid_summary"])
        print("Border:", result["border"])
        print("Star:", result["star"])
        print("Palette:", result["palette"])
        print("Shiny votes:", result["votes"])
        print("Actual shiny classification: PASS")

        prepared = True

        root.quit()

    def cancel_preparation():

        view.stop()
        root.quit()

    ttk.Button(
        container,
        text="Confirm Shiny Summary",
        command=confirm_summary
    ).pack(pady=10)

    root.protocol(
        "WM_DELETE_WINDOW",
        cancel_preparation
    )

    view.start()

    root.mainloop()

    view.stop()
    container.destroy()

    if not prepared:

        raise RuntimeError(
            "Controlled shiny preparation cancelled."
        )


class NotificationTestDashboard(HuntingDashboard):

    def __init__(self, parent, configurations):

        self.normal_encounters_at_notification = None

        super().__init__(
            parent,
            configurations
        )

    def notify_shiny(self, entry):

        previous_count = len(
            self.shiny_notifications
        )

        super().notify_shiny(entry)

        if (
                len(self.shiny_notifications)
                == previous_count
        ):

            return

        for normal_entry in self.entries:

            worker = normal_entry["worker"]

            if worker.profile_name != NORMAL_PROFILE:

                continue

            instance = worker.instance

            self.normal_encounters_at_notification = (
                instance.valid_encounters
                if instance is not None
                else 0
            )

        print(
            "\n--- Shiny Notification Verification ---"
        )

        print(
            "Normal encounters at notification:",
            self.normal_encounters_at_notification
        )

        print("Allow Bulbasaur to continue hunting.")
        print("Capture the dashboard screenshot.")
        print("Then stop the remaining instance.")


def test_shiny_notification():

    assert CONTROLLED_SAVE.exists(), (
        f"Controlled save missing: {CONTROLLED_SAVE}"
    )

    assert CONTROLLED_SAVE.stat().st_size == 131072

    controlled_save_bytes = (
        CONTROLLED_SAVE.read_bytes()
    )

    original_profiles = {}

    for profile_name in (
            SHINY_PROFILE,
            NORMAL_PROFILE
    ):

        profile_directory = (
                SAVES_DIR / profile_name
        )

        original_profiles[profile_name] = {
            "save": (
                    profile_directory / "game.sav"
            ).read_bytes(),
            "metadata": (
                    profile_directory / "profile.json"
            ).read_bytes()
        }

    shiny_metadata = load_profile(
        SHINY_PROFILE
    )

    normal_metadata = load_profile(
        NORMAL_PROFILE
    )

    configurations = {
        SHINY_PROFILE: {
            "profile": shiny_metadata,
            "count": 1
        },
        NORMAL_PROFILE: {
            "profile": normal_metadata,
            "count": 1
        }
    }

    root = tk.Tk()

    root.title(
        "Controlled Shiny Notification Test"
    )

    shiny_instance = None
    dashboard = None

    instance_directories = []

    try:

        with TemporaryDirectory(
                prefix="shiny_notification_"
        ) as staging_directory:

            staging_path = Path(
                staging_directory
            )

            staged_profile = (
                    staging_path / SHINY_PROFILE
            )

            staged_profile.mkdir()

            shutil.copy2(
                CONTROLLED_SAVE,
                staged_profile / "game.sav"
            )

            shutil.copy2(
                SAVES_DIR
                / SHINY_PROFILE
                / "profile.json",
                staged_profile / "profile.json"
            )

            with patch(
                    "instances.library_manager.SAVES_DIR",
                    staging_path
            ):

                shiny_instance = LibraryInstance(
                    SHINY_PROFILE
                )

        instance_directories.append(
            shiny_instance.instance_dir
        )

        prepare_shiny_summary(
            root,
            shiny_instance
        )

        shiny_instance.run_macro = (
            capture_live_summary
        )

        original_core_id = id(
            shiny_instance.core
        )

        original_screen_id = id(
            shiny_instance.screen
        )

        def create_test_instance(profile_name):

            if profile_name == SHINY_PROFILE:

                return shiny_instance

            return LibraryInstance(profile_name)

        ttk.Label(
            root,
            text="Controlled notification experiment running.",
            padding=20
        ).pack()

        with patch(
                "instances.hunting_worker.LibraryInstance",
                side_effect=create_test_instance
        ):

            dashboard = NotificationTestDashboard(
                root,
                configurations
            )

            root.protocol(
                "WM_DELETE_WINDOW",
                dashboard.request_close
            )

            def dashboard_destroyed(event):

                if event.widget is dashboard:

                    root.quit()

            dashboard.bind(
                "<Destroy>",
                dashboard_destroyed,
                add="+"
            )

            preservation_verified = False

            def verify_preservation():

                nonlocal preservation_verified

                if not dashboard.winfo_exists():

                    return

                if not preservation_verified:

                    for entry in dashboard.entries:

                        worker = entry["worker"]

                        if (
                                worker.profile_name
                                != SHINY_PROFILE
                        ):

                            continue

                        if not entry["handled"]:

                            continue

                        assert worker.error is None

                        assert (
                                worker.controller.state
                                == HuntingState.SHINY_FOUND
                        )

                        assert not worker.is_running()

                        assert (
                                id(worker.instance.core)
                                == original_core_id
                        )

                        assert (
                                id(worker.instance.screen)
                                == original_screen_id
                        )

                        assert (
                            worker.controller
                            .last_screenshot.exists()
                        )

                        assert (
                                len(dashboard.shiny_notifications)
                                == 1
                        )

                        assert entry["shiny_notified"]

                        # A repeated notification request
                        # must not produce a duplicate alert.

                        dashboard.notify_shiny(entry)

                        assert (
                                len(dashboard.shiny_notifications)
                                == 1
                        )

                        preservation_verified = True

                        print("Shiny worker stopped: PASS")
                        print("Original emulator core preserved: PASS")
                        print("Original framebuffer preserved: PASS")
                        print("Shiny screenshot preserved: PASS")
                        print("Duplicate notification prevention: PASS")

                dashboard.after(
                    200,
                    verify_preservation
                )

            dashboard.after(
                200,
                verify_preservation
            )

            root.mainloop()

        assert preservation_verified

        assert len(
            dashboard.shiny_notifications
        ) == 1

        notification = (
            dashboard.shiny_notifications[0]
        )

        assert notification["target_name"] == "Charmander"
        assert notification["encounters"] == 1
        assert notification["votes"] >= 2

        assert notification["screenshot"].exists()

        print("\n--- Final Worker Verification ---")

        for entry in dashboard.entries:

            worker = entry["worker"]

            assert worker.error is None
            assert not worker.is_running()
            assert worker.closed

            instance = worker.instance

            instance_directories.append(
                instance.instance_dir
            )

            print(
                "Profile:",
                worker.profile_name
            )

            print(
                "Final state:",
                worker.controller.state.value
            )

            print(
                "Valid encounters:",
                instance.valid_encounters
            )

            if worker.profile_name == NORMAL_PROFILE:

                assert (
                        worker.controller.state
                        == HuntingState.STOPPED
                )

                assert (
                        instance.valid_encounters
                        > dashboard.normal_encounters_at_notification
                )

                print(
                    "Continued hunting after shiny detection: PASS"
                )

        for directory in instance_directories:

            assert not directory.exists()

        print("Temporary instance cleanup: PASS")

        for profile_name, original in (
                original_profiles.items()
        ):

            profile_directory = (
                    SAVES_DIR / profile_name
            )

            assert (
                    (profile_directory / "game.sav").read_bytes()
                    == original["save"]
            )

            assert (
                    (profile_directory / "profile.json").read_bytes()
                    == original["metadata"]
            )

            print(
                f"{profile_name}: Permanent profile unchanged"
            )

        assert (
                CONTROLLED_SAVE.read_bytes()
                == controlled_save_bytes
        )

        print("Controlled source save unchanged: PASS")

        print(
            "\nShiny notification verification: PASS"
        )

    finally:

        if dashboard is not None:

            for entry in dashboard.entries:

                worker = entry["worker"]

                worker.request_stop()
                worker.join()

                if not worker.closed:

                    worker.close()

        if (
                shiny_instance is not None
                and shiny_instance.instance_dir.exists()
        ):

            shiny_instance.close()

        root.destroy()


if __name__ == "__main__":

    test_shiny_notification()