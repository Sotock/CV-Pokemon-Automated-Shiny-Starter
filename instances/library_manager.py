from pathlib import Path
import shutil
from profiles.profile_manager import load_profile
import gc

import mgba.core
import mgba.vfs
import mgba.image
import mgba.log

from instances.instance_manager import create_instance, remove_instance
from importlib import import_module

PROJECT_DIR = Path(__file__).resolve().parent.parent
SAVES_DIR = PROJECT_DIR / "saves"
PICTURE_DIR = PROJECT_DIR / "pictures"


class EmulatorLogger(mgba.log.Logger):
    def log(self, category, level, message):
        if level in (self.FATAL, self.ERROR, self.WARN):
            super().log(category, level, message)


mgba.log.install_default(EmulatorLogger())


class LibraryInstance:

    def __init__(self, profile_name):
        self.profile_name = profile_name
        self.instance_id = None
        self.instance_dir = None
        self.core = None
        self.screen = None
        self.attempts = 0

        profile = load_profile(profile_name)
        profile_dir = SAVES_DIR / profile_name

        self.game = profile["game"]
        self.emulator = profile["emulator"]
        self.trainer_name = profile["trainer_name"]
        self.target_name = profile["target_name"]
        self.target_species = profile["target_species"]
        self.vision_config = profile["vision_config"]

        if self.emulator != "mGBA":
            raise ValueError(f"Unsupported emulator: {self.emulator}")

        macro_module = import_module(profile["macro"])
        self.run_macro = macro_module.run_macro

        source_rom = PROJECT_DIR / profile["rom_path"]
        source_save = profile_dir / profile["save_file"]

        if not source_rom.is_file():
            raise FileNotFoundError("Profile ROM not found.")

        if not source_save.is_file():
            raise FileNotFoundError("Profile save not found.")

        self.instance_id, self.instance_dir = create_instance()

        try:
            # Create independent ROM and save copies
            self.rom_path = self.instance_dir / source_rom.name
            self.save_path = self.rom_path.with_suffix(".sav")

            shutil.copy2(source_rom, self.rom_path)
            shutil.copy2(source_save, self.save_path)

            # Initialize emulator core
            self.core = mgba.core.load_path(str(self.rom_path))

            if self.core is None:
                raise RuntimeError("ROM failed to load.")

            # Load temporary save
            save = mgba.vfs.open_path(str(self.save_path), "r+")

            if save is None:
                raise RuntimeError("Save file failed to open.")

            if not self.core.load_save(save):
                save.close()
                raise RuntimeError("Save failed to load.")

            # Initialize framebuffer
            self.screen = mgba.image.Image(
                *self.core.desired_video_dimensions()
            )

            self.core.set_video_buffer(self.screen)

            self.picture_dir = PICTURE_DIR / self.instance_id
            self.picture_dir.mkdir(parents=True, exist_ok=True)

            print(f"[{self.instance_id}] Instance initialized.")

        except Exception:
            self.close()
            raise

    def run_attempt(self):
        if self.core is None:
            raise RuntimeError("Instance is closed.")

        self.attempts += 1

        screenshot_path = self.picture_dir / f"attempt_{self.attempts}.png"

        print(f"[{self.instance_id}] Attempt {self.attempts}")

        self.run_macro(self.core, self.screen, screenshot_path)

        return screenshot_path

    def close(self):
        # Release emulator resources before deleting files
        self.core = None
        gc.collect()

        self.screen = None

        if self.instance_dir is not None:
            if self.instance_dir.exists():
                remove_instance(self.instance_dir)

            print(f"[{self.instance_id}] Instance closed.")