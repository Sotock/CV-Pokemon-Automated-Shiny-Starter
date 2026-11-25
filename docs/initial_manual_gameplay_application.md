# Manual Gameplay and Profile Preparation

## Objective

Provide an integrated manual gameplay environment that allows users to prepare permanent hunting profiles without requiring an external emulator or manual file management.

The implementation consolidates emulator initialization, framebuffer rendering, keyboard input, normal-speed frame pacing, battery save preparation, and profile finalization into reusable application components.

## Implementation

| Component | Responsibility |
|---|---|
| `instances/manual_session.py` | Manual emulator initialization, frame execution, input handling, battery save preparation, and profile finalization. |
| `gui/emulator_view.py` | Framebuffer rendering, keyboard controls, and normal-speed frame scheduling. |
| `profiles/game_registry.py` | Game-specific save size and target frame rate configuration. |
| `profiles/profile_manager.py` | Permanent save creation and metadata generation. |
| `tests/emulation/test_manual_session.py` | Initialization, interactive gameplay, and profile finalization verification. |

### Manual Session Controller

The `ManualSession` class initializes an isolated emulator session using the selected game's configuration.

Each session creates:

- A unique temporary instance directory.
- A temporary copy of the selected ROM.
- A fresh battery save.
- An independent libmGBA emulator core.
- A framebuffer for rendering the current game state.

The controller exposes methods for advancing emulator frames, retrieving framebuffer images, processing button inputs, finalizing prepared saves, and releasing emulator resources.

The controller is independent of Tkinter, allowing emulator functionality to remain separate from the graphical interface.

### Framebuffer Rendering

The `EmulatorView` component retrieves RGB framebuffer images from the emulator session and renders them using Tkinter and Pillow.

FireRed produces a native framebuffer resolution of 240 x 160 pixels. Nearest-neighbor interpolation preserves the original pixel appearance when scaling the display.

| Property | Value |
|---|---|
| Native resolution | 240 x 160 |
| Display scale | 3x |
| Display resolution | 720 x 480 |
| Color format | RGB |
| Scaling method | Nearest neighbor |

Framebuffer dimensions are obtained directly from the emulator session rather than hardcoded into the display component.

### Keyboard Controls

| Keyboard Input | GBA Button |
|---|---|
| Z | A |
| X | B |
| Backspace | Select |
| Enter | Start |
| Right Arrow | Right |
| Left Arrow | Left |
| Up Arrow | Up |
| Down Arrow | Down |
| S | R |
| A | L |

Key press and release events are forwarded to the emulator session. Held buttons are released when the display loses keyboard focus.

### Frame Pacing

Manual gameplay is designed to operate at the original Game Boy Advance frame rate.

The target frame interval is calculated as:

```python
frame_interval = 1.0 / target_fps
```

The display component uses `perf_counter()` to track frame deadlines and schedules subsequent frames using Tkinter's `after()` method.

The target frame rate is obtained from the game registry.

## Profile Preparation Workflow

The manual preparation process consists of:

- Selecting the supported game and target starter.
- Entering the trainer-name metadata.
- Initializing a fresh manual emulator session.
- Completing the game's introduction manually.
- Positioning the player in front of the selected starter's Poké Ball.
- Saving in-game before accepting the starter.
- Finalizing the prepared save as a permanent profile.

During finalization, emulator resources are released before the battery save is copied. The prepared save is checked for its expected size and nonblank contents.

The permanent profile manager then creates the save directory and associated metadata automatically.

Temporary instance cleanup does not remove the finalized permanent profile.

## Verification

### Manual Session Initialization

| Verification | Result |
|---|---|
| Isolated ROM copy | PASS |
| Fresh battery save creation | PASS |
| Expected battery save size | PASS |
| Emulator frame execution | PASS |
| RGB framebuffer retrieval | PASS |
| Native framebuffer dimensions | PASS |
| Keyboard input API execution | PASS |
| Temporary instance cleanup | PASS |

The initialized FireRed battery save contained 131,072 bytes (128 KiB).

### Frame Pacing Performance

An interactive gameplay session was executed to evaluate normal-speed frame pacing.

| Metric | Result |
|---|---:|
| Target frame rate | 59.7275 FPS |
| Reported average frame rate | 59.65 FPS |
| Total frames rendered | 4,477 |
| Elapsed time | 75.05 seconds |
| Approximate deviation from target | 0.13% |

The measured frame rate remained close to the intended Game Boy Advance operating speed.

The results represent a single interactive session and do not establish performance across different hardware configurations or multiple concurrent manual sessions.

### Permanent Profile Finalization

A fresh FireRed game was manually prepared and finalized through the integrated gameplay interface.

The following permanent profile was generated:

```text
saves/
└── FireRed TEST Bulbasaur/
    ├── game.sav
    └── profile.json
```

The generated profile contained the expected configuration:

| Property | Value |
|---|---|
| Profile name | FireRed TEST Bulbasaur |
| Game | Pokemon FireRed Rev 1 |
| Trainer | TEST |
| Target | Bulbasaur |
| Species ID | 001 |
| Emulator | mGBA |
| Macro | macros.firered_main_macro |
| Vision configuration | firered_leafgreen |

### Finalization Results

| Verification | Result |
|---|---|
| Permanent save creation | PASS |
| Prepared and permanent save byte equality | PASS |
| Generated metadata validation | PASS |
| Temporary instance cleanup | PASS |
| Permanent profile preservation | PASS |

The permanent save matched the prepared battery save byte-for-byte and remained available following temporary instance cleanup.

### Hunting Compatibility

The newly created profile was subsequently used for an automated hunting attempt with integrated computer vision classification.

The macro successfully executed, and the combined shiny detector returned zero shiny votes. Live framebuffer classification and saved screenshot classification produced identical results.

Temporary instance cleanup completed successfully, and the permanent battery save remained unchanged.

This verifies compatibility between manually prepared profiles and the automated hunting implementation.

## Limitations

- Save size and nonblank data checks do not independently establish complete battery save integrity or correct player positioning.
- Recovery following unsuccessful profile finalization requires additional handling because emulator resources are released before permanent save creation.
- Audio output is not implemented.
- The reusable gameplay component has been verified through a test interface rather than the complete production graphical application.
- Compatibility with additional games requires game-specific verification.

## Conclusion

The integrated manual gameplay implementation successfully provides reusable emulator control, framebuffer rendering, keyboard input, and normal-speed frame pacing.

Permanent hunting profiles can be prepared directly through the application without manual save copying, external emulator interaction, or metadata editing.

The resulting profiles are compatible with automated emulator instances and computer vision classification while preserving the original permanent battery saves.