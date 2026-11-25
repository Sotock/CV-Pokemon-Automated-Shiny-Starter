import random

RESET_DELAY = 1800
SCREENSHOT_DELAY = 90

# GBA button indices
A = 0
START = 3
DOWN = 7

# Base frame, button, maximum variance
SCHEDULE = [
    (0, A, 1800),
    (207, A, 1800),
    (367, A, 0),
    (508, A, 0),
    (599, A, 600),
    (858, A, 600),
    (1111, A, 600),
    (1298, A, 3600),
    (1948, DOWN, 0),
    (2015, A, 0),
    (2295, A, 0),
    (2694, START, 0),
    (2780, A, 0),
    (2863, A, 0),
    (2934, A, 0)
]


def run_macro(core, screen, screenshot_path):
    schedule = []
    current_variance = 0

    # Generate cumulative randomized delays
    for frame, key, max_variance in SCHEDULE:
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

    # Reset emulator
    core.reset()
    print("FireRed reset initiated.")

    for _ in range(RESET_DELAY):
        core.run_frame()

    # Execute scheduled button inputs
    current_frame = 0

    for step, (target_frame, key) in enumerate(schedule):

        while current_frame < target_frame:
            core.run_frame()
            current_frame += 1

        core.add_keys(key)

        for _ in range(5):
            core.run_frame()

        core.clear_keys(key)

        print(f"Step {step} executed at macro frame {current_frame}")

        current_frame += 5

    # Wait until screenshot target frame
    screenshot_frame = schedule[-1][0] + SCREENSHOT_DELAY

    while current_frame < screenshot_frame:
        core.run_frame()
        current_frame += 1

    # Capture final game state
    screen.to_pil().convert("RGB").save(screenshot_path)

    print("FireRed reset macro completed!")
    print("Screenshot captured.")