from pathlib import Path
import shutil
import tkinter as tk

from tempfile import TemporaryDirectory
from unittest.mock import patch

import test_shiny_notification as notification_test

from profiles.profile_manager import load_profile
from instances.library_manager import LibraryInstance
from instances.hunting_controller import HuntingState
from gui.hunting_dashboard import HuntingDashboard


PROJECT_DIR = Path(__file__).resolve().parents[2]
SAVES_DIR = PROJECT_DIR / "saves"

SHINY_PROFILE = "Sapphire TEST Treecko"
NORMAL_PROFILE = "Sapphire TEST Torchic"

CONTROLLED_SAVE = (
        PROJECT_DIR / "temp" / "shiny_preservation" / "game.sav"
)


class SapphireNotificationDashboard(
    notification_test.NotificationTestDashboard
):

    def notify_shiny(self, entry):

        previous_count = len(self.shiny_notifications)

        HuntingDashboard.notify_shiny(self, entry)

        if len(self.shiny_notifications) == previous_count:
            return

        for normal_entry in self.entries:

            worker = normal_entry["worker"]

            if worker.profile_name != NORMAL_PROFILE:
                continue

            self.normal_encounters_at_notification = (
                worker.instance.valid_encounters
                if worker.instance is not None
                else 0
            )

        print("\n--- Sapphire Shiny Notification ---")
        print(
            "Normal encounters at notification:",
            self.normal_encounters_at_notification
        )
        print("Allow Torchic to continue hunting.")
        print("Then stop Torchic and perform manual takeover.")
        print("Finish the battle and save in-game.")
        print("Export the shiny save before closing.")


def test_sapphire_shiny_notification():

    assert CONTROLLED_SAVE.is_file()

    controlled_bytes = CONTROLLED_SAVE.read_bytes()

    assert len(controlled_bytes) in (131072, 131088)

    original_profiles = {}

    for name in (SHINY_PROFILE, NORMAL_PROFILE):

        directory = SAVES_DIR / name

        original_profiles[name] = {
            "save": (directory / "game.sav").read_bytes(),
            "metadata": (directory / "profile.json").read_bytes()
        }

    configurations = {
        SHINY_PROFILE: {
            "profile": load_profile(SHINY_PROFILE),
            "count": 1
        },
        NORMAL_PROFILE: {
            "profile": load_profile(NORMAL_PROFILE),
            "count": 1
        }
    }

    root = tk.Tk()
    root.title("Sapphire Controlled Shiny Test")

    shiny_instance = None
    dashboard = None

    preservation_verified = False
    verification_error = None

    try:

        with TemporaryDirectory(
                prefix="sapphire_shiny_"
        ) as staging_directory:

            staging_path = Path(staging_directory)
            staged_profile = staging_path / SHINY_PROFILE

            staged_profile.mkdir()

            shutil.copy2(
                CONTROLLED_SAVE,
                staged_profile / "game.sav"
            )

            shutil.copy2(
                SAVES_DIR / SHINY_PROFILE / "profile.json",
                staged_profile / "profile.json"
            )

            with patch(
                    "instances.library_manager.SAVES_DIR",
                    staging_path
            ):

                shiny_instance = LibraryInstance(
                    SHINY_PROFILE
                )

        original_core_id = id(shiny_instance.core)
        original_screen_id = id(shiny_instance.screen)

        def create_test_instance(profile_name):

            if profile_name == SHINY_PROFILE:
                return shiny_instance

            return LibraryInstance(profile_name)

        with patch(
                "instances.hunting_worker.LibraryInstance",
                side_effect=create_test_instance
        ):

            dashboard = SapphireNotificationDashboard(
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

            def verify_preservation():

                nonlocal preservation_verified
                nonlocal verification_error

                if not dashboard.winfo_exists():
                    return

                if preservation_verified:
                    return

                try:

                    for entry in dashboard.entries:

                        worker = entry["worker"]

                        if worker.profile_name != SHINY_PROFILE:
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

                        result = worker.controller.last_result

                        assert result["valid_battle"]
                        assert result["valid_sprite"]
                        assert result["valid_encounter"]
                        assert result["palette"]
                        assert result["is_shiny"]

                        assert (
                            worker.controller
                            .last_screenshot.exists()
                        )

                        assert len(
                            dashboard.shiny_notifications
                        ) == 1

                        assert entry["shiny_notified"]

                        dashboard.notify_shiny(entry)

                        assert len(
                            dashboard.shiny_notifications
                        ) == 1

                        preservation_verified = True

                        print("\n--- Preservation Verification ---")
                        print("Battle validation: PASS")
                        print("Sprite validation: PASS")
                        print("Shiny palette classification: PASS")
                        print("Shiny worker stopped: PASS")
                        print("Original emulator core preserved: PASS")
                        print("Original framebuffer preserved: PASS")
                        print("Shiny screenshot preserved: PASS")
                        print("Duplicate notification prevention: PASS")

                except Exception as error:

                    verification_error = error
                    root.quit()
                    return

                if not preservation_verified:

                    dashboard.after(
                        100,
                        verify_preservation
                    )

            dashboard.after(
                100,
                verify_preservation
            )

            root.mainloop()

        if verification_error is not None:
            raise verification_error

        assert preservation_verified

        assert len(dashboard.shiny_notifications) == 1

        notification = dashboard.shiny_notifications[0]

        assert notification["target_name"] == "Treecko"
        assert notification["encounters"] == 1
        assert notification["detection"] == "Palette: Shiny"
        assert notification["screenshot"].exists()

        print("\n--- Final Worker Verification ---")

        for entry in dashboard.entries:

            worker = entry["worker"]
            instance = worker.instance

            assert worker.error is None
            assert not worker.is_running()
            assert worker.closed

            print("Profile:", worker.profile_name)
            print("Final state:", worker.controller.state.value)
            print("Valid encounters:", instance.valid_encounters)
            print("Failed rotations:", instance.failed_rotations)

            assert not instance.instance_dir.exists()

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

            elif worker.profile_name == SHINY_PROFILE:

                assert (
                        worker.controller.state
                        == HuntingState.SHINY_FOUND
                )

                assert instance.shinies_found == 1

                exported_path = entry["exported_path"]

                assert exported_path is not None

                exported_path = Path(exported_path)

                assert exported_path.is_file()

                assert exported_path.stat().st_size in (
                    131072,
                    131088
                )

                print("Exported save:", exported_path)
                print(
                    "Exported save size:",
                    exported_path.stat().st_size
                )
                print("Shiny save export: PASS")

        print("Temporary instance cleanup: PASS")

        for name, original in original_profiles.items():

            directory = SAVES_DIR / name

            assert (
                    (directory / "game.sav").read_bytes()
                    == original["save"]
            )

            assert (
                    (directory / "profile.json").read_bytes()
                    == original["metadata"]
            )

            print(f"{name}: Permanent profile unchanged")

        assert CONTROLLED_SAVE.read_bytes() == controlled_bytes

        print("Controlled source save unchanged: PASS")

        print("\nSapphire shiny notification verification: PASS")

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
    test_sapphire_shiny_notification()