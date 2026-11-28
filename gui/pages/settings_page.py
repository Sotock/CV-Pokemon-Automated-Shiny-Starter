import tkinter as tk
from tkinter import ttk, messagebox

from gui.settings import (
    load_settings,
    save_settings,
    default_settings,
    normalize_key,
    format_key,
    DEFAULT_AUDIO_SETTINGS
)

# Provides configurable keyboard controls and application audio preferences.
class SettingsPage(ttk.Frame):
    # Initializes saved preferences and settings controls.
    def __init__(self, parent, application):
        super().__init__(parent)
        self.application = application
        self.settings = load_settings()

        self.key_buttons = {}
        self.audio_vars = {}
        self.selected_binding = None

        self.status_var = tk.StringVar(
            value="Configure keyboard and audio preferences."
        )

        self.create_widgets()

    # Creates the settings page and its configuration sections.
    def create_widgets(self):
        ttk.Label(
            self,
            text="Settings",
            font=("Segoe UI", 20, "bold")
        ).pack(anchor="w")

        ttk.Label(
            self,
            text="Customize gameplay controls and application audio.",
            style="Secondary.TLabel"
        ).pack(anchor="w", pady=(5, 15))

        ttk.Separator(
            self,
            orient="horizontal"
        ).pack(fill="x", pady=(0, 15))

        self.create_keyboard_settings()
        self.create_audio_settings()
        self.create_settings_actions()

    # Creates keyboard binding controls for all supported GBA buttons.
    def create_keyboard_settings(self):
        container = ttk.LabelFrame(
            self,
            text="Keyboard Controls",
            padding=15
        )
        container.pack(fill="x", pady=(0, 15))

        ttk.Label(
            container,
            text="Select a binding and press the desired keyboard key.",
            style="Secondary.TLabel"
        ).pack(anchor="w", pady=(0, 10))

        bindings_frame = ttk.Frame(container)
        bindings_frame.pack(fill="x")
        bindings_frame.columnconfigure(1, weight=1)
        bindings_frame.columnconfigure(3, weight=1)

        button_groups = (
            ("A", "B", "Start", "Select", "L"),
            ("Up", "Down", "Left", "Right", "R")
        )

        for group_index, buttons in enumerate(button_groups):
            label_column = group_index * 2
            button_column = label_column + 1

            for row, button in enumerate(buttons):
                ttk.Label(
                    bindings_frame,
                    text=button
                ).grid(
                    row=row,
                    column=label_column,
                    sticky="w",
                    padx=(0, 10),
                    pady=3
                )

                key_button = ttk.Button(
                    bindings_frame,
                    text=format_key(
                        self.settings["key_bindings"][button]
                    ),
                    width=18,
                    command=lambda name=button: self.begin_key_capture(name)
                )
                key_button.grid(
                    row=row,
                    column=button_column,
                    sticky="ew",
                    padx=(0, 20),
                    pady=3
                )

                key_button.bind("<KeyPress>", self.capture_key)
                key_button.bind("<FocusOut>", self.cancel_key_capture)
                self.key_buttons[button] = key_button

    # Creates independent toggles for each application audio feature.
    def create_audio_settings(self):
        container = ttk.LabelFrame(
            self,
            text="Audio Settings",
            padding=15
        )
        container.pack(fill="x", pady=(0, 15))

        audio_options = {
            "preparation_music": "Play music during game preparation",
            "shiny_notification": "Play shiny notification sound",
            "export_fanfare": "Play fanfare after successful save export"
        }

        for name, description in audio_options.items():
            variable = tk.BooleanVar(
                value=self.settings["audio"][name]
            )
            self.audio_vars[name] = variable

            ttk.Checkbutton(
                container,
                text=description,
                variable=variable,
                command=self.mark_unsaved
            ).pack(anchor="w", pady=4)

    # Creates the settings status message and preference management buttons.
    def create_settings_actions(self):
        ttk.Label(
            self,
            textvariable=self.status_var,
            style="Secondary.TLabel",
            wraplength=700
        ).pack(anchor="w", pady=(0, 10))

        buttons = ttk.Frame(self)
        buttons.pack(fill="x")

        ttk.Button(
            buttons,
            text="Restore Defaults",
            command=self.restore_defaults
        ).pack(side="left")

        ttk.Button(
            buttons,
            text="Save Settings",
            style="Accent.TButton",
            command=self.save_preferences
        ).pack(side="right")

    # Activates keyboard capture for the selected GBA button.
    def begin_key_capture(self, button):
        self.cancel_key_capture()
        self.selected_binding = button

        key_button = self.key_buttons[button]
        key_button.configure(text="Press a key...")
        key_button.focus_set()

        self.status_var.set(
            f"Press a keyboard key to bind {button}. "
            "Press Escape to cancel."
        )

    # Validates and assigns a captured keyboard key.
    def capture_key(self, event):
        if self.selected_binding is None:
            return

        if event.keysym == "Escape":
            self.cancel_key_capture()
            return "break"

        # Exclude modifier and navigation keys unsuitable for gameplay binding.
        unsupported_keys = {
            "Shift_L",
            "Shift_R",
            "Control_L",
            "Control_R",
            "Alt_L",
            "Alt_R",
            "Meta_L",
            "Meta_R",
            "Super_L",
            "Super_R",
            "Caps_Lock",
            "Num_Lock",
            "Scroll_Lock",
            "Tab",
            "ISO_Left_Tab",
            "NoSymbol"
        }

        if event.keysym in unsupported_keys:
            self.status_var.set(
                "Select a non-modifier gameplay key."
            )
            return "break"

        key = normalize_key(event.keysym)
        button = self.selected_binding

        # Prevent multiple GBA buttons from sharing the same keyboard key.
        for other_button, other_key in self.settings["key_bindings"].items():
            if other_button != button and other_key == key:
                self.status_var.set(
                    f"{format_key(key)} is already assigned "
                    f"to {other_button}. Select another key."
                )
                return "break"

        self.settings["key_bindings"][button] = key
        self.selected_binding = None

        self.refresh_key_buttons()
        self.mark_unsaved()

        return "break"

    # Cancels active keyboard capture without changing the binding.
    def cancel_key_capture(self, event=None):
        if self.selected_binding is None:
            return

        self.selected_binding = None
        self.refresh_key_buttons()

        self.status_var.set(
            "Keyboard binding selection cancelled."
        )

    # Updates keyboard binding buttons to display their current assignments.
    def refresh_key_buttons(self):
        for button, widget in self.key_buttons.items():
            widget.configure(
                text=format_key(
                    self.settings["key_bindings"][button]
                )
            )

    # Indicates that modified preferences have not yet been saved.
    def mark_unsaved(self):
        self.status_var.set(
            "Unsaved changes. Select Save Settings to apply."
        )

    # Restores default keyboard bindings and audio toggles after confirmation.
    def restore_defaults(self):
        self.cancel_key_capture()

        confirmed = messagebox.askyesno(
            "Restore Default Settings",
            "Restore default keyboard bindings and audio toggles?",
            parent=self.winfo_toplevel()
        )

        if not confirmed:
            return

        defaults = default_settings()
        self.settings["key_bindings"] = defaults["key_bindings"]
        self.settings["audio"] = defaults["audio"]

        self.refresh_key_buttons()

        for name, variable in self.audio_vars.items():
            variable.set(DEFAULT_AUDIO_SETTINGS[name])

        self.status_var.set(
            "Defaults restored. Select Save Settings to apply."
        )

    # Validates and saves modified keyboard and audio preferences.
    def save_preferences(self):
        self.cancel_key_capture()

        for name, variable in self.audio_vars.items():
            self.settings["audio"][name] = variable.get()

        # Preserve volume changes made during preparation.
        current_settings = load_settings()
        current_settings["key_bindings"] = self.settings["key_bindings"].copy()
        current_settings["audio"] = self.settings["audio"].copy()

        try:
            save_settings(current_settings)
        except (OSError, ValueError) as error:
            messagebox.showerror(
                "Settings Save Failed",
                str(error),
                parent=self.winfo_toplevel()
            )
            return

        self.settings = current_settings
        self.status_var.set("Settings saved successfully.")