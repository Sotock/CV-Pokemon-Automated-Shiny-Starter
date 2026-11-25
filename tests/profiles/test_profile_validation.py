from pathlib import Path
import sys
import json
from tempfile import TemporaryDirectory
from unittest.mock import patch

PROJECT_DIR = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(PROJECT_DIR))

from profiles import profile_manager as pm

GAME = "Pokemon FireRed Rev 1"

PROFILES = [
    "FireRed Starter",
    "FireRed ASH Bulbasaur",
    "FireRed ASH Squirtle"
]

# Validate existing profiles
for profile_name in PROFILES:
    profile = pm.load_profile(profile_name)

    print(f"{profile_name}: PASS")

# Test creation and invalid configurations
# without modifying permanent profiles
source_save = (
        PROJECT_DIR / "saves" /
        "FireRed ASH Bulbasaur" / "game.sav"
)

original_save = source_save.read_bytes()

with TemporaryDirectory() as temp_dir:
    with patch.object(pm, "SAVES_DIR", Path(temp_dir)):

        metadata_path = pm.create_profile(
            GAME, "Bulbasaur", "ASH", source_save
        )

        profile_name = "FireRed ASH Bulbasaur"
        original = pm.load_profile(profile_name)

        assert (
                       metadata_path.parent / "game.sav"
               ).read_bytes() == original_save

        print("New profile creation: PASS")

        try:
            pm.create_profile(
                GAME, "Bulbasaur", "ASH", source_save
            )
        except FileExistsError:
            print("Duplicate profile rejection: PASS")
        else:
            raise AssertionError("Duplicate profile accepted.")

        invalid_fields = {
            "target_species": "004",
            "macro": "invalid_macro",
            "vision_config": "invalid_config",
            "emulator": "invalid_emulator",
            "rom_path": "invalid_rom.gba",
            "game": "Unsupported Game",
            "target_name": "Pikachu"
        }

        for field, value in invalid_fields.items():
            modified = original.copy()
            modified[field] = value

            metadata_path.write_text(
                json.dumps(modified, indent=4),
                encoding="utf-8"
            )

            try:
                pm.load_profile(profile_name)
            except ValueError:
                print(f"Invalid {field} rejection: PASS")
            else:
                raise AssertionError(
                    f"Invalid {field} accepted."
                )

        modified = original.copy()
        del modified["target_species"]

        metadata_path.write_text(
            json.dumps(modified, indent=4),
            encoding="utf-8"
        )

        try:
            pm.load_profile(profile_name)
        except ValueError:
            print("Missing field rejection: PASS")
        else:
            raise AssertionError("Incomplete profile accepted.")

assert source_save.read_bytes() == original_save

print("Permanent save unchanged: True")
print("\nAll profile validation tests passed.")