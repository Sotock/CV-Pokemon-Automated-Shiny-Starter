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