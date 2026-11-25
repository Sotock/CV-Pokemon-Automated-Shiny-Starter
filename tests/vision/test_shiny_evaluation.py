from pathlib import Path
import sys
from time import perf_counter

PROJECT_DIR = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(PROJECT_DIR))

import cv2

from vision.shiny_detector import ShinyDetector


EVALUATION_DIR = (
        PROJECT_DIR
        / "dataset"
        / "firered_leafgreen"
        / "evaluation"
        / "shiny"
)

SPECIES_NAMES = {
    "001": "Bulbasaur",
    "004": "Charmander",
    "007": "Squirtle"
}

SAMPLES_PER_SPECIES = 3


def test_shiny_evaluation():

    detector = ShinyDetector("firered_leafgreen")

    totals = {
        "samples": 0,
        "valid": 0,
        "border": 0,
        "star": 0,
        "palette": 0,
        "shiny": 0
    }

    validation_times = []
    classification_times = []
    failures = []

    print("\n--- Independent Shiny Evaluation ---")

    for species, name in SPECIES_NAMES.items():

        print(f"\n--- {name} ---")

        counts = {
            key: 0 for key in totals
        }

        for index in range(1, SAMPLES_PER_SPECIES + 1):

            filename = f"{species}_{index:02d}.png"
            path = EVALUATION_DIR / filename

            assert path.is_file(), (
                f"Missing evaluation image: {path}"
            )

            image = cv2.imread(str(path))

            assert image is not None
            assert image.shape == (160, 240, 3)

            counts["samples"] += 1

            start = perf_counter()

            valid = detector.validate_summary(
                image,
                species
            )

            validation_times.append(
                perf_counter() - start
            )

            if not valid:

                print(f"{filename}: INVALID SUMMARY")
                failures.append(filename)
                continue

            counts["valid"] += 1

            start = perf_counter()

            result = detector.predict(
                image,
                species
            )

            classification_times.append(
                perf_counter() - start
            )

            counts["border"] += int(result["border"])
            counts["star"] += int(result["star"])
            counts["palette"] += int(result["palette"])
            counts["shiny"] += int(result["is_shiny"])

            expected_votes = sum([
                int(result["border"]),
                int(result["star"]),
                int(result["palette"])
            ])

            assert result["votes"] == expected_votes

            assert result["is_shiny"] == (
                    expected_votes >= 2
            )

            if not result["is_shiny"]:
                failures.append(filename)

            print(f"\nImage: {filename}")
            print("Summary validation: PASS")
            print("Border:", result["border"])
            print("Star:", result["star"])
            print("Palette:", result["palette"])
            print(f"Shiny votes: {result['votes']}/3")

            print(
                "Prediction:",
                "Shiny" if result["is_shiny"] else "Normal"
            )

        print(f"\n{name} Results:")

        for key, value in counts.items():
            totals[key] += value

        print(
            f"Valid summaries: "
            f"{counts['valid']}/{counts['samples']}"
        )

        for classifier in ("border", "star", "palette"):

            print(
                f"{classifier.capitalize()} detections: "
                f"{counts[classifier]}/{counts['valid']}"
            )

        print(
            f"Combined shiny detections: "
            f"{counts['shiny']}/{counts['samples']}"
        )

    total = totals["samples"]
    valid = totals["valid"]
    detected = totals["shiny"]

    assert total == 9

    rejected = total - valid
    false_negatives = valid - detected
    missed_shinies = total - detected

    print("\n--- Aggregate Evaluation Results ---")

    print("Total shiny samples:", total)
    print("Accepted summaries:", valid)
    print("Rejected summaries:", rejected)

    print(
        f"Summary acceptance rate: "
        f"{valid / total * 100:.2f}%"
    )

    print("\n--- Individual Classifier Results ---")

    for classifier in ("border", "star", "palette"):

        correct = totals[classifier]

        recall = (
            correct / valid * 100
            if valid else 0.0
        )

        print(
            f"{classifier.capitalize()}: "
            f"{correct}/{valid} ({recall:.2f}%)"
        )

    print("\n--- Combined Detector Results ---")

    print("True positives:", detected)
    print("Classification false negatives:", false_negatives)
    print("Total missed shiny samples:", missed_shinies)

    if valid:

        print(
            f"Classifier shiny recall: "
            f"{detected / valid * 100:.2f}%"
        )

    print(
        f"End-to-end shiny detection rate: "
        f"{detected / total * 100:.2f}%"
    )

    print("\n--- Processing Performance ---")

    print(
        "Average summary validation time: "
        f"{sum(validation_times) / len(validation_times) * 1000:.4f} ms"
    )

    if classification_times:

        print(
            "Average shiny classification time: "
            f"{sum(classification_times) / len(classification_times) * 1000:.4f} ms"
        )

    if failures:

        print("\n--- Missed Shiny Samples ---")

        for filename in failures:
            print(filename)

    assert valid == total, (
        "One or more shiny summaries were rejected."
    )

    assert detected == total, (
        "One or more shiny samples were missed."
    )

    print("\nIndependent shiny evaluation: PASS")


if __name__ == "__main__":

    test_shiny_evaluation()