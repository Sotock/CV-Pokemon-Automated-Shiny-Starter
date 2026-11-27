from instances.library_manager import LibraryInstance


PROFILE_NAME = "Sapphire TEST Treecko"


def test_sapphire_profile_macro():

    instance = LibraryInstance(PROFILE_NAME)

    try:

        print("Profile:", instance.profile_name)
        print("Game:", instance.game)
        print("Target:", instance.target_name)
        print("Species:", instance.target_species)

        screenshot_path = instance.run_attempt()

        assert screenshot_path.is_file()

        print("Screenshot:", screenshot_path)
        print("Profile macro execution successful.")

    finally:

        instance.close()


if __name__ == "__main__":
    test_sapphire_profile_macro()