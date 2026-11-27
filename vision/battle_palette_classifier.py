import numpy as np

from vision.palette_classifier import PaletteClassifier


class BattlePaletteClassifier(PaletteClassifier):

    def create_mask(self, normal, shiny):

        if normal.shape != shiny.shape:

            raise ValueError(
                "Battle reference dimensions do not match."
            )

        # Isolate pixels affected by shiny coloration.
        foreground = np.any(
            normal != shiny,
            axis=2
        )

        if not np.any(foreground):

            raise ValueError(
                "Normal and shiny references are identical."
            )

        return foreground.astype(np.uint8) * 255