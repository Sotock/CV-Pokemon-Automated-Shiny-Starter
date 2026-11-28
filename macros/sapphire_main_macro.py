import random

#This macro also supports Ruby; original naming conventions preserved.
SCREENSHOT_DELAY = 270
MAX_VARIANCE = 1791

# GBA button indices.
A = 0
RIGHT = 4
LEFT = 5

# Base frame, button index, and maximum random frame variance.
STARTUP_SCHEDULE = [
    (269, A, 0),
    (344, A, 0),
    (415, A, 0),
    (510, A, 0),
    (601, A, 0)
]

SELECTION_FRAME = 726

BATTLE_SCHEDULE = [
    (756, A, 0),
    (819, A, MAX_VARIANCE),
    (1245, A, 0)
]

# Executes a randomized starter encounter and captures the battle screen.
def run_macro(core, screen, screenshot_path, on_frame=None, target_species="255"):
    if target_species not in ("252", "255", "258"):
        raise ValueError(f"Unsupported Sapphire starter: {target_species}")

    if on_frame is None:
        advance_frame = core.run_frame
    else:
        # Advances emulation and publishes the framebuffer to the display callback.
        def advance_frame():
            core.run_frame()
            on_frame(screen)

    base_schedule = STARTUP_SCHEDULE.copy()

    # Select the desired starter from Birch's bag.
    # Torchic is highlighted by default.
    if target_species == "252":
        base_schedule.append((SELECTION_FRAME, LEFT, 0))
    elif target_species == "258":
        base_schedule.append((SELECTION_FRAME, RIGHT, 0))

    base_schedule.extend(BATTLE_SCHEDULE)
    schedule = []
    current_variance = 0

    # Generate cumulative randomized delays to vary encounter timing.
    for frame, key, max_variance in base_schedule:
        added_variance = random.randint(0, max_variance)
        current_variance += added_variance
        target_frame = frame + current_variance
        schedule.append((target_frame, key))
        print(
            f"Step {len(schedule) - 1}: "
            f"+{added_variance} frames; "
            f"target frame {target_frame}"
        )

    print("Total cumulative variance:", current_variance)

    # Reset the emulator before executing the encounter sequence.
    core.reset()
    print("Sapphire reset initiated.")

    # Execute scheduled button inputs using five-frame button presses.
    current_frame = 0
    for step, (target_frame, key) in enumerate(schedule):
        while current_frame < target_frame:
            advance_frame()
            current_frame += 1

        core.add_keys(key)
        for _ in range(5):
            advance_frame()
        core.clear_keys(key)

        print(f"Step {step} executed at macro frame {current_frame}")
        current_frame += 5

    # Wait until the starter's back sprite is fully visible.
    screenshot_frame = schedule[-1][0] + SCREENSHOT_DELAY
    while current_frame < screenshot_frame:
        advance_frame()
        current_frame += 1

    # Capture the final battle screen for computer vision classification.
    screen.to_pil().convert("RGB").save(screenshot_path)
    print("Sapphire reset macro completed!")
    print("Screenshot captured.")