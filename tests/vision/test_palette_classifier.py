from pathlib import Path
import json
import cv2

from vision.palette_classifier import PaletteClassifier

PROJECT_DIR = Path(__file__).resolve().parents[2]

DATASET_DIR = (
        PROJECT_DIR / "dataset" / "firered_leafgreen" / "captures"
)

CONFIG_PATH = (
        PROJECT_DIR / "vision" / "configurations"
        / "firered_leafgreen.json"
)

OUTPUT_DIR = PROJECT_DIR / "pictures" / "palette_test"

OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

with CONFIG_PATH.open("r", encoding="utf-8") as file:
    config = json.load(file)

classifier = PaletteClassifier(config["regions"]["sprite"])

SPECIES = {
    "001": "Bulbasaur",
    "004": "Charmander",
    "007": "Squirtle"
}

images = []

for species, name in SPECIES.items():

    normal = cv2.imread(
        str(DATASET_DIR / "normal" / f"{species}.png")
    )

    shiny = cv2.imread(
        str(DATASET_DIR / "shiny" / f"{species}.png")
    )

    if normal is None or shiny is None:
        raise RuntimeError(f"Unable to load {name} references")

    classifier.register_species(species, normal, shiny)

    images.append((normal, species, False))
    images.append((shiny, species, True))

    cv2.imwrite(
        str(OUTPUT_DIR / f"{species}_mask.png"),
        classifier.masks[species]
    )

    print(f"Registered references: {name}")

print()
print("Palette classifier initialized.")
print()

correct = 0

for image, species, expected in images:

    features = classifier.extract_features(image, species)

    normal_distance, shiny_distance = classifier.compare(
        image,
        species
    )

    prediction = classifier.predict(image, species)

    passed = prediction == expected

    correct += int(passed)

    print(f"Pokemon: {SPECIES[species]}")
    print(f"Histogram feature count: {features.size}")
    print(f"Normal distance: {normal_distance:.6f}")
    print(f"Shiny distance: {shiny_distance:.6f}")
    print(f"Expected: {'Shiny' if expected else 'Normal'}")
    print(f"Predicted: {'Shiny' if prediction else 'Normal'}")
    print(f"Correct: {passed}")
    print()

print(f"Correct classifications: {correct}/{len(images)}")