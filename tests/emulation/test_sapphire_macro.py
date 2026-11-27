from instances.library_manager import LibraryInstance


PROFILE_NAME = "Sapphire TEST Treecko"
ROTATIONS = 3

STARTERS = {
    "Treecko": "252",
    "Torchic": "255",
    "Mudkip": "258"
}


def test_sapphire_macro():

    instance = LibraryInstance(PROFILE_NAME)

    try:

        for starter, species in STARTERS.items():

            for rotation in range(ROTATIONS):

                screenshot_path = (
                        instance.picture_dir
                        / f"{starter.lower()}_test_{rotation + 1}.png"
                )

                instance.run_macro(
                    instance.core,
                    instance.screen,
                    screenshot_path,
                    target_species=species
                )

                print("Starter:", starter)
                print("Rotation:", rotation + 1)
                print("Screenshot:", screenshot_path)
                print("Screenshot exists:", screenshot_path.is_file())

    finally:

        instance.close()


if __name__ == "__main__":
    test_sapphire_macro()