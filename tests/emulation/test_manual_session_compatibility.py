from pathlib import Path
import sys
from tempfile import TemporaryDirectory
from unittest.mock import patch

PROJECT_DIR = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(PROJECT_DIR))

from instances.manual_session import ManualSession
from profiles import profile_manager
from profiles.profile_manager import (
    create_profile,
    load_profile
)


PROFILE_NAME = "FireRed Starter"


def test_manual_session_compatibility():

    profile_dir = (
            PROJECT_DIR / "saves" / PROFILE_NAME
    )

    source_save = profile_dir / "game.sav"
    source_metadata = profile_dir / "profile.json"

    original_save = source_save.read_bytes()
    original_metadata = source_metadata.read_bytes()

    profile = load_profile(PROFILE_NAME)

    game = profile["game"]
    starter = profile["target_name"]
    trainer = profile["trainer_name"]

    print("\n--- Manual Session Compatibility ---")

    with TemporaryDirectory(
            dir=PROJECT_DIR / "temp"
    ) as directory:

        temporary_saves = Path(directory)

        with patch.object(
                profile_manager,
                "SAVES_DIR",
                temporary_saves
        ):

            metadata_path = create_profile(
                game,
                starter,
                trainer,
                source_save
            )

            base_name = metadata_path.parent.name

            existing_metadata = metadata_path.read_bytes()

            existing_save = (
                    metadata_path.parent / "game.sav"
            )

            session = ManualSession(
                game,
                starter,
                trainer
            )

            instance_dir = session.instance_dir

            try:

                assert (
                        session.profile_name
                        == f"{base_name} (2)"
                )

                assert (
                        session.metadata["name"]
                        == session.profile_name
                )

                print("Duplicate session initialization: PASS")
                print("Generated profile:", session.profile_name)

                original_core_id = id(session.core)

                try:

                    session.finalize()

                except ValueError as error:

                    print("Blank save rejection: PASS")
                    print("Reason:", error)

                else:

                    raise AssertionError(
                        "Blank save finalization was accepted."
                    )

                assert session.core is not None

                assert id(session.core) == original_core_id

                assert not session.finalized

                print("Emulator preservation: PASS")

                for _ in range(120):

                    session.run_frame()

                frame = session.get_frame()

                assert frame.size == (240, 160)

                print("Continued frame advancement: PASS")
                print("Framebuffer retrieval: PASS")

                assert not (
                        temporary_saves / session.profile_name
                ).exists()

                print("Premature profile creation prevented: PASS")

            finally:

                session.close()

            assert not instance_dir.exists()

            assert (
                    existing_save.read_bytes()
                    == original_save
            )

            assert (
                    metadata_path.read_bytes()
                    == existing_metadata
            )

            print("Cancelled session cleanup: PASS")
            print("Existing profile preservation: PASS")

    assert not temporary_saves.exists()

    assert source_save.read_bytes() == original_save
    assert source_metadata.read_bytes() == original_metadata

    print("Experimental directory cleanup: PASS")
    print("Permanent save unchanged: True")
    print("Permanent metadata unchanged: True")

    print("\nManual session compatibility: PASS")


if __name__ == "__main__":

    test_manual_session_compatibility()