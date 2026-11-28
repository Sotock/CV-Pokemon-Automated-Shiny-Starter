from pathlib import Path
import json
import cv2

from vision.battle_validator import BattleValidator
from vision.battle_palette_classifier import BattlePaletteClassifier

PROJECT_DIR = Path(__file__).resolve().parent.parent

# Combines battle validation, species verification, and shiny palette classification.
class BattleShinyDetector:
    # Loads the game configuration and initializes battle classification resources.
    def __init__(self, game):
        self.game = game
        config_path = PROJECT_DIR / "vision" / "configurations" / f"{game}.json"
        self.dataset_dir = PROJECT_DIR / "dataset" / game / "captures"

        with config_path.open("r", encoding="utf-8") as file:
            self.config = json.load(file)

        self.palette = BattlePaletteClassifier(self.config["regions"]["sprite"])
        self.validator = BattleValidator(self.config, self.dataset_dir)
        self.initialize_classifier()

    # Registers paired normal and shiny battle references for each species.
    def initialize_classifier(self):
        for normal_path in sorted((self.dataset_dir / "normal").glob("*.png")):
            species = normal_path.stem
            shiny_path = self.dataset_dir / "shiny" / normal_path.name
            normal = cv2.imread(str(normal_path))
            shiny = cv2.imread(str(shiny_path))

            if normal is None or shiny is None:
                raise RuntimeError(f"Missing references for species {species}")

            self.palette.register_species(species, normal, shiny)

    # Validates the battle encounter before determining shiny status.
    def predict(self, image, species):
        valid_battle = self.validator.validate_battle(image)
        valid_sprite = False
        palette_prediction = None

        # Verify the target species only after successful battle validation.
        if valid_battle:
            valid_sprite = self.validator.validate_sprite(image, species)

        valid_encounter = valid_battle and valid_sprite

        # Bypass shiny classification when encounter validation fails.
        if valid_encounter:
            palette_prediction = self.palette.predict(image, species)

        return {
            "valid_battle": valid_battle,
            "valid_sprite": valid_sprite,
            "valid_encounter": valid_encounter,
            "palette": palette_prediction,
            "is_shiny": palette_prediction
        }