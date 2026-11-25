from pathlib import Path
import json
import cv2

from vision.border_classifier import BorderClassifier
from vision.star_classifier import StarClassifier
from vision.palette_classifier import PaletteClassifier


PROJECT_DIR = Path(__file__).resolve().parent.parent


class ShinyDetector:

    def __init__(self, game):

        self.game = game

        config_path = (
                PROJECT_DIR / "vision" / "configurations"
                / f"{game}.json"
        )

        self.dataset_dir = (
                PROJECT_DIR / "dataset" / game / "captures"
        )

        with config_path.open("r", encoding="utf-8") as file:
            self.config = json.load(file)

        regions = self.config["regions"]

        self.border = BorderClassifier(regions["border"])
        self.star = StarClassifier(regions["star"])
        self.palette = PaletteClassifier(regions["sprite"])

        self.initialize_classifiers()

    def initialize_classifiers(self):

        images = []
        labels = []

        for category, label in [("normal", 0), ("shiny", 1)]:

            for path in sorted(
                    (self.dataset_dir / category).glob("*.png")
            ):

                image = cv2.imread(str(path))

                if image is None:
                    raise RuntimeError(f"Unable to load {path}")

                images.append(image)
                labels.append(label)

        self.border.train(images, labels)
        self.star.train(images, labels)

        for normal_path in sorted(
                (self.dataset_dir / "normal").glob("*.png")
        ):

            species = normal_path.stem

            shiny_path = (
                    self.dataset_dir / "shiny" / normal_path.name
            )

            normal = cv2.imread(str(normal_path))
            shiny = cv2.imread(str(shiny_path))

            if normal is None or shiny is None:
                raise RuntimeError(
                    f"Missing references for species {species}"
                )

            self.palette.register_species(
                species,
                normal,
                shiny
            )

    @staticmethod
    def majority_vote(border, star, palette):

        votes = sum([
            bool(border),
            bool(star),
            bool(palette)
        ])

        return votes >= 2

    def predict(self, image, species):

        border_prediction = self.border.predict(image)

        star_prediction = self.star.predict(image)

        palette_prediction = self.palette.predict(
            image,
            species
        )

        votes = sum([
            border_prediction,
            star_prediction,
            palette_prediction
        ])

        is_shiny = self.majority_vote(
            border_prediction,
            star_prediction,
            palette_prediction
        )

        return {
            "border": border_prediction,
            "star": star_prediction,
            "palette": palette_prediction,
            "votes": votes,
            "is_shiny": is_shiny
        }