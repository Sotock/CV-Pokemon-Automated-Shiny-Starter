import cv2
import numpy as np

# Classifies Pokemon coloration using spatial RGB histograms.
class PaletteClassifier:
    # Initializes the sprite region, species references, and histogram configuration.
    def __init__(self, region):
        self.region = region
        self.references = {}
        self.masks = {}
        self.bins = 32

    # Extracts the sprite region and converts it from BGR to RGB.
    def extract_roi(self, image):
        x, y, w, h = self.region
        roi = image[y:y + h, x:x + w]
        return cv2.cvtColor(roi, cv2.COLOR_BGR2RGB)

    # Creates a foreground mask by excluding shared summary screen background pixels.
    def create_mask(self, normal, shiny):
        normal_background = (
                np.all(normal == 239, axis=2)
                | np.all(normal == 255, axis=2)
        )
        shiny_background = (
                np.all(shiny == 247, axis=2)
                | np.all(shiny == 255, axis=2)
        )
        foreground = ~(normal_background & shiny_background)
        return foreground.astype(np.uint8) * 255

    # Extracts normalized RGB histograms from four spatial sprite regions.
    def extract_features(self, image, species):
        roi = self.extract_roi(image)
        mask = self.masks[species]
        height, width = roi.shape[:2]
        features = []

        # Divide the sprite into a 2x2 grid to preserve spatial color information.
        for row in range(2):
            for col in range(2):
                y1 = row * height // 2
                y2 = (row + 1) * height // 2
                x1 = col * width // 2
                x2 = (col + 1) * width // 2
                cell = roi[y1:y2, x1:x2]
                cell_mask = mask[y1:y2, x1:x2]

                # Calculate and normalize a histogram for each RGB channel.
                for channel in range(3):
                    histogram = cv2.calcHist(
                        [cell], [channel], cell_mask, [self.bins], [0, 256]
                    )
                    total = histogram.sum()
                    if total > 0:
                        histogram /= total
                    features.extend(histogram.flatten())

        return np.array(features, dtype=np.float32)

    # Registers normal and shiny reference features for a species.
    def register_species(self, species, normal, shiny):
        normal_roi = self.extract_roi(normal)
        shiny_roi = self.extract_roi(shiny)
        self.masks[species] = self.create_mask(normal_roi, shiny_roi)
        self.references[species] = {
            "normal": self.extract_features(normal, species),
            "shiny": self.extract_features(shiny, species)
        }

    # Calculates Bhattacharyya distances against both species references.
    def compare(self, image, species):
        features = self.extract_features(image, species)
        normal_distance = cv2.compareHist(
            features,
            self.references[species]["normal"],
            cv2.HISTCMP_BHATTACHARYYA
        )
        shiny_distance = cv2.compareHist(
            features,
            self.references[species]["shiny"],
            cv2.HISTCMP_BHATTACHARYYA
        )
        return normal_distance, shiny_distance

    # Classifies the sprite as shiny when its shiny reference is closer.
    def predict(self, image, species):
        normal_distance, shiny_distance = self.compare(image, species)
        return shiny_distance < normal_distance