from pathlib import Path
import sys
import json

PROJECT_DIR = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(PROJECT_DIR))

from profiles.profile_manager import (
    generate_profile_name,
    generate_profile_metadata
)

GAME = "Pokemon FireRed Rev 1"
TRAINER_NAME = "ASH"

starters = {
    "Bulbasaur": "001",
    "Charmander": "004",
    "Squirtle": "007"
}

for starter, species in starters.items():
    name = generate_profile_name(
        GAME, starter, TRAINER_NAME
    )

    metadata = generate_profile_metadata(
        GAME, starter, TRAINER_NAME
    )

    assert name == f"FireRed ASH {starter}"
    assert metadata["name"] == name
    assert metadata["target_species"] == species
    assert metadata["target_name"] == starter
    assert metadata["trainer_name"] == TRAINER_NAME
    assert (PROJECT_DIR / metadata["rom_path"]).is_file()

    print(json.dumps(metadata, indent=4))
    print("PASS\n")

print("All profile generation tests passed.")