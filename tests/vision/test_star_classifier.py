from pathlib import Path
import json
import cv2

from vision.star_classifier import StarClassifier

PROJECT_DIR = Path(__file__).resolve().parents[2]

DATASET_DIR = (
        PROJECT_DIR / "dataset" / "firered_leafgreen" / "captures"
)

CONFIG_PATH = (
        PROJECT_DIR / "vision" / "configurations"
        / "firered_leafgreen.json"
)

with CONFIG_PATH.open("r", encoding="utf-8") as file:
    config = json.load(file)

classifier = StarClassifier(config["regions"]["star"])

images = []
labels = []
filenames = []

for category, label in [("normal", 0), ("shiny", 1)]:
    for path in sorted((DATASET_DIR / category).glob("*.png")):
        image = cv2.imread(str(path))

        if image is None:
            raise RuntimeError(f"Unable to load {path}")

        images.append(image)
        labels.append(label)
        filenames.append(f"{category}/{path.name}")

classifier.train(images, labels)

print("Star classifier trained.")
print()

correct = 0

for image, label, filename in zip(images, labels, filenames):
    prediction = classifier.predict(image)
    features = classifier.extract_features(image)

    passed = prediction == bool(label)
    correct += int(passed)

    print(f"Image: {filename}")
    print(f"HOG feature count: {features.size}")
    print(f"Expected: {'Shiny' if label else 'Normal'}")
    print(f"Predicted: {'Shiny' if prediction else 'Normal'}")
    print(f"Correct: {passed}")
    print()

print(f"Correct classifications: {correct}/{len(images)}")