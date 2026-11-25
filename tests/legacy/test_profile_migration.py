from pathlib import Path
import sys
import json

PROJECT_DIR = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(PROJECT_DIR))

from profiles.profile_manager import migrate_profile

GAME = "Pokemon FireRed Rev 1"

PROFILES = [
    ("FireRed Starter", "Charmander", "CHRIS", "004"),
    ("FireRed ASH Bulbasaur", "Bulbasaur", "ASH", "001"),
    ("FireRed ASH Squirtle", "Squirtle", "ASH", "007")
]

for profile_name, starter, trainer, species in PROFILES:
    profile_dir = PROJECT_DIR / "saves" / profile_name
    save_path = profile_dir / "game.sav"

    original_save = save_path.read_bytes()

    metadata_path = migrate_profile(
        profile_name,
        GAME,
        starter,
        trainer
    )

    with metadata_path.open("r", encoding="utf-8") as file:
        metadata = json.load(file)

    assert metadata["name"] == profile_name
    assert metadata["trainer_name"] == trainer
    assert metadata["target_name"] == starter
    assert metadata["target_species"] == species
    assert (PROJECT_DIR / metadata["rom_path"]).is_file()
    assert save_path.read_bytes() == original_save

    print(json.dumps(metadata, indent=4))
    print("Permanent save unchanged: True")
    print("Migration: PASS\n")

print("All profile migrations passed.")