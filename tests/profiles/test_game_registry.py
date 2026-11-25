from pathlib import Path
import sys

PROJECT_DIR = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(PROJECT_DIR))

from profiles.game_registry import (
    get_supported_games,
    get_game_config,
    get_supported_starters,
    get_target_species
)

games = get_supported_games()
print("Supported games:", games)

for game in games:
    config = get_game_config(game)

    print("\nGame:", game)
    print("Emulator:", config["emulator"])
    print("Macro:", config["macro"])
    print("Vision configuration:", config["vision_config"])

    rom_path = PROJECT_DIR / config["rom_path"]
    print("ROM exists:", rom_path.is_file())

    for starter in get_supported_starters(game):
        species = get_target_species(game, starter)

        print(f"{starter}: {species}")