from pathlib import Path
import winsound


SHINY_SOUND = (
        Path(__file__).resolve().parents[1]
        / "assets"
        / "audio"
        / "shiny.wav"
)


def play_shiny_sound():

    if not SHINY_SOUND.is_file():

        print(f"Shiny sound not found: {SHINY_SOUND}")

        return False

    try:

        winsound.PlaySound(
            str(SHINY_SOUND),
            winsound.SND_FILENAME
            | winsound.SND_ASYNC
            | winsound.SND_NODEFAULT
        )

        return True

    except (RuntimeError, OSError) as error:

        print(f"Unable to play shiny sound: {error}")

        return False


if __name__ == "__main__":

    import time

    if play_shiny_sound():

        time.sleep(3)