from pathlib import Path
import sys
from time import perf_counter
from unittest.mock import patch

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

FAILURE_DIR = (
        PROJECT_DIR / "docs" / "figures" / "macro"
)

FAILURE_IMAGES = [
    "nickname_failure.png",
    "selection_failure.png"
]

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
            assert result["valid_summary"]

            image = cv2.imread(str(screenshot))

            assert image is not None

            assert instance.detector.validate_summary(
                image,
                instance.target_species
            )

            disk_result = instance.detector.predict(
                image,
                instance.target_species
            )

            disk_result["valid_summary"] = True

            assert result == disk_result

            assert 0 <= result["votes"] <= 3

            assert result["is_shiny"] == (
                    result["votes"] >= 2
            )

            print("Live summary validation: PASS")
            print("Live and saved classification match: PASS")
            print("Majority voting: PASS")

            original_statistics = instance.get_statistics()

            start = perf_counter()

            for _ in range(100):
                instance.classify_frame()

            elapsed = perf_counter() - start

            assert (
                    instance.get_statistics()
                    == original_statistics
            )

            print("Repeated classification counters: PASS")

            print(
                "Average framebuffer processing time: "
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

            assert len(paths) == 10

            for path in paths:

                image = cv2.imread(str(path))

                assert image is not None

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
        "Average validation time: "
        f"{sum(validation_times) / len(validation_times) * 1000:.4f} ms"
    )

    if classification_times:

        print(
            "Average classification time: "
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

    rejected = 0
    validation_times = []

    print("\n--- Failed Rotation Validation ---")

    for filename in FAILURE_IMAGES:

        failure_path = FAILURE_DIR / filename

        image = cv2.imread(str(failure_path))

        assert image is not None
        assert image.shape == (160, 240, 3)

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

            assert not valid

            rejected += 1

            print(f"{name}: REJECTED")

    expected = len(FAILURE_IMAGES) * len(SPECIES_NAMES)

    assert rejected == expected

    print("\n--- Aggregate Rejection Results ---")
    print("Unique invalid captures:", len(FAILURE_IMAGES))

    print(
        f"Invalid screen comparisons rejected: "
        f"{rejected}/{expected}"
    )

    print(
        "Average rejection time: "
        f"{sum(validation_times) / len(validation_times) * 1000:.4f} ms"
    )

    print("Failed rotation validation: PASS")


def test_live_validation_integration():

    profile_name = "FireRed TEST Bulbasaur"

    save_path = (
            PROJECT_DIR / "saves"
            / profile_name / "game.sav"
    )

    original_save = save_path.read_bytes()

    instance = LibraryInstance(profile_name)
    instance_dir = instance.instance_dir

    try:

        print("\n--- Live Validation Integration ---")

        # Execute one genuine automated encounter
        screenshot, result = (
            instance.run_classified_attempt()
        )

        assert result["valid_summary"]
        assert screenshot.is_file()

        valid_image = cv2.imread(str(screenshot))

        assert valid_image is not None

        initial_shinies = int(result["is_shiny"])

        stats = instance.get_statistics()

        assert stats["attempts"] == 1
        assert stats["completed_rotations"] == 1
        assert stats["valid_encounters"] == 1
        assert stats["failed_rotations"] == 0

        print("Live encounter validation: PASS")
        print("Valid encounter tracking: PASS")

        # Inject controlled invalid framebuffer samples
        print("\n--- Controlled Fault Injection ---")

        for index, filename in enumerate(
                FAILURE_IMAGES,
                start=1
        ):

            image = cv2.imread(
                str(FAILURE_DIR / filename)
            )

            assert image is not None

            def injected_macro(core, screen, path):
                if not cv2.imwrite(str(path), image):
                    raise RuntimeError(
                        "Unable to save injected screenshot."
                    )

            with patch.object(
                    instance,
                    "run_macro",
                    side_effect=injected_macro
            ):

                with patch.object(
                        instance,
                        "get_frame_bgr",
                        return_value=image
                ):

                    with patch.object(
                            instance.detector,
                            "predict",
                            side_effect=AssertionError(
                                "Invalid summary was classified."
                            )
                    ) as predict_mock:

                        screenshot, result = (
                            instance.run_classified_attempt()
                        )

                        predict_mock.assert_not_called()

            assert not result["valid_summary"]
            assert result["is_shiny"] is None
            assert result["votes"] is None

            stats = instance.get_statistics()

            assert stats["attempts"] == index + 1
            assert stats["completed_rotations"] == index + 1
            assert stats["valid_encounters"] == 1
            assert stats["failed_rotations"] == index
            assert stats["consecutive_failures"] == index
            assert stats["shinies_found"] == initial_shinies

            print(f"{filename}: PASS")
            print("Classification bypass: PASS")
            print("Failed rotation tracking: PASS")

        # Inject a valid summary following both failures
        print("\n--- Counter Recovery Verification ---")

        def recovered_macro(core, screen, path):
            if not cv2.imwrite(str(path), valid_image):
                raise RuntimeError(
                    "Unable to save recovery screenshot."
                )

        with patch.object(
                instance,
                "run_macro",
                side_effect=recovered_macro
        ):

            with patch.object(
                    instance,
                    "get_frame_bgr",
                    return_value=valid_image
            ):

                screenshot, result = (
                    instance.run_classified_attempt()
                )

                assert result["valid_summary"]

                previous_stats = instance.get_statistics()

                for _ in range(100):
                    instance.classify_frame()

                assert (
                        instance.get_statistics()
                        == previous_stats
                )

        stats = instance.get_statistics()

        assert stats["attempts"] == 4
        assert stats["completed_rotations"] == 4
        assert stats["valid_encounters"] == 2
        assert stats["failed_rotations"] == 2
        assert stats["consecutive_failures"] == 0
        assert stats["shinies_found"] == initial_shinies * 2
        assert stats["success_rate"] == 50.0

        assert stats["completed_rotations"] == (
                stats["valid_encounters"]
                + stats["failed_rotations"]
        )

        print("Consecutive failure reset: PASS")
        print("Repeated classification counters: PASS")
        print("Rotation counter consistency: PASS")

        print("\n--- Final Test Statistics ---")

        for name, value in stats.items():
            print(f"{name}: {value}")

    finally:
        instance.close()

    assert not instance_dir.exists()
    assert save_path.read_bytes() == original_save

    print("\nTemporary instance cleanup: PASS")
    print("Permanent save unchanged: True")
    print("Live validation integration: PASS")


if __name__ == "__main__":

    test_live_validation_integration()