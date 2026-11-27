from pathlib import Path
from importlib import import_module
import shutil
import gc

import cv2
import numpy as np

import mgba.core
import mgba.vfs
import mgba.image
import mgba.log

from profiles.profile_manager import load_profile
from instances.instance_manager import (
    create_instance,
    remove_instance
)

from vision.shiny_detector import ShinyDetector


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

        self.on_frame = None

        # Rotation and encounter statistics
        self.attempts = 0
        self.completed_rotations = 0
        self.valid_encounters = 0
        self.failed_rotations = 0
        self.consecutive_failures = 0
        self.shinies_found = 0

        # Computer vision
        self.detector = None
        self.last_result = None

        profile = load_profile(profile_name)

        profile_dir = SAVES_DIR / profile_name

        self.game = profile["game"]
        self.emulator = profile["emulator"]
        self.trainer_name = profile["trainer_name"]
        self.target_name = profile["target_name"]
        self.target_species = profile["target_species"]
        self.vision_config = profile["vision_config"]

        if self.emulator != "mGBA":

            raise ValueError(
                f"Unsupported emulator: {self.emulator}"
            )

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
            self.rom_path = (
                    self.instance_dir / source_rom.name
            )

            self.save_path = self.rom_path.with_suffix(".sav")

            shutil.copy2(source_rom, self.rom_path)
            shutil.copy2(source_save, self.save_path)

            # Initialize emulator core
            self.core = mgba.core.load_path(
                str(self.rom_path)
            )

            if self.core is None:

                raise RuntimeError("ROM failed to load.")

            # Load temporary save
            save = mgba.vfs.open_path(
                str(self.save_path), "r+"
            )

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

            self.picture_dir.mkdir(
                parents=True,
                exist_ok=True
            )

            print(f"[{self.instance_id}] Instance initialized.")

        except Exception:

            self.close()

            raise

    def run_attempt(self):

        if self.core is None:

            raise RuntimeError("Instance is closed.")

        self.attempts += 1

        screenshot_path = (
                self.picture_dir
                / "encounter.png"
        )

        print(
            f"[{self.instance_id}] Attempt {self.attempts}"
        )

        macro_arguments = {}

        if self.on_frame is not None:

            macro_arguments["on_frame"] = self.on_frame

        # Sapphire selects the starter through Birch's bag.
        if self.game == "Pokemon Sapphire Rev 2":

            macro_arguments["target_species"] = (
                self.target_species
            )

        self.run_macro(
            self.core,
            self.screen,
            screenshot_path,
            **macro_arguments
        )

        return screenshot_path

    def get_frame_bgr(self):

        if self.core is None or self.screen is None:

            raise RuntimeError("Framebuffer unavailable.")

        frame = self.screen.to_pil().convert("RGB")

        return cv2.cvtColor(
            np.asarray(frame),
            cv2.COLOR_RGB2BGR
        )

    def classify_frame(self):

        if self.detector is None:

            self.detector = ShinyDetector(
                self.vision_config
            )

        image = self.get_frame_bgr()

        valid_summary = self.detector.validate_summary(
            image,
            self.target_species
        )

        # Invalid summaries bypass shiny classification
        if not valid_summary:

            self.last_result = {
                "valid_summary": False,
                "border": None,
                "star": None,
                "palette": None,
                "votes": None,
                "is_shiny": None
            }

            return self.last_result

        result = self.detector.predict(
            image,
            self.target_species
        )

        result["valid_summary"] = True

        self.last_result = result

        return self.last_result

    def run_classified_attempt(self):

        self.last_result = None

        screenshot_path = self.run_attempt()

        result = self.classify_frame()

        self.completed_rotations += 1

        if not result["valid_summary"]:

            self.failed_rotations += 1
            self.consecutive_failures += 1

            print(
                f"[{self.instance_id}] "
                "Invalid summary detected."
            )

            print(
                f"[{self.instance_id}] "
                "Shiny classification bypassed."
            )

        else:

            self.valid_encounters += 1
            self.consecutive_failures = 0

            if result["is_shiny"]:

                self.shinies_found += 1

            print(
                f"[{self.instance_id}] "
                "Classification results:"
            )

            print("Border:", result["border"])
            print("Star:", result["star"])
            print("Palette:", result["palette"])
            print(f"Shiny votes: {result['votes']}/3")

            print(
                "Prediction:",
                "Shiny" if result["is_shiny"] else "Normal"
            )

        print(f"[{self.instance_id}] Rotation statistics:")
        print("Completed rotations:", self.completed_rotations)
        print("Valid encounters:", self.valid_encounters)
        print("Failed rotations:", self.failed_rotations)
        print("Consecutive failures:", self.consecutive_failures)
        print("Shinies found:", self.shinies_found)

        return screenshot_path, result

    def get_statistics(self):

        success_rate = 0.0

        if self.completed_rotations > 0:

            success_rate = (
                    self.valid_encounters
                    / self.completed_rotations
                    * 100
            )

        return {
            "attempts": self.attempts,
            "completed_rotations": self.completed_rotations,
            "valid_encounters": self.valid_encounters,
            "failed_rotations": self.failed_rotations,
            "consecutive_failures": self.consecutive_failures,
            "shinies_found": self.shinies_found,
            "success_rate": success_rate
        }

    def close(self):

        # Release emulator resources before deleting files
        self.on_frame = None

        self.core = None

        gc.collect()

        self.screen = None
        self.detector = None

        if self.instance_dir is not None:

            if self.instance_dir.exists():

                remove_instance(self.instance_dir)

            print(f"[{self.instance_id}] Instance closed.")