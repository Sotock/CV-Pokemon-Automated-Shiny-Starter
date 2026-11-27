from instances.library_manager import LibraryInstance


PROFILE = "Sapphire TEST Mudkip"
ROTATIONS = 10


def test_sapphire_classified_attempt():

    instance = LibraryInstance(PROFILE)

    try:

        print("Profile:", instance.profile_name)
        print("Game:", instance.game)
        print("Target:", instance.target_name)
        print("Species:", instance.target_species)

        for _ in range(ROTATIONS):

            screenshot_path, result = (
                instance.run_classified_attempt()
            )

            assert screenshot_path.is_file()

            if result["is_shiny"]:

                print("Shiny encounter detected.")
                break

        statistics = instance.get_statistics()

        print("\nFinal statistics:")

        for name, value in statistics.items():

            print(f"{name}: {value}")

        assert statistics["completed_rotations"] > 0
        assert statistics["failed_rotations"] == 0

        assert (
                statistics["valid_encounters"]
                == statistics["completed_rotations"]
        )

        print("\nSapphire classified attempt test passed.")

    finally:

        instance.close()

    assert not instance.instance_dir.exists()

    print("Temporary instance cleanup verified.")


if __name__ == "__main__":
    test_sapphire_classified_attempt()