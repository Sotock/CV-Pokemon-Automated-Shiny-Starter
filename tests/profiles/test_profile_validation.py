from pathlib import Path
import sys
import json
from tempfile import TemporaryDirectory
from unittest.mock import patch

PROJECT_DIR = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(PROJECT_DIR))

from profiles import profile_manager
from profiles.profile_manager import (
    load_profile,
    create_profile
)


PROFILE_NAME = "FireRed Starter"

SAVES_DIR = PROJECT_DIR / "saves"

SOURCE_SAVE = (
        SAVES_DIR / PROFILE_NAME / "game.sav"
)

SOURCE_METADATA = (
        SAVES_DIR / PROFILE_NAME / "profile.json"
)


def test_profile_validation():

    print("\n--- Profile Validation ---")

    assert SOURCE_SAVE.is_file()
    assert SOURCE_METADATA.is_file()

    original_save = SOURCE_SAVE.read_bytes()
    original_metadata = SOURCE_METADATA.read_bytes()

    profile = load_profile(PROFILE_NAME)

    assert profile["name"] == PROFILE_NAME

    print("Existing profile loading: PASS")
    print("Profile:", profile["name"])
    print("Game:", profile["game"])
    print("Trainer:", profile["trainer_name"])
    print("Target:", profile["target_name"])
    print("Species:", profile["target_species"])

    with TemporaryDirectory() as directory:

        temporary_saves = Path(directory)

        with patch.object(
                profile_manager,
                "SAVES_DIR",
                temporary_saves
        ):

            metadata_path = create_profile(
                profile["game"],
                profile["target_name"],
                "VALIDATION",
                SOURCE_SAVE
            )

            with metadata_path.open(
                    "r",
                    encoding="utf-8"
            ) as file:

                metadata = json.load(file)

            test_profile_name = metadata["name"]

            test_save = (
                    metadata_path.parent / "game.sav"
            )

            assert test_save.is_file()
            assert test_save.read_bytes() == original_save

            loaded = load_profile(test_profile_name)

            assert loaded == metadata

            print("\n--- Profile Creation ---")
            print("New profile creation: PASS")
            print("Copied save verification: PASS")

            try:

                create_profile(
                    profile["game"],
                    profile["target_name"],
                    "VALIDATION",
                    SOURCE_SAVE
                )

            except FileExistsError:

                print("Duplicate profile rejection: PASS")

            else:

                raise AssertionError(
                    "Duplicate profile was accepted."
                )

            invalid_configurations = [
                (
                    "target_species",
                    "999",
                    "Incorrect species ID"
                ),
                (
                    "macro",
                    "macros.invalid_macro",
                    "Invalid macro"
                ),
                (
                    "vision_config",
                    "invalid_configuration",
                    "Invalid vision configuration"
                ),
                (
                    "emulator",
                    "Unsupported Emulator",
                    "Unsupported emulator"
                ),
                (
                    "rom_path",
                    "roms/invalid.gba",
                    "Invalid ROM path"
                ),
                (
                    "game",
                    "Unsupported Game",
                    "Unsupported game"
                ),
                (
                    "target_name",
                    "Unsupported Starter",
                    "Unsupported starter"
                )
            ]

            print("\n--- Invalid Configuration Testing ---")

            for field, value, description in (
                    invalid_configurations
            ):

                modified = metadata.copy()
                modified[field] = value

                with metadata_path.open(
                        "w",
                        encoding="utf-8"
                ) as file:

                    json.dump(
                        modified,
                        file,
                        indent=4
                    )

                try:

                    load_profile(test_profile_name)

                except (ValueError, KeyError, FileNotFoundError):

                    print(f"{description} rejection: PASS")

                else:

                    raise AssertionError(
                        f"{description} was accepted."
                    )

            print("\n--- Missing Metadata Testing ---")

            modified = metadata.copy()
            del modified["target_species"]

            with metadata_path.open(
                    "w",
                    encoding="utf-8"
            ) as file:

                json.dump(
                    modified,
                    file,
                    indent=4
                )

            try:

                load_profile(test_profile_name)

            except ValueError:

                print("Missing metadata field rejection: PASS")

            else:

                raise AssertionError(
                    "Incomplete metadata was accepted."
                )

            # Restore valid temporary metadata
            with metadata_path.open(
                    "w",
                    encoding="utf-8"
            ) as file:

                json.dump(
                    metadata,
                    file,
                    indent=4
                )

            assert load_profile(test_profile_name) == metadata

            assert test_save.read_bytes() == original_save

            print("Restored profile validation: PASS")
            print("Temporary save preservation: PASS")

    assert not temporary_saves.exists()

    assert SOURCE_SAVE.read_bytes() == original_save

    assert SOURCE_METADATA.read_bytes() == original_metadata

    print("\n--- Resource and Save Preservation ---")
    print("Temporary directory cleanup: PASS")
    print("Permanent save preservation: PASS")
    print("Permanent metadata preservation: PASS")

    print("\nAll profile validation tests passed.")


if __name__ == "__main__":

    test_profile_validation()