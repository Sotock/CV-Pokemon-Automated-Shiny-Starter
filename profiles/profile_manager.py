import json
import shutil
from pathlib import Path
from profiles.game_registry import get_game_config, get_target_species

PROJECT_DIR = Path(__file__).resolve().parent.parent
SAVES_DIR = PROJECT_DIR / "saves"

# Validates profile names against Windows directory naming restrictions.
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

# Copies an existing battery save into a new permanent profile directory.
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

    # Remove the incomplete profile if copying fails.
    try:
        shutil.copy2(save_path, destination)
    except Exception:
        shutil.rmtree(profile_dir)
        raise

    return destination

# Registers an imported save using the original FireRed profile format.
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

# Generates a profile name from the game, trainer, and selected starter.
def generate_profile_name(game, starter, trainer_name):
    config = get_game_config(game)
    get_target_species(game, starter)

    if not isinstance(trainer_name, str):
        raise ValueError("Trainer name must be a string.")

    trainer_name = trainer_name.strip()
    if not trainer_name:
        raise ValueError("Trainer name cannot be empty.")

    profile_name = f"{config['short_name']} {trainer_name} {starter}"
    validate_profile_name(profile_name)
    return profile_name

# Appends a numerical suffix when the generated profile name already exists.
def generate_unique_profile_name(game, starter, trainer_name):
    base_name = generate_profile_name(game, starter, trainer_name)
    profile_name = base_name
    counter = 2

    while (SAVES_DIR / profile_name).exists():
        profile_name = f"{base_name} ({counter})"
        counter += 1

    return profile_name

# Generates profile metadata using the registered game configuration.
def generate_profile_metadata(game, starter, trainer_name):
    profile_name = generate_profile_name(game, starter, trainer_name)
    config = get_game_config(game)
    species = get_target_species(game, starter)

    return {
        "name": profile_name,
        "game": game,
        "emulator": config["emulator"],
        "rom_path": config["rom_path"],
        "save_file": "game.sav",
        "trainer_name": trainer_name.strip(),
        "target_name": starter,
        "target_species": species,
        "macro": config["macro"],
        "vision_config": config["vision_config"]
    }

# Creates a permanent profile containing a prepared save and its metadata.
def create_profile(game, starter, trainer_name, save_path):
    metadata = generate_profile_metadata(game, starter, trainer_name)
    rom_path = PROJECT_DIR / metadata["rom_path"]

    if not rom_path.is_file():
        raise FileNotFoundError("Game ROM not found.")

    profile_name = generate_unique_profile_name(game, starter, trainer_name)
    metadata["name"] = profile_name
    destination = import_save(save_path, profile_name)
    metadata_path = destination.parent / "profile.json"

    # Remove the incomplete profile if metadata creation fails.
    try:
        with metadata_path.open("w", encoding="utf-8") as file:
            json.dump(metadata, file, indent=4)
    except Exception:
        shutil.rmtree(destination.parent)
        raise

    return metadata_path

# Updates an existing profile to the current metadata format.
def migrate_profile(profile_name, game, starter, trainer_name):
    validate_profile_name(profile_name)
    profile_dir = SAVES_DIR / profile_name
    save_path = profile_dir / "game.sav"
    metadata_path = profile_dir / "profile.json"

    if not save_path.is_file():
        raise FileNotFoundError("Profile save file not found.")
    if not metadata_path.is_file():
        raise FileNotFoundError("Profile metadata not found.")

    metadata = generate_profile_metadata(game, starter, trainer_name)
    rom_path = PROJECT_DIR / metadata["rom_path"]
    if not rom_path.is_file():
        raise FileNotFoundError("Game ROM not found.")

    # Preserve the existing profile name and directory.
    metadata["name"] = profile_name

    # Write the updated metadata before replacing the original file.
    temporary_path = profile_dir / "profile.json.tmp"
    with temporary_path.open("w", encoding="utf-8") as file:
        json.dump(metadata, file, indent=4)

    temporary_path.replace(metadata_path)
    return metadata_path

# Loads a permanent profile and validates its configuration and files.
def load_profile(profile_name):
    validate_profile_name(profile_name)
    profile_dir = SAVES_DIR / profile_name
    metadata_path = profile_dir / "profile.json"

    if not metadata_path.is_file():
        raise FileNotFoundError("Profile metadata not found.")

    with metadata_path.open("r", encoding="utf-8") as file:
        profile = json.load(file)

    required_fields = {
        "name",
        "game",
        "emulator",
        "rom_path",
        "save_file",
        "trainer_name",
        "target_name",
        "target_species",
        "macro",
        "vision_config"
    }

    if not isinstance(profile, dict):
        raise ValueError("Invalid profile metadata.")

    missing_fields = required_fields - profile.keys()
    if missing_fields:
        raise ValueError(f"Missing profile fields: {sorted(missing_fields)}")

    # Compare stored metadata against the registered game configuration.
    expected = generate_profile_metadata(
        profile["game"],
        profile["target_name"],
        profile["trainer_name"]
    )

    if profile["name"] != profile_name:
        raise ValueError("Profile name mismatch.")

    for field in required_fields - {"name"}:
        if profile[field] != expected[field]:
            raise ValueError(f"Invalid profile configuration: {field}")

    rom_path = PROJECT_DIR / profile["rom_path"]
    save_path = profile_dir / profile["save_file"]

    if not rom_path.is_file():
        raise FileNotFoundError("Profile ROM not found.")
    if not save_path.is_file():
        raise FileNotFoundError("Profile save not found.")

    return profile