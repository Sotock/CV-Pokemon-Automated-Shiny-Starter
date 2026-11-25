from pathlib import Path
import cv2

PROJECT_DIR = Path(__file__).resolve().parents[2]

DATASET_DIR = (
        PROJECT_DIR / "dataset" / "firered_leafgreen" / "captures"
)

OUTPUT_DIR = PROJECT_DIR / "pictures" / "roi_test"

REGIONS = {
    "border": (20, 20, 17, 11),
    "star": (100, 34, 12, 12),
    "sprite": (24, 34, 72, 60)
}

COLORS = {
    "border": (255, 0, 0),
    "star": (0, 0, 255),
    "sprite": (0, 255, 0)
}

OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

for category in ("normal", "shiny"):
    for image_path in sorted(
            (DATASET_DIR / category).glob("*.png")
    ):
        image = cv2.imread(str(image_path))

        if image is None:
            raise RuntimeError(f"Unable to load {image_path}")

        if image.shape[:2] != (160, 240):
            raise ValueError(f"Unexpected resolution: {image_path}")

        annotated = image.copy()
        prefix = f"{category}_{image_path.stem}"

        for name, (x, y, w, h) in REGIONS.items():
            roi = image[y:y + h, x:x + w]

            cv2.imwrite(
                str(OUTPUT_DIR / f"{prefix}_{name}.png"),
                roi
            )

            cv2.rectangle(
                annotated,
                (x, y),
                (x + w - 1, y + h - 1),
                COLORS[name],
                1
            )

        enlarged = cv2.resize(
            annotated,
            None,
            fx=3,
            fy=3,
            interpolation=cv2.INTER_NEAREST
        )

        cv2.imwrite(
            str(OUTPUT_DIR / f"{prefix}_annotated.png"),
            enlarged
        )

        print(f"Processed: {prefix}")

print("ROI visualization completed.")