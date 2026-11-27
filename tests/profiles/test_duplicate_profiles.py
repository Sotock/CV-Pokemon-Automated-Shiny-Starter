from pathlib import Path
import sys
from tempfile import TemporaryDirectory
from unittest.mock import patch
import shutil

PROJECT_DIR = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(PROJECT_DIR))

from profiles.profile_manager import (
    generate_profile_name,
    generate_unique_profile_name,
    create_profile,
    import_save,
    load_profile
)


PROFILE_NAME = "FireRed Starter"


def test_duplicate_profiles():

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

    base_name = generate_profile_name(
        game,
        starter,
        trainer
    )

    print("\n--- Duplicate Profile Verification ---")

    with TemporaryDirectory(
            dir=PROJECT_DIR / "temp"
    ) as temporary_dir:

        test_saves = Path(temporary_dir)

        with patch(
                "profiles.profile_manager.SAVES_DIR",
                test_saves
        ):

            assert generate_unique_profile_name(
                game,
                starter,
                trainer
            ) == base_name

            print("Initial profile naming: PASS")

            created_profiles = {}

            for number in range(1, 5):

                expected_name = (
                    base_name
                    if number == 1
                    else f"{base_name} ({number})"
                )

                generated_name = (
                    generate_unique_profile_name(
                        game,
                        starter,
                        trainer
                    )
                )

                assert generated_name == expected_name

                metadata_path = create_profile(
                    game,
                    starter,
                    trainer,
                    source_save
                )

                assert (
                        metadata_path.parent.name
                        == expected_name
                )

                loaded_profile = load_profile(
                    expected_name
                )

                assert (
                        loaded_profile["name"]
                        == expected_name
                )

                assert loaded_profile["game"] == game
                assert loaded_profile["target_name"] == starter
                assert loaded_profile["trainer_name"] == trainer

                created_save = (
                        metadata_path.parent / "game.sav"
                )

                assert (
                        created_save.read_bytes()
                        == original_save
                )

                created_profiles[expected_name] = {
                    "save": created_save.read_bytes(),
                    "metadata": metadata_path.read_bytes()
                }

                print(
                    f"Created and validated: "
                    f"{expected_name}"
                )

            print("\nAutomatic duplicate numbering: PASS")
            print("Numbered profile loading: PASS")

            # Verify that previous profiles were
            # not modified by subsequent creation.

            for name, contents in created_profiles.items():

                directory = test_saves / name

                assert (
                        (directory / "game.sav").read_bytes()
                        == contents["save"]
                )

                assert (
                        (directory / "profile.json").read_bytes()
                        == contents["metadata"]
                )

            print("Existing profile preservation: PASS")

            # Direct imports must still reject overwriting.

            try:

                import_save(
                    source_save,
                    base_name
                )

            except FileExistsError:

                print("Direct overwrite rejection: PASS")

            else:

                raise AssertionError(
                    "Existing profile overwrite was allowed."
                )

            # Remove only an experimental profile
            # to verify available suffix reuse.

            removed_name = f"{base_name} (2)"

            shutil.rmtree(
                test_saves / removed_name
            )

            assert generate_unique_profile_name(
                game,
                starter,
                trainer
            ) == removed_name

            print("Available suffix reuse: PASS")

            recreated_metadata = create_profile(
                game,
                starter,
                trainer,
                source_save
            )

            assert (
                    recreated_metadata.parent.name
                    == removed_name
            )

            assert (
                    load_profile(removed_name)["name"]
                    == removed_name
            )

            print("Numbered profile recreation: PASS")

            # Base naming must remain deterministic.

            assert generate_profile_name(
                game,
                starter,
                trainer
            ) == base_name

            print("Deterministic base naming: PASS")

            assert len(
                list(test_saves.iterdir())
            ) == 4

            print("Independent profile directories: PASS")

    assert not test_saves.exists()

    assert source_save.read_bytes() == original_save

    assert source_metadata.read_bytes() == original_metadata

    print("\nExperimental profile cleanup: PASS")
    print("Permanent save unchanged: True")
    print("Permanent metadata unchanged: True")

    print("\nDuplicate profile verification: PASS")


if __name__ == "__main__":

    test_duplicate_profiles()