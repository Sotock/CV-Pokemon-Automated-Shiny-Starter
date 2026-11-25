from pathlib import Path
import shutil
import mgba.core
import mgba.vfs
import mgba.image
import mgba.log

PROJECT_DIR = Path(__file__).resolve().parents[2]

ROM_PATH = PROJECT_DIR / "roms" / "Pokemon - FireRed Version (USA, Europe) (Rev 1).gba"
SAVE_PATH = PROJECT_DIR / "saves" / "FireRed Starter" / "game.sav"
TEMP_SAVE = PROJECT_DIR / "temp" / "test_libmgba.sav"
PICTURE_DIR = PROJECT_DIR / "pictures"

# 1.1 - Load ROM
mgba.log.silence()

core = mgba.core.load_path(str(ROM_PATH))

if core is None:
    raise RuntimeError("ROM failed to load.")

print("ROM loaded successfully.")

# 1.2 - Load temporary save
TEMP_SAVE.parent.mkdir(parents=True, exist_ok=True)
shutil.copy2(SAVE_PATH, TEMP_SAVE)

save = mgba.vfs.open_path(str(TEMP_SAVE), "r+")

if not core.load_save(save):
    raise RuntimeError("Save failed to load.")

print("Save loaded successfully.")

# 1.3 - Initialize framebuffer and reset
screen = mgba.image.Image(*core.desired_video_dimensions())

core.set_video_buffer(screen)
core.reset()

print("Emulator reset successfully.")
print("Screen dimensions:", core.desired_video_dimensions())

# 1.4 - Advance emulator frames
for frame in range(1800):
    core.run_frame()

print("1800 frames executed.")

# 1.5 - Capture framebuffer
PICTURE_DIR.mkdir(parents=True, exist_ok=True)

SCREENSHOT_PATH = PICTURE_DIR / "libmgba_test.png"

screen.to_pil().convert("RGB").save(SCREENSHOT_PATH)

print("Screenshot captured:", SCREENSHOT_PATH.is_file())

# 1.6 - Test A button input
for frame in range(300):
    core.run_frame()

screen.to_pil().convert("RGB").save(
    PICTURE_DIR / "libmgba_before_input.png"
)

core.add_keys(3)

for frame in range(10):
    core.run_frame()

core.clear_keys(3)

for interval in range(1, 5):
    for frame in range(120):
        core.run_frame()

    screen.to_pil().convert("RGB").save(
        PICTURE_DIR / f"libmgba_transition_{interval}.png"
    )

print("Button input test completed.")

# 1.7 - Enter saved game
core.add_keys(0)

for frame in range(10):
    core.run_frame()

core.clear_keys(0)

for frame in range(600):
    core.run_frame()

screen.to_pil().convert("RGB").save(
    PICTURE_DIR / "libmgba_saved_game.png"
)

print("Saved game entry test completed.")