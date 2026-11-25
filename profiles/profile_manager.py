from pathlib import Path
import shutil
import json

PROJECT_DIR = Path(__file__).resolve().parent.parent
SAVES_DIR = PROJECT_DIR / "saves"

def validate_profile_name(profile_name):
    if not isinstance(profile_name, str) or not profile_name.strip():
        raise ValueError("Profile name cannot be empty.")

    if profile_name != profile_name.strip():
        raise ValueError("Profile name cannot begin or end with spaces.")

    invalid_characters = '<>:"/\\|?*'

    if any(char in profile_name for char in invalid_characters):
        raise ValueError("Profile name contains invalid characters.")

    if profile_name.endswith("."):
        raise ValueError("Profile name cannot end with a period.")

    if any(ord(char) < 32 for char in profile_name):
        raise ValueError("Profile name contains invalid control characters.")

    reserved_names = {
        "CON", "PRN", "AUX", "NUL",
        *(f"COM{i}" for i in range(1, 10)),
        *(f"LPT{i}" for i in range(1, 10))
    }

    if profile_name.split(".")[0].upper() in reserved_names:
        raise ValueError("Profile name is reserved by Windows.")

def import_save(save_path, profile_name):
    validate_profile_name(profile_name)

    save_path = Path(save_path)

    if not save_path.is_file():
        raise FileNotFoundError("Save file not found.")

    if save_path.suffix.lower() != ".sav":
        raise ValueError("Selected file must be a .sav file.")

    profile_dir = SAVES_DIR / profile_name

    if profile_dir.exists():
        raise FileExistsError("A profile with this name already exists.")

    profile_dir.mkdir(parents=True)
    destination = profile_dir / "game.sav"

    shutil.copy2(save_path, destination)

    return destination

def register_profile(profile_name, rom_path):
    validate_profile_name(profile_name)

    profile_dir = SAVES_DIR / profile_name
    save_path = profile_dir / "game.sav"
    rom_path = Path(rom_path)

    if not save_path.is_file():
        raise FileNotFoundError("Profile save file not found.")

    if not rom_path.is_file():
        raise FileNotFoundError("ROM file not found.")

    if rom_path.suffix.lower() != ".gba":
        raise ValueError("Selected ROM must be a .gba file.")

    profile_data = {
        "name": profile_name,
        "game": "Pokemon FireRed Rev 1",
        "emulator": "mGBA",
        "rom_path": str(rom_path),
        "save_file": "game.sav"
    }

    metadata_path = profile_dir / "profile.json"

    with metadata_path.open("w", encoding="utf-8") as file:
        json.dump(profile_data, file, indent=4)

    return metadata_path