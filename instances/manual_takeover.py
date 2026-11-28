from instances.hunting_controller import HuntingState
from profiles.game_registry import get_game_config

# Provides manual control of an emulator following successful shiny detection.
class ManualTakeover:
    # Validates the hunting state and retains the original emulator instance.
    def __init__(self, controller):
        if controller.state != HuntingState.SHINY_FOUND:
            raise RuntimeError("Manual takeover requires a successful shiny detection.")
        if controller.finished_at is None:
            raise RuntimeError("Hunting execution has not finished.")

        self.instance = controller.instance
        if self.instance.core is None:
            raise RuntimeError("Emulator is unavailable.")

        self.game = self.instance.game
        config = get_game_config(self.game)
        self.target_fps = config["target_fps"]
        self.frame_interval = 1 / self.target_fps
        self.pressed_keys = set()
        self.active = True

    # Advances the retained emulator by one frame.
    def run_frame(self):
        if not self.active:
            raise RuntimeError("Manual takeover is inactive.")
        self.instance.core.run_frame()

    # Retrieves the current framebuffer as an RGB image.
    def get_frame(self):
        return self.instance.screen.to_pil().convert("RGB")

    # Presses and tracks the specified GBA button.
    def press_key(self, key):
        if not self.active:
            return
        self.instance.core.add_keys(key)
        self.pressed_keys.add(key)

    # Releases the specified GBA button if currently pressed.
    def release_key(self, key):
        if key not in self.pressed_keys:
            return
        self.instance.core.clear_keys(key)
        self.pressed_keys.discard(key)

    # Releases all tracked buttons to prevent retained input.
    def release_all_keys(self):
        for key in tuple(self.pressed_keys):
            self.release_key(key)

    # Ends manual control while preserving the emulator for save export.
    def close(self):
        self.release_all_keys()
        self.active = False