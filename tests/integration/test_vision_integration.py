from pathlib import Path
import sys
from time import perf_counter

PROJECT_DIR = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(PROJECT_DIR))

import cv2

from instances.library_manager import LibraryInstance
from vision.shiny_detector import ShinyDetector


PROFILES = [
    "FireRed TEST Bulbasaur",
    "FireRed Starter",
    "FireRed ASH Squirtle"
]

PICTURE_DIR = PROJECT_DIR / "pictures"

INSTANCE_GROUPS = {
    "001": [
        "9766050e",
        "8b5a91b9",
        "5e7ec5a9",
        "9e49cd72",
        "aad18bbd",
        "d7eb9ff8",
        "34b4b840",
        "a7f7c06c",
        "d57856d2",
        "1cc51cb6"
    ],
    "004": [
        "ad5a774d",
        "2dae7405"
    ],
    "007": [
        "6d888776",
        "7d2d16ba"
    ]
}

SPECIES_NAMES = {
    "001": "Bulbasaur",
    "004": "Charmander",
    "007": "Squirtle"
}

EXPECTED_COUNTS = {
    "001": 100,
    "004": 20,
    "007": 20
}


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

    print("\nAll vision integration tests passed.")


def test_bulk_encounter_validation():

    detector = ShinyDetector("firered_leafgreen")

    total = 0
    accepted = 0
    rejected = 0
    normal_predictions = 0
    shiny_predictions = 0
    wrong_species_rejected = 0
    wrong_species_total = 0

    validation_times = []
    classification_times = []

    print("\n--- Prior Encounter Validation ---")

    for species, instance_ids in INSTANCE_GROUPS.items():

        species_total = 0
        species_accepted = 0
        species_normal = 0
        species_shiny = 0

        print(f"\n--- {SPECIES_NAMES[species]} ---")

        for instance_id in instance_ids:

            instance_dir = PICTURE_DIR / instance_id

            assert instance_dir.is_dir(), (
                f"Missing instance directory: {instance_id}"
            )

            paths = sorted(
                instance_dir.glob("attempt_*.png")
            )

            assert len(paths) == 10, (
                f"Unexpected capture count: {instance_id}"
            )

            for path in paths:

                image = cv2.imread(str(path))

                assert image is not None, (
                    f"Unable to load {path}"
                )

                total += 1
                species_total += 1

                start = perf_counter()

                valid = detector.validate_summary(
                    image,
                    species
                )

                validation_times.append(
                    perf_counter() - start
                )

                if not valid:

                    rejected += 1

                    print(
                        f"REJECTED: "
                        f"{instance_id}/{path.name}"
                    )

                    continue

                accepted += 1
                species_accepted += 1

                # Classify accepted encounters
                start = perf_counter()

                result = detector.predict(
                    image,
                    species
                )

                classification_times.append(
                    perf_counter() - start
                )

                if result["is_shiny"]:

                    shiny_predictions += 1
                    species_shiny += 1

                    print(
                        f"SHINY PREDICTION: "
                        f"{instance_id}/{path.name}"
                    )

                else:

                    normal_predictions += 1
                    species_normal += 1

                # Test rejection of incorrect species
                for wrong_species in SPECIES_NAMES:

                    if wrong_species == species:
                        continue

                    wrong_species_total += 1

                    wrong_valid = detector.validate_summary(
                        image,
                        wrong_species
                    )

                    if not wrong_valid:

                        wrong_species_rejected += 1

                    else:

                        print(
                            f"INCORRECT SPECIES ACCEPTED: "
                            f"{instance_id}/{path.name} "
                            f"as {wrong_species}"
                        )

        assert species_total == EXPECTED_COUNTS[species]

        print("Total captures:", species_total)
        print("Accepted summaries:", species_accepted)
        print("Normal predictions:", species_normal)
        print("Shiny predictions:", species_shiny)

    print("\n--- Aggregate Results ---")

    print("Total captures:", total)
    print("Accepted summaries:", accepted)
    print("Rejected summaries:", rejected)

    print(
        f"Summary acceptance rate: "
        f"{accepted / total * 100:.2f}%"
    )

    print("Normal predictions:", normal_predictions)
    print("Shiny predictions:", shiny_predictions)

    print(
        f"Incorrect species rejected: "
        f"{wrong_species_rejected}/{wrong_species_total}"
    )

    print("\n--- Processing Performance ---")

    print(
        f"Average validation time: "
        f"{sum(validation_times) / len(validation_times) * 1000:.4f} ms"
    )

    if classification_times:

        print(
            f"Average classification time: "
            f"{sum(classification_times) / len(classification_times) * 1000:.4f} ms"
        )

    assert total == 140
    assert accepted == 140
    assert rejected == 0
    assert wrong_species_total == 280
    assert wrong_species_rejected == 280

    print("\nAll bulk encounter validation tests passed.")


def test_failed_rotation_validation():

    detector = ShinyDetector("firered_leafgreen")

    failure_dir = (
            PROJECT_DIR / "docs" / "figures" / "macro"
    )

    failure_images = [
        "nickname_failure.png",
        "selection_failure.png"
    ]

    rejected = 0
    validation_times = []

    print("\n--- Failed Rotation Validation ---")

    for filename in failure_images:

        failure_path = failure_dir / filename

        assert failure_path.is_file(), (
            f"Missing failure screenshot: {failure_path}"
        )

        image = cv2.imread(str(failure_path))

        assert image is not None, (
            f"Unable to load {failure_path}"
        )

        assert image.shape == (160, 240, 3), (
            "Failure screenshot must be at native resolution."
        )

        print(f"\nImage: {filename}")
        print("Image resolution: 240 x 160")

        for species, name in SPECIES_NAMES.items():

            start = perf_counter()

            valid = detector.validate_summary(
                image,
                species
            )

            validation_times.append(
                perf_counter() - start
            )

            assert not valid, (
                f"{filename} incorrectly accepted for {name}"
            )

            rejected += 1

            print(f"{name}: REJECTED")

    expected = len(failure_images) * len(SPECIES_NAMES)

    assert rejected == expected

    print("\n--- Aggregate Rejection Results ---")
    print("Unique invalid captures:", len(failure_images))

    print(
        f"Invalid screen comparisons rejected: "
        f"{rejected}/{expected}"
    )

    print(
        f"Average rejection time: "
        f"{sum(validation_times) / len(validation_times) * 1000:.4f} ms"
    )

    print("Failed rotation validation: PASS")


if __name__ == "__main__":

    test_failed_rotation_validation()