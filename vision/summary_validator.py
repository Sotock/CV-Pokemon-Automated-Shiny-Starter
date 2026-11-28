import cv2
import numpy as np

# Validates summary screen structure and expected Pokemon species.
class SummaryValidator:
    # Initializes summary and species templates from normal reference images.
    def __init__(self, config, dataset_dir):
        self.width = config["resolution"]["width"]
        self.height = config["resolution"]["height"]
        self.regions = config["validation_regions"]
        self.summary_templates = {}
        self.species_templates = {}

        normal_dir = dataset_dir / "normal"
        reference_paths = sorted(normal_dir.glob("*.png"))
        if not reference_paths:
            raise RuntimeError("No summary references found.")

        for path in reference_paths:
            image = cv2.imread(str(path))
            if image is None:
                raise RuntimeError(f"Unable to load reference: {path}")
            if image.shape != (self.height, self.width, 3):
                raise ValueError(f"Invalid reference dimensions: {path}")

            # Store the species number template independently.
            species = path.stem
            self.species_templates[species] = self.extract_region(
                image, self.regions["species_number"]
            ).copy()

            # Verify that static summary regions are consistent across references.
            for name, region in self.regions.items():
                if name == "species_number":
                    continue

                template = self.extract_region(image, region)
                if name not in self.summary_templates:
                    self.summary_templates[name] = template.copy()
                elif not np.array_equal(template, self.summary_templates[name]):
                    raise ValueError(f"Inconsistent summary region: {name}")

    # Extracts a rectangular region from an image.
    @staticmethod
    def extract_region(image, region):
        x, y, width, height = region
        return image[y:y + height, x:x + width]

    # Validates the summary screen and confirms the expected species.
    def validate(self, image, species):
        if image is None:
            return False
        if image.shape != (self.height, self.width, 3):
            return False
        if species not in self.species_templates:
            return False

        # Verify static summary screen regions.
        for name, template in self.summary_templates.items():
            region = self.extract_region(image, self.regions[name])
            if not np.array_equal(region, template):
                return False

        # Verify the expected Pokemon species.
        species_region = self.extract_region(image, self.regions["species_number"])
        return np.array_equal(species_region, self.species_templates[species])