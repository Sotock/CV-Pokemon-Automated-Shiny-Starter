from instances.hunting_controller import HuntingState
from profiles.game_registry import get_game_config


class ManualTakeover:

    def __init__(self, controller):

        if controller.state != HuntingState.SHINY_FOUND:

            raise RuntimeError(
                "Manual takeover requires a successful shiny detection."
            )

        if controller.finished_at is None:

            raise RuntimeError(
                "Hunting execution has not finished."
            )

        self.instance = controller.instance

        if self.instance.core is None:

            raise RuntimeError("Emulator is unavailable.")

        self.game = self.instance.game

        config = get_game_config(self.game)

        self.target_fps = config["target_fps"]
        self.frame_interval = 1 / self.target_fps

        self.pressed_keys = set()
        self.active = True

    def run_frame(self):

        if not self.active:

            raise RuntimeError("Manual takeover is inactive.")

        self.instance.core.run_frame()

    def get_frame(self):

        return self.instance.screen.to_pil().convert("RGB")

    def press_key(self, key):

        if not self.active:

            return

        self.instance.core.add_keys(key)

        self.pressed_keys.add(key)

    def release_key(self, key):

        if key not in self.pressed_keys:

            return

        self.instance.core.clear_keys(key)

        self.pressed_keys.discard(key)

    def release_all_keys(self):

        for key in tuple(self.pressed_keys):

            self.release_key(key)

    def close(self):

        self.release_all_keys()

        self.active = False