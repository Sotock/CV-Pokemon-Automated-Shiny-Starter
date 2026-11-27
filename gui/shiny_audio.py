from pathlib import Path
import winsound

from gui.settings import audio_enabled


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


def play_audio(path, loop=False):

    if not path.is_file():

        print(f"Audio file not found: {path}")

        return False

    flags = (
            winsound.SND_FILENAME
            | winsound.SND_ASYNC
            | winsound.SND_NODEFAULT
    )

    if loop:

        flags |= winsound.SND_LOOP

    try:

        winsound.PlaySound(str(path), flags)

        return True

    except (RuntimeError, OSError) as error:

        print(f"Unable to play audio: {error}")

        return False


def stop_audio():

    try:

        winsound.PlaySound(None, 0)

    except (RuntimeError, OSError) as error:

        print(f"Unable to stop audio: {error}")


def play_preparation_music(game):

    if not audio_enabled("preparation_music"):

        return False

    theme = PREPARATION_THEMES.get(game)

    if theme is None:

        print(f"No preparation theme for: {game}")

        return False

    return play_audio(theme, loop=True)


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

    print("Testing shiny notification...")

    play_shiny_sound()

    time.sleep(3)

    print("Testing export fanfare...")

    play_export_fanfare()

    time.sleep(6)

    for game in (
            "Pokemon FireRed Rev 1",
            "Pokemon Sapphire Rev 2"
    ):

        print(f"Testing preparation music: {game}")

        play_preparation_music(game)

        time.sleep(10)

        stop_audio()

    print("Audio test completed.")