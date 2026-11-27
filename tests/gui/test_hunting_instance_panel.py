from pathlib import Path
import sys

PROJECT_DIR = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(PROJECT_DIR))

import tkinter as tk
from tkinter import ttk

from PIL import Image

from gui.hunting_instance_panel import (
    HuntingInstancePanel
)


def test_hunting_instance_panel():

    root = tk.Tk()

    root.title("Hunting Instance Panel Verification")

    callbacks = {
        "stop": 0,
        "takeover": 0,
        "export": 0
    }

    def stop():

        callbacks["stop"] += 1

        panel.update_status("Stopped")

        print("Stop callback: PASS")

    def takeover():

        callbacks["takeover"] += 1

        panel.update_status("Manual Gameplay")

        print("Manual takeover callback: PASS")

    def export():

        callbacks["export"] += 1

        panel.update_status("Exported")

        print("Export callback: PASS")

    panel = HuntingInstancePanel(
        root,
        profile_name="FireRed ASH Bulbasaur",
        target="Bulbasaur",
        on_stop=stop,
        on_takeover=takeover,
        on_export=export
    )

    panel.pack(
        padx=15,
        pady=15,
        fill="both",
        expand=True
    )

    panel.update_instance_id("TEST001")

    dataset_dir = (
            PROJECT_DIR
            / "dataset"
            / "firered_leafgreen"
            / "captures"
    )

    normal_path = (
            dataset_dir / "normal" / "001.png"
    )

    shiny_path = (
            dataset_dir / "shiny" / "001.png"
    )

    with Image.open(normal_path) as image:

        normal_frame = image.convert("RGB")

    with Image.open(shiny_path) as image:

        shiny_frame = image.convert("RGB")

    def show_normal():

        panel.update_framebuffer(normal_frame)

        panel.update_status("Hunting")

        panel.update_statistics({
            "completed_rotations": 24,
            "valid_encounters": 23,
            "failed_rotations": 1,
            "encounters_per_minute": 12.64,
            "success_rate": 95.8333,
            "shinies_found": 0
        })

        panel.update_classification({
            "valid_summary": True,
            "border": False,
            "star": False,
            "palette": False
        })

    def show_shiny():

        panel.update_framebuffer(shiny_frame)

        panel.update_status("Shiny Found")

        panel.update_statistics({
            "completed_rotations": 25,
            "valid_encounters": 24,
            "failed_rotations": 1,
            "encounters_per_minute": 12.64,
            "success_rate": 96.0,
            "shinies_found": 1
        })

        panel.update_classification({
            "valid_summary": True,
            "border": True,
            "star": True,
            "palette": True
        })

    def show_invalid():

        panel.update_status("Hunting")

        panel.update_classification({
            "valid_summary": False
        })

    def show_export_ready():

        panel.update_status("Ready to Export")

    print("\n--- Instance Panel Verification ---")

    show_normal()

    assert panel.status_var.get() == "Hunting"

    assert panel.stop_button.instate(["!disabled"])

    assert panel.takeover_button.instate(["disabled"])

    assert panel.export_button.instate(["disabled"])

    assert (
            panel.statistics["completed_rotations"].get()
            == "24"
    )

    assert (
            panel.statistics["success_rate"].get()
            == "95.83%"
    )

    assert all(
        variable.get() == "Normal"
        for variable in panel.classifier_vars.values()
    )

    print("Normal hunting display: PASS")
    print("Statistics formatting: PASS")

    panel.stop_button.invoke()

    assert callbacks["stop"] == 1

    show_shiny()

    assert panel.stop_button.instate(["disabled"])

    assert panel.takeover_button.instate(["!disabled"])

    assert all(
        variable.get() == "Shiny"
        for variable in panel.classifier_vars.values()
    )

    print("Shiny detection display: PASS")

    panel.takeover_button.invoke()

    assert callbacks["takeover"] == 1

    show_export_ready()

    assert panel.export_button.instate(["!disabled"])

    panel.export_button.invoke()

    assert callbacks["export"] == 1

    show_invalid()

    assert all(
        variable.get() == "Invalid"
        for variable in panel.classifier_vars.values()
    )

    print("Invalid summary display: PASS")

    controls = ttk.LabelFrame(
        root,
        text="Test Controls",
        padding=10
    )

    controls.pack(
        fill="x",
        padx=15,
        pady=(0, 15)
    )

    for label, command in (
            ("Normal Encounter", show_normal),
            ("Shiny Encounter", show_shiny),
            ("Invalid Summary", show_invalid),
            ("Ready to Export", show_export_ready)
    ):

        ttk.Button(
            controls,
            text=label,
            command=command
        ).pack(
            fill="x",
            pady=3
        )

    show_normal()

    print("Automated panel checks: PASS")
    print("Interactive panel verification started.")

    root.mainloop()

    print("\nHunting instance panel verification: PASS")


if __name__ == "__main__":

    test_hunting_instance_panel()