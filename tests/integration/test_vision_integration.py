from pathlib import Path
import sys
from time import perf_counter

PROJECT_DIR = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(PROJECT_DIR))

import cv2

from instances.library_manager import LibraryInstance


PROFILES = [
    "FireRed TEST Bulbasaur",
    "FireRed Starter",
    "FireRed ASH Squirtle"
]


def test_vision_integration():

    for profile_name in PROFILES:

        save_path = (
                PROJECT_DIR / "saves"
                / profile_name / "game.sav"
        )

        original_save = save_path.read_bytes()

        instance = LibraryInstance(profile_name)
        instance_dir = instance.instance_dir

        try:
            print(f"\n--- {profile_name} ---")
            print("Target species:", instance.target_species)
            print("Vision configuration:", instance.vision_config)

            screenshot, result = (
                instance.run_classified_attempt()
            )

            assert screenshot.is_file()

            # Compare live framebuffer classification
            # against the saved screenshot
            image = cv2.imread(str(screenshot))

            assert image is not None

            disk_result = instance.detector.predict(
                image,
                instance.target_species
            )

            assert result == disk_result

            assert 0 <= result["votes"] <= 3

            assert result["is_shiny"] == (
                    result["votes"] >= 2
            )

            print("Live and saved classification match: PASS")
            print("Majority voting: PASS")

            # Measure repeated framebuffer inference
            start = perf_counter()

            for _ in range(100):
                instance.classify_frame()

            elapsed = perf_counter() - start

            print(
                f"Average framebuffer classification time: "
                f"{elapsed * 1000 / 100:.4f} ms"
            )

            print("Screenshot:", screenshot)
            print("Vision integration: PASS")

        finally:
            instance.close()

        assert not instance_dir.exists()
        assert save_path.read_bytes() == original_save

        print("Temporary instance cleanup: PASS")
        print("Permanent save unchanged: True")


if __name__ == "__main__":

    test_vision_integration()

    print("\nAll vision integration tests passed.")