import cv2
import numpy as np


class BattleValidator:

    def __init__(self, config, dataset_dir):

        self.width = config["resolution"]["width"]
        self.height = config["resolution"]["height"]

        self.menu_region = (
            config["validation_regions"]["battle_menu"]
        )

        self.sprite_region = config["regions"]["sprite"]

        self.menu_templates = []
        self.species = set()

        self.hog = cv2.HOGDescriptor(
            (64, 64),
            (16, 16),
            (8, 8),
            (8, 8),
            9
        )

        self.svm = cv2.ml.SVM_create()
        self.svm.setType(cv2.ml.SVM_C_SVC)
        self.svm.setKernel(cv2.ml.SVM_LINEAR)
        self.svm.setC(1.0)

        self.initialize_classifier(dataset_dir)

    @staticmethod
    def extract_region(image, region):

        x, y, width, height = region

        return image[
            y:y + height,
            x:x + width
        ]

    def extract_features(self, image):

        roi = self.extract_region(
            image,
            self.sprite_region
        )

        resized = cv2.resize(
            roi,
            (64, 64),
            interpolation=cv2.INTER_NEAREST
        )

        gray = cv2.cvtColor(
            resized,
            cv2.COLOR_BGR2GRAY
        )

        features = self.hog.compute(gray)

        return features.flatten().astype(np.float32)

    def initialize_classifier(self, dataset_dir):

        features = []
        labels = []

        for category in ("normal", "shiny"):

            reference_paths = sorted(
                (dataset_dir / category).glob("*.png")
            )

            for path in reference_paths:

                image = cv2.imread(str(path))

                if image is None:

                    raise RuntimeError(
                        f"Unable to load reference: {path}"
                    )

                if image.shape != (
                        self.height,
                        self.width,
                        3
                ):

                    raise ValueError(
                        f"Invalid reference dimensions: {path}"
                    )

                species = int(path.stem)

                self.species.add(species)

                menu = self.extract_region(
                    image,
                    self.menu_region
                )

                if not any(
                        np.array_equal(menu, template)
                        for template in self.menu_templates
                ):

                    self.menu_templates.append(menu.copy())

                features.append(
                    self.extract_features(image)
                )

                labels.append(species)

        if len(self.species) < 2:

            raise RuntimeError(
                "Insufficient battle sprite references."
            )

        self.svm.train(
            np.array(features, dtype=np.float32),
            cv2.ml.ROW_SAMPLE,
            np.array(labels, dtype=np.int32)
        )

    def validate_battle(self, image):

        if image is None:
            return False

        if image.shape != (
                self.height,
                self.width,
                3
        ):
            return False

        menu = self.extract_region(
            image,
            self.menu_region
        )

        return any(
            np.array_equal(menu, template)
            for template in self.menu_templates
        )

    def validate_sprite(self, image, species):

        if image is None:
            return False

        if image.shape != (
                self.height,
                self.width,
                3
        ):
            return False

        species = int(species)

        if species not in self.species:
            return False

        features = self.extract_features(
            image
        ).reshape(1, -1)

        _, prediction = self.svm.predict(features)

        predicted_species = int(prediction[0, 0])

        return predicted_species == species

    def validate(self, image, species):

        if not self.validate_battle(image):
            return False

        return self.validate_sprite(
            image,
            species
        )