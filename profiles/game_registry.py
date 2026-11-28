SUPPORTED_GAMES = {
    "Pokemon FireRed Rev 1": {
        "short_name": "FireRed",
        "emulator": "mGBA",
        "save_size": 131072,
        "target_fps": 59.7275,
        "rom_path": (
            "roms/Pokemon - FireRed Version "
            #"roms_demo/Pokemon - FireRed Version "
            "(USA, Europe) (Rev 1).gba"
        ),
        "macro": "macros.firered_main_macro",
        "vision_config": "firered_leafgreen",
        "starters": {
            "Bulbasaur": "001",
            "Charmander": "004",
            "Squirtle": "007"
        }
    },
    "Pokemon LeafGreen Rev 1": {
        "short_name": "LeafGreen",
        "emulator": "mGBA",
        "save_size": 131072,
        "target_fps": 59.7275,
        "rom_path": (
            "roms/Pokemon - LeafGreen Version "
            #"roms_demo/Pokemon - LeafGreen Version "
            "(USA, Europe) (Rev 1).gba"
        ),
        "macro": "macros.firered_main_macro",
        "vision_config": "firered_leafgreen",
        "starters": {
            "Bulbasaur": "001",
            "Charmander": "004",
            "Squirtle": "007"
        }
    },
    "Pokemon Ruby Rev 2": {
        "short_name": "Ruby",
        "emulator": "mGBA",
        "save_size": 131072,
        "rtc_size": 16,
        "target_fps": 59.7275,
        "rom_path": (
            "roms/Pokemon - Ruby Version "
            #"roms_demo/Pokemon - Ruby Version "
            "(USA, Europe) (Rev 2).gba"
        ),
        "macro": "macros.sapphire_main_macro",
        "vision_config": "ruby_sapphire",
        "starters": {
            "Treecko": "252",
            "Torchic": "255",
            "Mudkip": "258"
        }
    },
    "Pokemon Sapphire Rev 2": {
        "short_name": "Sapphire",
        "emulator": "mGBA",
        "save_size": 131072,
        "rtc_size": 16,
        "target_fps": 59.7275,
        "rom_path": (
            "roms/Pokemon - Sapphire Version "
            #"roms_demo/Pokemon - Sapphire Version "
            "(USA, Europe) (Rev 2).gba"
        ),
        "macro": "macros.sapphire_main_macro",
        "vision_config": "ruby_sapphire",
        "starters": {
            "Treecko": "252",
            "Torchic": "255",
            "Mudkip": "258"
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