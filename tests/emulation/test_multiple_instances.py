from pathlib import Path
from concurrent.futures import ThreadPoolExecutor

from instances.library_manager import LibraryInstance

PROJECT_DIR = Path(__file__).resolve().parents[2]
PROFILE_NAME = "FireRed ASH Squirtle"
INSTANCE_COUNT = 2
ATTEMPTS = 10

PERMANENT_SAVE = (
        PROJECT_DIR / "saves" / PROFILE_NAME / "game.sav"
)

original_save = PERMANENT_SAVE.read_bytes()


def run_instance(instance_number):
    instance = LibraryInstance(PROFILE_NAME)

    try:
        print(f"Worker {instance_number}: {instance.instance_id}")

        for _ in range(ATTEMPTS):
            screenshot = instance.run_attempt()

            print(
                f"[{instance.instance_id}] "
                f"Screenshot captured: {screenshot.is_file()}"
            )

        print(
            f"[{instance.instance_id}] "
            f"Total attempts: {instance.attempts}"
        )

    finally:
        instance.close()

    return {
        "instance_id": instance.instance_id,
        "attempts": instance.attempts,
        "directory_removed": not instance.instance_dir.exists()
    }


with ThreadPoolExecutor(max_workers=INSTANCE_COUNT) as executor:
    results = list(
        executor.map(run_instance, range(1, INSTANCE_COUNT + 1))
    )

print("\n--- Multi-instance results ---")

for result in results:
    print("Instance ID:", result["instance_id"])
    print("Total attempts:", result["attempts"])
    print("Directory removed:", result["directory_removed"])
    print()

print("Unique instance IDs:",
      len({r["instance_id"] for r in results}) == INSTANCE_COUNT)

print("Total attempts:", sum(r["attempts"] for r in results))

print("Permanent save unchanged:",
      PERMANENT_SAVE.read_bytes() == original_save)