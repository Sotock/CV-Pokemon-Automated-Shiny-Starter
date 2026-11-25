from pathlib import Path
import sys

PROJECT_DIR = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(PROJECT_DIR))

from instances.library_manager import LibraryInstance

PROFILES = [
    ("FireRed Starter", "Charmander", "004"),
    ("FireRed ASH Bulbasaur", "Bulbasaur", "001"),
    ("FireRed ASH Squirtle", "Squirtle", "007")
]

for profile_name, target, species in PROFILES:
    save_path = PROJECT_DIR / "saves" / profile_name / "game.sav"
    original_save = save_path.read_bytes()

    instance = LibraryInstance(profile_name)
    instance_dir = instance.instance_dir

    try:
        print(f"\nProfile: {profile_name}")
        print("Game:", instance.game)
        print("Emulator:", instance.emulator)
        print("Trainer:", instance.trainer_name)
        print("Target:", instance.target_name)
        print("Species:", instance.target_species)
        print("Vision configuration:", instance.vision_config)
        print("Macro:", instance.run_macro.__module__)

        assert instance.target_name == target
        assert instance.target_species == species
        assert instance.vision_config == "firered_leafgreen"

        assert (
                instance.run_macro.__module__
                == "macros.firered_main_macro"
        )

        screenshot = instance.run_attempt()

        assert screenshot.is_file()

        print("Screenshot:", screenshot)
        print("Instance configuration: PASS")

    finally:
        instance.close()

    assert not instance_dir.exists()
    assert save_path.read_bytes() == original_save

    print("Instance cleanup: PASS")
    print("Permanent save unchanged: True")

print("\nAll profile-driven instance tests passed.")