from pathlib import Path
from itertools import product
from time import perf_counter
import cv2

from vision.shiny_detector import ShinyDetector


PROJECT_DIR = Path(__file__).resolve().parents[2]

GAME = "firered_leafgreen"

DATASET_DIR = (
        PROJECT_DIR / "dataset" / GAME / "captures"
)

start = perf_counter()

detector = ShinyDetector(GAME)

initialization_time = perf_counter() - start

print("Shiny detector initialized.")
print(f"Initialization time: {initialization_time:.6f} seconds")
print()

print("--- Reference Image Classification ---")
print()

correct = 0
total = 0
processing_times = []

for category, expected in [("normal", False), ("shiny", True)]:

    for path in sorted(
            (DATASET_DIR / category).glob("*.png")
    ):

        image = cv2.imread(str(path))

        if image is None:
            raise RuntimeError(f"Unable to load {path}")

        species = path.stem

        start = perf_counter()

        result = detector.predict(image, species)

        elapsed = perf_counter() - start

        processing_times.append(elapsed)

        passed = result["is_shiny"] == expected

        correct += int(passed)
        total += 1

        print(f"Image: {category}/{path.name}")
        print(f"Border: {result['border']}")
        print(f"Star: {result['star']}")
        print(f"Palette: {result['palette']}")
        print(f"Shiny votes: {result['votes']}/3")
        print(f"Expected: {'Shiny' if expected else 'Normal'}")
        print(
            f"Predicted: "
            f"{'Shiny' if result['is_shiny'] else 'Normal'}"
        )
        print(f"Processing time: {elapsed * 1000:.4f} ms")
        print(f"Correct: {passed}")
        print()

print(f"Correct classifications: {correct}/{total}")

average_time = sum(processing_times) / len(processing_times)

print(f"Average processing time: {average_time * 1000:.4f} ms")
print()

print("--- Majority Voting Verification ---")
print()

voting_correct = 0

for border, star, palette in product([False, True], repeat=3):

    expected = (
            (border and star)
            or (border and palette)
            or (star and palette)
    )

    prediction = detector.majority_vote(
        border,
        star,
        palette
    )

    passed = prediction == expected

    voting_correct += int(passed)

    print(
        f"Border: {int(border)} | "
        f"Star: {int(star)} | "
        f"Palette: {int(palette)} | "
        f"Result: {'Shiny' if prediction else 'Normal'} | "
        f"Correct: {passed}"
    )

print()
print(f"Correct voting decisions: {voting_correct}/8")

print()
print("--- Summary Screen Validation ---")
print()

valid_count = 0
invalid_count = 0

start = perf_counter()

for category in ["normal", "shiny"]:

    for path in sorted(
            (DATASET_DIR / category).glob("*.png")
    ):

        image = cv2.imread(str(path))
        species = path.stem

        assert image is not None

        valid = detector.validate_summary(
            image,
            species
        )

        assert valid

        valid_count += 1

        print(f"{category}/{path.name}: PASS")

        # Reject incorrect target species
        for wrong_species in ["001", "004", "007"]:

            if wrong_species == species:
                continue

            valid = detector.validate_summary(
                image,
                wrong_species
            )

            assert not valid

            invalid_count += 1

            print(
                f"Incorrect species {wrong_species}: "
                "REJECTED"
            )

elapsed = perf_counter() - start

print()
print("Valid summaries accepted:", valid_count)
print("Incorrect species rejected:", invalid_count)

print()
print("--- Validation Performance ---")

image = cv2.imread(
    str(DATASET_DIR / "normal" / "001.png")
)

iterations = 1000

start = perf_counter()

for _ in range(iterations):

    detector.validate_summary(
        image,
        "001"
    )

elapsed = perf_counter() - start

print(
    f"Average validation time: "
    f"{elapsed * 1000 / iterations:.4f} ms"
)

print()
print("All summary validation tests passed.")