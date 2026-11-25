SUPPORTED_GAMES = {
    "Pokemon FireRed Rev 1": {
        "short_name": "FireRed",
        "emulator": "mGBA",
        "save_size": 131072,
        "target_fps": 59.7275,
        "rom_path": (
            "roms/Pokemon - FireRed Version "
            "(USA, Europe) (Rev 1).gba"
        ),
        "macro": "macros.firered_main_macro",
        "vision_config": "firered_leafgreen",
        "starters": {
            "Bulbasaur": "001",
            "Charmander": "004",
            "Squirtle": "007"
        }
    }
}


def get_supported_games():
    return list(SUPPORTED_GAMES.keys())


def get_game_config(game):
    if game not in SUPPORTED_GAMES:
        raise ValueError(f"Unsupported game: {game}")

    return SUPPORTED_GAMES[game]


def get_supported_starters(game):
    config = get_game_config(game)
    return list(config["starters"].keys())


def get_target_species(game, starter):
    config = get_game_config(game)

    if starter not in config["starters"]:
        raise ValueError(f"Unsupported starter: {starter}")

    return config["starters"][starter]