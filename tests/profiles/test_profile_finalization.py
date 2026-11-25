from pathlib import Path
import json

from profiles.profile_manager import import_save, register_profile


PROJECT_DIR = Path(__file__).resolve().parents[2]

ROM_NAME = "Pokemon - FireRed Version (USA, Europe) (Rev 1).gba"

SOURCE_ROM = PROJECT_DIR / "roms" / ROM_NAME

PREPARED_SAVE = (
        PROJECT_DIR / "temp" / "fresh_save_test"
        / Path(ROM_NAME).with_suffix(".sav")
)

PROFILE_NAME = "FireRed ASH Squirtle"


# Verify prepared files

if not SOURCE_ROM.is_file():
    raise FileNotFoundError("Original ROM not found.")

if not PREPARED_SAVE.is_file():
    raise FileNotFoundError("Prepared save not found.")

original_save = PREPARED_SAVE.read_bytes()

if len(original_save) != 131072:
    raise ValueError("Unexpected FireRed save size.")

if original_save == b"\xff" * 131072:
    raise ValueError("Prepared save is blank.")

print("Prepared save verified.")
print("Save size:", len(original_save))


# Finalize permanent profile

imported_save = import_save(
    PREPARED_SAVE,
    PROFILE_NAME
)

metadata_path = register_profile(
    PROFILE_NAME,
    SOURCE_ROM
)


# Verify finalized profile

with metadata_path.open("r", encoding="utf-8") as file:
    metadata = json.load(file)

print()
print("--- Profile Finalization Results ---")
print("Profile name:", PROFILE_NAME)
print("Permanent save exists:", imported_save.is_file())
print("Profile metadata exists:", metadata_path.is_file())

print(
    "Permanent save matches prepared save:",
    imported_save.read_bytes() == original_save
)

print(
    "Prepared save unchanged:",
    PREPARED_SAVE.read_bytes() == original_save
)

print(
    "Registered ROM correct:",
    Path(metadata["rom_path"]) == SOURCE_ROM
)

print()
print("Profile metadata:")
print(json.dumps(metadata, indent=4))

print()
print("Profile finalization completed.")