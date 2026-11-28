from pathlib import Path
import hashlib

PROJECT_DIR = Path(__file__).resolve().parents[2]
SOURCE_DIR = PROJECT_DIR / "roms"
OUTPUT_DIR = PROJECT_DIR / "roms_demo"

PATCHES = {
    "Pokemon - FireRed Version (USA, Europe) (Rev 1).gba": {
        "sha256": "729041b940afe031302d630fdbe57c0c145f3f7b6d9b8eca5e98678d0ca4d059",
        "offsets": (
            0x44134,
            0x441AA,
            0x444C4,
            0xF17EE,
        ),
    },
    "Pokemon - LeafGreen Version (USA, Europe) (Rev 1).gba": {
        "sha256": "2f978f635b9593f6ca26ec42481c53a6b39f6cddd894ad5c062c1419fac58825",
        "offsets": (
            0x44134,
            0x441AA,
            0x444C4,
            0xF17C6,
        ),
    },
    "Pokemon - Ruby Version (USA, Europe) (Rev 2).gba": {
        "sha256": "0fdd36e92b75bed65d09df4635ab0b707b288c2bf1dc4c6e7a4a4f0eebe9d64c",
        "offsets": (
            0x40988,
            0x409FE,
            0x40D14,
            0x14189A,
        ),
    },
    "Pokemon - Sapphire Version (USA, Europe) (Rev 2).gba": {
        "sha256": "02ca41513580a8b780989dee428df747b52a0b1a55bec617886b4059eb1152fb",
        "offsets": (
            0x40988,
            0x409FE,
            0x40D14,
            0x14189A,
        ),
    },
}


def patch_rom(filename, configuration):
    source = SOURCE_DIR / filename
    destination = OUTPUT_DIR / filename

    original = source.read_bytes()

    if len(original) != 16777216:
        raise ValueError(f"Unexpected ROM size: {filename}")

    if hashlib.sha256(original).hexdigest() != configuration["sha256"]:
        raise ValueError(f"Original ROM verification failed: {filename}")

    patched = bytearray(original)

    for offset in configuration["offsets"]:
        if patched[offset] != 0x07:
            raise ValueError(f"Unexpected instruction at {offset:#x}")

        if not 0x28 <= patched[offset + 1] <= 0x2F:
            raise ValueError(f"Unexpected comparison at {offset:#x}")

        patched[offset] = 0xFF

        print(f"Patched {offset:#010x}: 07 -> FF")

    differences = sum(
        before != after
        for before, after in zip(original, patched)
    )

    if differences != len(configuration["offsets"]):
        raise ValueError(f"Unexpected modification count: {filename}")

    destination.write_bytes(patched)

    if destination.read_bytes() != patched:
        raise IOError(f"Output verification failed: {filename}")

    print(f"ROM: {filename}")
    print(f"Modified bytes: {differences}")
    print(f"Output: {destination}")
    print("Original ROM preserved.")
    print("Output verification: PASS")


def main():
    OUTPUT_DIR.mkdir(exist_ok=True)

    successful = 0
    failed = 0

    for filename, configuration in PATCHES.items():
        print(f"\n--- Patching {filename} ---")

        try:
            patch_rom(filename, configuration)
            successful += 1

        except (OSError, ValueError) as error:
            print(f"FAILED: {error}")
            failed += 1

    print("\n--- Demo ROM Patch Summary ---")
    print(f"Successful: {successful}")
    print(f"Failed: {failed}")

    if failed:
        raise SystemExit(1)

    print("Demo ROM patching completed.")


if __name__ == "__main__":
    main()