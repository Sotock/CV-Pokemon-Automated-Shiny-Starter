from pathlib import Path
import sys

import tkinter as tk
from time import perf_counter

from gui.emulator_view import EmulatorView

PROJECT_DIR = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(PROJECT_DIR))

from instances.manual_session import ManualSession

from tkinter import messagebox
from profiles.profile_manager import load_profile


GAME = "Pokemon FireRed Rev 1"
STARTER = "Bulbasaur"
TRAINER_NAME = "TEST"


def test_initialization():

    session = ManualSession(
        GAME,
        STARTER,
        TRAINER_NAME
    )

    instance_dir = session.instance_dir

    try:
        print("Profile:", session.profile_name)
        print("Game:", session.game)
        print("Starter:", session.starter)
        print("Trainer:", session.trainer_name)
        print("Target FPS:", session.target_fps)

        assert session.rom_path.is_file()
        assert session.save_path.is_file()

        assert (
                session.save_path.stat().st_size
                == session.save_size
        )

        assert session.save_path.read_bytes() == (
                b"\xff" * session.save_size
        )

        print("ROM copy: PASS")
        print("Fresh battery save: PASS")

        for _ in range(120):
            session.run_frame()

        frame = session.get_frame()

        assert frame.size == (240, 160)
        assert frame.mode == "RGB"

        print("Framebuffer size:", frame.size)
        print("Framebuffer mode:", frame.mode)
        print("Frame execution: PASS")

        session.press_key(0)
        session.run_frame()
        session.release_key(0)
        session.release_all_keys()

        print("Keyboard input API: PASS")

    finally:
        session.close()

    assert not instance_dir.exists()

    print("Temporary instance cleanup: PASS")

def test_manual_gameplay():

    session = ManualSession(
        GAME,
        STARTER,
        TRAINER_NAME
    )

    instance_dir = session.instance_dir

    root = tk.Tk()
    root.title("Manual Gameplay Test")
    root.resizable(False, False)

    view = EmulatorView(
        root,
        session,
        scale=3
    )

    view.pack()

    def close_window():
        view.stop()
        root.destroy()

    root.protocol(
        "WM_DELETE_WINDOW",
        close_window
    )

    start_time = perf_counter()

    try:
        view.start()
        root.mainloop()

    finally:
        elapsed = perf_counter() - start_time

        session.close()

        print()
        print("--- Manual Gameplay Results ---")
        print("Frames rendered:", view.frame_count)
        print(f"Elapsed time: {elapsed:.2f} seconds")

        if elapsed > 0:
            print(
                f"Average FPS: "
                f"{view.frame_count / elapsed:.2f}"
            )

    assert not instance_dir.exists()

    print("Temporary instance cleanup: PASS")

def test_profile_finalization():

    session = ManualSession(
        GAME,
        STARTER,
        TRAINER_NAME
    )

    instance_dir = session.instance_dir
    metadata_path = None

    root = tk.Tk()
    root.title(f"Prepare Profile - {session.profile_name}")
    root.resizable(False, False)

    instructions = tk.Label(
        root,
        text=(
            f"Target: {session.starter}\n"
            "Reach the selected Poké Ball and save in-game "
            "before finalizing."
        ),
        pady=10
    )

    instructions.pack()

    view = EmulatorView(root, session, scale=3)
    view.pack()

    def finalize_profile():
        nonlocal metadata_path

        confirmed = messagebox.askyesno(
            "Finalize Profile",
            "Have you saved in-game in front of the "
            f"{session.starter} Poké Ball?"
        )

        if not confirmed:
            view.display.focus_set()
            return

        view.stop()

        try:
            metadata_path = session.finalize()

        except Exception as error:
            messagebox.showerror(
                "Finalization Failed",
                str(error)
            )

            if session.core is not None:
                view.start()

            return

        messagebox.showinfo(
            "Profile Created",
            session.profile_name
        )

        root.destroy()

    def cancel_profile():

        confirmed = messagebox.askyesno(
            "Cancel Profile",
            "Discard this temporary preparation session?"
        )

        if confirmed:
            view.stop()
            root.destroy()

        else:
            view.display.focus_set()

    controls = tk.Frame(root)
    controls.pack(pady=10)

    tk.Button(
        controls,
        text="Finalize Profile",
        command=finalize_profile
    ).pack(side=tk.LEFT, padx=5)

    tk.Button(
        controls,
        text="Cancel",
        command=cancel_profile
    ).pack(side=tk.LEFT, padx=5)

    root.protocol(
        "WM_DELETE_WINDOW",
        cancel_profile
    )

    try:
        view.start()
        root.mainloop()

        if metadata_path is not None:

            prepared_save = session.save_path.read_bytes()
            permanent_save = metadata_path.parent / "game.sav"

            assert permanent_save.is_file()
            assert permanent_save.read_bytes() == prepared_save

            profile = load_profile(session.profile_name)

            assert profile["target_name"] == STARTER
            assert profile["trainer_name"] == TRAINER_NAME

            print("\n--- Profile Finalization Results ---")
            print("Profile:", profile["name"])
            print("Species:", profile["target_species"])
            print("Permanent save creation: PASS")
            print("Save byte equality: PASS")
            print("Profile validation: PASS")

        else:
            print("Profile preparation cancelled.")

    finally:
        session.close()

    assert not instance_dir.exists()

    print("Temporary instance cleanup: PASS")

    if metadata_path is not None:
        assert metadata_path.is_file()
        assert permanent_save.is_file()

        print("Permanent profile preservation: PASS")
        print("Profile finalization: PASS")

if __name__ == "__main__":

    test_profile_finalization()

    print()
    print("Manual session test completed.")