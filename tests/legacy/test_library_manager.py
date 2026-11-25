from pathlib import Path

from instances.library_manager import LibraryInstance

PROJECT_DIR = Path(__file__).resolve().parents[2]
PROFILE_NAME = "FireRed Starter"

PERMANENT_SAVE = (
        PROJECT_DIR / "saves" / PROFILE_NAME / "game.sav"
)

original_save = PERMANENT_SAVE.read_bytes()

instance = LibraryInstance(PROFILE_NAME)

try:
    print("Instance ID:", instance.instance_id)
    print("Directory created:", instance.instance_dir.exists())
    print("Temporary ROM exists:", instance.rom_path.is_file())
    print("Temporary save exists:", instance.save_path.is_file())
    print("Emulator initialized:", instance.core is not None)
    print("Framebuffer initialized:", instance.screen is not None)

    # Execute five hunting attempts
    for attempt in range(5):
        screenshot = instance.run_attempt()

        print("Screenshot captured:", screenshot.is_file())

    print("Total attempts:", instance.attempts)

finally:
    instance.close()

print("Directory removed:", not instance.instance_dir.exists())
print("Permanent save exists:", PERMANENT_SAVE.is_file())
print("Permanent save unchanged:",
      PERMANENT_SAVE.read_bytes() == original_save)