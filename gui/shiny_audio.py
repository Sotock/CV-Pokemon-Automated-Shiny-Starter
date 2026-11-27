from pathlib import Path

import pygame

from gui.settings import (
    audio_enabled,
    get_music_volume
)


AUDIO_DIR = (
        Path(__file__).resolve().parents[1]
        / "assets"
        / "audio"
)

SHINY_SOUND = AUDIO_DIR / "shiny.wav"

EXPORT_SOUND = AUDIO_DIR / "pokemon_obtained.wav"

PREPARATION_THEMES = {
    "Pokemon FireRed Rev 1":
        AUDIO_DIR / "firered_leafgreen_theme.wav",

    "Pokemon LeafGreen Rev 1":
        AUDIO_DIR / "firered_leafgreen_theme.wav",

    "Pokemon Ruby Rev 2":
        AUDIO_DIR / "ruby_sapphire_theme.wav",

    "Pokemon Sapphire Rev 2":
        AUDIO_DIR / "ruby_sapphire_theme.wav"
}

sound_cache = {}


def initialize_audio():

    if pygame.mixer.get_init() is not None:

        return True

    try:

        pygame.mixer.init(
            frequency=44100,
            size=-16,
            channels=2,
            buffer=512
        )

        return True

    except pygame.error as error:

        print(f"Unable to initialize audio: {error}")

        return False


def play_audio(path):

    if not path.is_file():

        print(f"Audio file not found: {path}")

        return False

    if not initialize_audio():

        return False

    try:

        if path not in sound_cache:

            sound_cache[path] = pygame.mixer.Sound(
                str(path)
            )

        sound = sound_cache[path]

        channel = sound.play()

        return channel is not None

    except (pygame.error, OSError) as error:

        print(f"Unable to play audio: {error}")

        return False


def set_music_volume(volume):

    if pygame.mixer.get_init() is None:

        return

    volume = max(
        0.0,
        min(1.0, float(volume) / 100)
    )

    pygame.mixer.music.set_volume(volume)


def stop_audio():

    if pygame.mixer.get_init() is not None:

        pygame.mixer.music.stop()

        pygame.mixer.music.unload()


def play_preparation_music(game):

    if not audio_enabled("preparation_music"):

        return False

    theme = PREPARATION_THEMES.get(game)

    if theme is None:

        print(f"No preparation theme for: {game}")

        return False

    if not theme.is_file():

        print(f"Audio file not found: {theme}")

        return False

    if not initialize_audio():

        return False

    try:

        pygame.mixer.music.load(str(theme))

        set_music_volume(get_music_volume())

        pygame.mixer.music.play(loops=-1)

        return True

    except (pygame.error, OSError) as error:

        print(f"Unable to play preparation music: {error}")

        return False


def play_shiny_sound():

    if not audio_enabled("shiny_notification"):

        return False

    return play_audio(SHINY_SOUND)


def play_export_fanfare():

    if not audio_enabled("export_fanfare"):

        return False

    return play_audio(EXPORT_SOUND)


if __name__ == "__main__":

    import time

    print("Testing preparation music...")

    play_preparation_music(
        "Pokemon FireRed Rev 1"
    )

    for volume in (100, 50, 25, 0, 75):

        print(f"Music volume: {volume}%")

        set_music_volume(volume)

        time.sleep(4)

    print("Testing simultaneous notification...")

    play_shiny_sound()

    time.sleep(4)

    stop_audio()

    print("Testing export fanfare...")

    play_export_fanfare()

    time.sleep(6)

    print("Audio test completed.")