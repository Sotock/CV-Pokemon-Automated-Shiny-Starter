from profiles.game_registry import get_game_config

# Validates battery save size and rejects blank game saves.
def validate_battery_save(save_data, game):
    config = get_game_config(game)
    expected_size = config["save_size"]
    rtc_size = config.get("rtc_size", 0)
    valid_sizes = {expected_size, expected_size + rtc_size}

    if len(save_data) not in valid_sizes:
        raise ValueError(
            f"Unexpected battery save size: "
            f"{len(save_data)} bytes. "
            f"Expected {sorted(valid_sizes)}."
        )

    # Exclude RTC metadata from blank save validation.
    payload = save_data[:expected_size]
    if payload == b"\xff" * expected_size:
        raise ValueError(
            "Prepared save is blank. "
            "Save through the in-game menu before finalizing."
        )