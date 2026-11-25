from pathlib import Path
import shutil
import uuid
import subprocess
import json

PROJECT_DIR = Path(__file__).resolve().parent.parent
TEMP_DIR = PROJECT_DIR / "temp"
MGBA_PATH = PROJECT_DIR / "emulators" / "mGBA" / "mGBA.exe"

def create_instance():
    instance_id = uuid.uuid4().hex[:8]
    instance_dir = TEMP_DIR / instance_id
    instance_dir.mkdir(parents=True, exist_ok=False)

    return instance_id, instance_dir


def remove_instance(instance_dir):
    shutil.rmtree(instance_dir)

def launch_instance(profile_name):
    profile_dir = PROJECT_DIR / "saves" / profile_name
    metadata_path = profile_dir / "profile.json"

    with metadata_path.open("r", encoding="utf-8") as file:
        profile = json.load(file)

    source_rom = Path(profile["rom_path"])
    source_save = profile_dir / profile["save_file"]

    if not source_rom.is_file():
        raise FileNotFoundError("Profile ROM not found.")

    if not source_save.is_file():
        raise FileNotFoundError("Profile save not found.")

    instance_id, instance_dir = create_instance()

    try:
        instance_rom = instance_dir / source_rom.name
        instance_save = instance_rom.with_suffix(".sav")

        shutil.copy2(source_rom, instance_rom)
        shutil.copy2(source_save, instance_save)

        process = subprocess.Popen([MGBA_PATH, str(instance_rom)], cwd=PROJECT_DIR)

    except Exception:
        remove_instance(instance_dir)
        raise

    return instance_id, instance_dir, process