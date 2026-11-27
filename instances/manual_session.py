from pathlib import Path
import shutil
import gc

import mgba.core
import mgba.image
import mgba.vfs
import mgba.log

from instances.instance_manager import (
    create_instance,
    remove_instance
)

from profiles.game_registry import get_game_config

from profiles.profile_manager import (
    generate_profile_metadata,
    generate_unique_profile_name,
    create_profile
)


PROJECT_DIR = Path(__file__).resolve().parent.parent


class EmulatorLogger(mgba.log.Logger):

    def log(self, category, level, message):
        if level in (self.FATAL, self.ERROR, self.WARN):
            super().log(category, level, message)


mgba.log.install_default(EmulatorLogger())


class ManualSession:

    def __init__(self, game, starter, trainer_name):

        self.metadata = generate_profile_metadata(
            game, starter, trainer_name
        )

        config = get_game_config(game)

        self.game = game
        self.starter = starter
        self.trainer_name = self.metadata["trainer_name"]

        self.profile_name = generate_unique_profile_name(
            self.game,
            self.starter,
            self.trainer_name
        )

        self.metadata["name"] = self.profile_name

        self.save_size = config["save_size"]
        self.target_fps = config["target_fps"]
        self.frame_interval = 1.0 / self.target_fps

        self.core = None
        self.screen = None
        self.instance_id = None
        self.instance_dir = None
        self.finalized = False

        if config["emulator"] != "mGBA":
            raise ValueError("Unsupported emulator.")

        source_rom = PROJECT_DIR / config["rom_path"]

        if not source_rom.is_file():
            raise FileNotFoundError("Game ROM not found.")

        self.instance_id, self.instance_dir = create_instance()

        try:
            # Prepare isolated ROM and battery save
            self.rom_path = self.instance_dir / source_rom.name
            self.save_path = self.rom_path.with_suffix(".sav")

            shutil.copy2(source_rom, self.rom_path)

            self.save_path.write_bytes(
                b"\xff" * self.save_size
            )

            self.initialize_emulator()

            print(
                f"[{self.instance_id}] "
                f"Manual session initialized: "
                f"{self.profile_name}"
            )

        except Exception:
            self.close()
            raise

    def initialize_emulator(self):

        if self.core is not None:
            raise RuntimeError("Emulator is already initialized.")

        try:

            self.core = mgba.core.load_path(
                str(self.rom_path)
            )

            if self.core is None:
                raise RuntimeError("Unable to load ROM.")

            save = mgba.vfs.open_path(
                str(self.save_path), "r+"
            )

            if save is None:
                raise RuntimeError("Unable to open battery save.")

            if not self.core.load_save(save):
                save.close()
                raise RuntimeError("Unable to attach battery save.")

            self.screen = mgba.image.Image(
                *self.core.desired_video_dimensions()
            )

            self.core.set_video_buffer(self.screen)
            self.core.reset()

        except Exception:
            self.close_emulator()
            raise

    def run_frame(self):
        if self.core is None:
            raise RuntimeError("Manual session is closed.")

        self.core.run_frame()

    def get_frame(self):
        if self.screen is None:
            raise RuntimeError("Framebuffer unavailable.")

        return self.screen.to_pil().convert("RGB")

    def press_key(self, key):
        if self.core is not None:
            self.core.add_keys(key)

    def release_key(self, key):
        if self.core is not None:
            self.core.clear_keys(key)

    def release_all_keys(self):
        if self.core is not None:
            for key in range(10):
                self.core.clear_keys(key)

    def close_emulator(self):
        self.release_all_keys()

        self.core = None
        gc.collect()

        self.screen = None

    def validate_prepared_save(self):

        if not self.save_path.is_file():
            raise FileNotFoundError("Prepared save not found.")

        save_data = self.save_path.read_bytes()

        if len(save_data) != self.save_size:
            raise ValueError("Unexpected battery save size.")

        if save_data == b"\xff" * self.save_size:
            raise ValueError(
                "Prepared save is blank. "
                "Save through the in-game menu before finalizing."
            )

    def finalize(self):

        if self.finalized:
            raise RuntimeError("Profile already finalized.")

        if self.instance_dir is None:
            raise RuntimeError("Manual session unavailable.")

        if not self.instance_dir.exists():
            raise RuntimeError("Manual session has been removed.")

        # Check the prepared save before closing
        # the active emulator.
        self.validate_prepared_save()

        # Release emulator resources before copying.
        self.close_emulator()

        # Verify the flushed battery save.
        self.validate_prepared_save()

        metadata_path = create_profile(
            self.game,
            self.starter,
            self.trainer_name,
            self.save_path
        )

        self.profile_name = metadata_path.parent.name
        self.metadata["name"] = self.profile_name

        self.finalized = True

        print(
            f"[{self.instance_id}] "
            f"Profile finalized: {self.profile_name}"
        )

        return metadata_path

    def close(self):
        self.close_emulator()

        if self.instance_dir is not None:
            if self.instance_dir.exists():
                remove_instance(self.instance_dir)

        print(f"[{self.instance_id}] Manual session closed.")