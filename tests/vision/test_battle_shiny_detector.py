from pathlib import Path
import cv2

from vision.battle_shiny_detector import BattleShinyDetector


PROJECT_DIR = Path(__file__).resolve().parents[2]

EVALUATION_DIR = (
        PROJECT_DIR
        / "dataset"
        / "ruby_sapphire"
        / "evaluation"
)

SPECIES = ("252", "255", "258")


def test_battle_shiny_detector():

    detector = BattleShinyDetector("ruby_sapphire")

    total = 0
    correct = 0

    wrong_species_total = 0
    wrong_species_rejected = 0

    for category in ("normal", "shiny"):

        expected_shiny = category == "shiny"

        paths = sorted(
            (EVALUATION_DIR / category).glob("*.png")
        )

        if not paths:

            raise RuntimeError(
                f"No evaluation images found: {category}"
            )

        for path in paths:

            species = path.stem.split("_")[0]

            if species not in SPECIES:

                raise ValueError(
                    f"Unknown species: {path.name}"
                )

            image = cv2.imread(str(path))

            if image is None:

                raise RuntimeError(
                    f"Unable to load {path}"
                )

            result = detector.predict(
                image,
                species
            )

            normal_distance, shiny_distance = (
                detector.palette.compare(image, species)
            )

            passed = (
                    result["valid_encounter"]
                    and result["is_shiny"] == expected_shiny
            )

            total += 1
            correct += int(passed)

            print("\nImage:", path.name)
            print("Expected:", category)
            print("Battle valid:", result["valid_battle"])
            print("Sprite valid:", result["valid_sprite"])
            print("Normal distance:", normal_distance)
            print("Shiny distance:", shiny_distance)
            print("Shiny prediction:", result["is_shiny"])
            print("Result:", "PASS" if passed else "FAIL")

            # Verify rejection of incorrect target species.
            for other_species in SPECIES:

                if other_species == species:
                    continue

                wrong_result = detector.predict(
                    image,
                    other_species
                )

                rejected = (
                        not wrong_result["valid_encounter"]
                        and wrong_result["is_shiny"] is None
                )

                wrong_species_total += 1
                wrong_species_rejected += int(rejected)

                print(
                    f"Wrong species {other_species}:",
                    "PASS" if rejected else "FAIL"
                )

    print("\nEvaluation results")
    print("Total images:", total)
    print("Correct classifications:", correct)
    print("Incorrect classifications:", total - correct)
    print(f"Accuracy: {correct / total * 100:.2f}%")

    print(
        "Wrong species rejected:",
        f"{wrong_species_rejected}/{wrong_species_total}"
    )

    assert correct == total
    assert wrong_species_rejected == wrong_species_total


if __name__ == "__main__":
    test_battle_shiny_detector()