import json
from pathlib import Path

SETTINGS_PATH = Path(__file__).resolve().parents[1] / "settings.json"

DEFAULT_KEY_BINDINGS = {
    "A": "z",
    "B": "x",
    "Select": "BackSpace",
    "Start": "Return",
    "Right": "Right",
    "Left": "Left",
    "Up": "Up",
    "Down": "Down",
    "R": "s",
    "L": "a"
}

BUTTON_INDICES = {
    "A": 0,
    "B": 1,
    "Select": 2,
    "Start": 3,
    "Right": 4,
    "Left": 5,
    "Up": 6,
    "Down": 7,
    "R": 8,
    "L": 9
}

DEFAULT_AUDIO_SETTINGS = {
    "preparation_music": True,
    "shiny_notification": True,
    "export_fanfare": True
}

DEFAULT_MUSIC_VOLUME = 75

# Generates an independent copy of the default application settings.
def default_settings():
    return {
        "key_bindings": DEFAULT_KEY_BINDINGS.copy(),
        "audio": DEFAULT_AUDIO_SETTINGS.copy(),
        "music_volume": DEFAULT_MUSIC_VOLUME
    }

# Normalizes single-character keyboard bindings.
def normalize_key(key):
    if len(key) == 1:
        return key.lower()

    return key

# Validates keyboard bindings and rejects missing or duplicate assignments.
def validate_key_bindings(bindings):
    if not isinstance(bindings, dict):
        return False

    if set(bindings) != set(DEFAULT_KEY_BINDINGS):
        return False

    if not all(
            isinstance(key, str) and key.strip()
            for key in bindings.values()
    ):
        return False

    keys = [
        normalize_key(key)
        for key in bindings.values()
    ]

    return len(keys) == len(set(keys))

# Loads valid saved preferences while retaining defaults for invalid values.
def load_settings():
    settings = default_settings()

    if not SETTINGS_PATH.is_file():
        return settings

    try:
        with SETTINGS_PATH.open("r", encoding="utf-8") as file:
            stored = json.load(file)

        if not isinstance(stored, dict):
            return settings

        bindings = stored.get("key_bindings")
        if validate_key_bindings(bindings):
            settings["key_bindings"] = {
                button: normalize_key(key)
                for button, key in bindings.items()
            }

        audio = stored.get("audio", {})
        if isinstance(audio, dict):
            for name in DEFAULT_AUDIO_SETTINGS:
                value = audio.get(name)
                if isinstance(value, bool):
                    settings["audio"][name] = value

        volume = stored.get("music_volume")
        if type(volume) is int and 0 <= volume <= 100:
            settings["music_volume"] = volume

    except (OSError, ValueError) as error:
        print(f"Unable to load settings: {error}")

    return settings

# Validates and persistently stores application preferences.
def save_settings(settings):
    if not validate_key_bindings(settings["key_bindings"]):
        raise ValueError("Invalid keyboard bindings.")

    audio = settings["audio"]
    if set(audio) != set(DEFAULT_AUDIO_SETTINGS):
        raise ValueError("Invalid audio settings.")

    if not all(isinstance(value, bool) for value in audio.values()):
        raise ValueError("Invalid audio preference.")

    volume = settings.get("music_volume", DEFAULT_MUSIC_VOLUME)
    if type(volume) is not int or not 0 <= volume <= 100:
        raise ValueError("Invalid music volume.")

    # Write to a temporary file before replacing the existing settings.
    temporary_path = SETTINGS_PATH.with_suffix(".tmp")

    with temporary_path.open("w", encoding="utf-8") as file:
        json.dump(settings, file, indent=4)

    temporary_path.replace(SETTINGS_PATH)

# Maps configured keyboard keys to emulator button indices.
def get_key_mapping():
    bindings = load_settings()["key_bindings"]

    return {
        key: BUTTON_INDICES[button]
        for button, key in bindings.items()
    }

# Determines whether a particular audio feature is enabled.
def audio_enabled(name):
    return load_settings()["audio"].get(name, False)

# Retrieves the saved preparation music volume.
def get_music_volume():
    return load_settings()["music_volume"]

# Saves the preparation music volume without changing other preferences.
def save_music_volume(volume):
    settings = load_settings()
    settings["music_volume"] = max(0, min(100, int(volume)))
    save_settings(settings)

# Converts keyboard identifiers into readable display names.
def format_key(key):
    names = {
        "Return": "Enter",
        "BackSpace": "Backspace",
        "space": "Space",
        "Escape": "Esc"
    }

    return names.get(
        key,
        key.upper() if len(key) == 1 else key
    )

# Generates the three-row gameplay controls reference.
def get_controls_text():
    bindings = load_settings()["key_bindings"]

    # Formats the assigned keyboard key and corresponding GBA button.
    def binding(button):
        return f"{format_key(bindings[button])}: {button}"

    first_row = "    ".join(
        binding(button)
        for button in ("A", "B", "Start", "Select")
    )

    second_row = "    ".join(
        binding(button)
        for button in ("Up", "Down", "Left", "Right")
    )

    third_row = "    ".join(
        binding(button)
        for button in ("L", "R")
    )

    return "\n".join((first_row, second_row, third_row))