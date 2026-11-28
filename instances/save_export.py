from pathlib import Path
import gc

from instances.save_validator import validate_battery_save

PROJECT_DIR = Path(__file__).resolve().parents[1]

# Exports and verifies the battery save from a completed manual takeover.
def export_battery_save(takeover, destination):
    if takeover.active:
        raise RuntimeError("Stop manual gameplay before exporting.")

    instance = takeover.instance
    source = instance.save_path.resolve()
    destination = Path(destination).resolve()

    if destination.suffix.lower() != ".sav":
        raise ValueError("Export destination must be a .sav file.")

    # Prevent exports into directories containing protected application data.
    protected_directories = (
        (PROJECT_DIR / "saves").resolve(),
        (PROJECT_DIR / "temp").resolve(),
        (PROJECT_DIR / "roms").resolve()
    )

    for directory in protected_directories:
        if destination.is_relative_to(directory):
            raise ValueError("Cannot export into a protected directory.")

    if destination.exists():
        raise FileExistsError("An exported save already exists at this location.")
    if not source.is_file():
        raise FileNotFoundError("Temporary battery save not found.")

    destination.parent.mkdir(parents=True, exist_ok=True)

    # Release native emulator resources to flush battery save data.
    instance.core = None
    gc.collect()
    instance.screen = None

    save_data = source.read_bytes()
    validate_battery_save(save_data, instance.game)
    created = False

    # Create the export without overwriting an existing file.
    try:
        with destination.open("xb") as file:
            created = True
            file.write(save_data)

        # Verify that the exported save matches the temporary save.
        if destination.read_bytes() != save_data:
            raise IOError("Exported battery save verification failed.")

    except Exception:
        # Remove incomplete exports while preserving the temporary save.
        if created:
            destination.unlink(missing_ok=True)
        raise

    print(f"[{instance.instance_id}] Battery save exported.")
    print("Export destination:", destination)
    print("Export size:", len(save_data))
    return destination