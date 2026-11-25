from pathlib import Path
import shutil
import mgba.core
import mgba.vfs
import mgba.image
import mgba.log

from macros.firered_main_macro import run_macro

PROJECT_DIR = Path(__file__).resolve().parents[2]

ROM_PATH = PROJECT_DIR / "roms" / "Pokemon - FireRed Version (USA, Europe) (Rev 1).gba"
SAVE_PATH = PROJECT_DIR / "saves" / "FireRed Starter" / "game.sav"
TEMP_SAVE = PROJECT_DIR / "temp" / "test_macro.sav"
SCREENSHOT_PATH = PROJECT_DIR / "pictures" / "firered_python_capture.png"

class EmulatorLogger(mgba.log.Logger):
    def log(self, category, level, message):
        if level in (self.FATAL, self.ERROR, self.WARN):
            super().log(category, level, message)


mgba.log.install_default(EmulatorLogger())

# Load ROM
core = mgba.core.load_path(str(ROM_PATH))

if core is None:
    raise RuntimeError("ROM failed to load.")

print("ROM loaded successfully.")

# Load temporary save
TEMP_SAVE.parent.mkdir(parents=True, exist_ok=True)
shutil.copy2(SAVE_PATH, TEMP_SAVE)

save = mgba.vfs.open_path(str(TEMP_SAVE), "r+")

if not core.load_save(save):
    raise RuntimeError("Save failed to load.")

print("Save loaded successfully.")

# Initialize framebuffer
screen = mgba.image.Image(*core.desired_video_dimensions())
core.set_video_buffer(screen)

SCREENSHOT_PATH.parent.mkdir(parents=True, exist_ok=True)

# Execute macro
for attempt in range(1, 6):
    print(f"\nAttempt {attempt}")

    run_macro(
        core,
        screen,
        SCREENSHOT_PATH.parent / f"firered_capture_{attempt}.png"
    )
