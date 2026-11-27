from pathlib import Path
from unittest.mock import patch

import test_shiny_notification as notification_test


PROJECT_DIR = Path(__file__).resolve().parents[2]

CONTROLLED_SAVE = (
        PROJECT_DIR
        / "temp"
        / "leafgreen_shiny_preservation"
        / "game.sav"
)


def test_leafgreen_shiny_notification():

    with patch.multiple(
            notification_test,
            SHINY_PROFILE="LeafGreen TEST Charmander",
            NORMAL_PROFILE="LeafGreen TEST Bulbasaur",
            CONTROLLED_SAVE=CONTROLLED_SAVE
    ):

        notification_test.test_shiny_notification()


if __name__ == "__main__":

    test_leafgreen_shiny_notification()