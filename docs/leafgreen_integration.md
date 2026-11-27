# Pokemon LeafGreen Integration

## Overview

Pokemon LeafGreen Rev 1 was integrated as the second supported
game in the automated shiny starter hunting application.

Due to the similarities between FireRed and LeafGreen, the
existing emulator, automation macro, computer vision
configuration, reference dataset, and graphical interface
were reused.

Only the game registry required modification to introduce
LeafGreen support.

## Game Configuration

| Property | Configuration |
|---|---|
| Game | Pokemon LeafGreen Rev 1 |
| Emulator | mGBA |
| Save size | 131072 bytes |
| Target FPS | 59.7275 |
| Macro | firered_main_macro |
| Vision configuration | firered_leafgreen |

### Supported Starters

| Pokemon | Species ID |
|---|---|
| Bulbasaur | 001 |
| Charmander | 004 |
| Squirtle | 007 |

## Normal Hunting Experiment

Three permanent LeafGreen profiles were created using the
integrated manual preparation interface, one for each
supported starter.

Two instances of each profile were launched concurrently
to evaluate compatibility with the existing automation
and computer vision pipeline.

### Experimental Results

| Target | Instances | Rotations | Valid Encounters | Failures | Encounters/min |
|---|---:|---:|---:|---:|---:|
| Bulbasaur | 2 | 45 | 45 | 0 | 21.30 |
| Charmander | 2 | 46 | 46 | 0 | 21.47 |
| Squirtle | 2 | 48 | 48 | 0 | 22.46 |
| Total | 6 | 139 | 139 | 0 | 65.23 |

All 139 rotations produced valid encounters, resulting
in a rotation success rate of 100%.

The combined encounter rate was calculated by summing
the displayed encounter rates of the six instances.

![LeafGreen concurrent hunting](figures/gui/hunting_page/leafgreen_verification.png)

*Six concurrent LeafGreen instances following completion
of the normal hunting experiment.*

All six instances were successfully stopped and closed.
Temporary instance directories were removed, and the
permanent hunting profiles remained available.

## Controlled Shiny Experiment

A separate controlled experiment was conducted using
a LeafGreen save containing a shiny Charmander.

The save was prepared using PKHeX and stored separately
from the permanent hunting profiles.

The existing shiny notification test was reused through
a separate LeafGreen test script:

tests/emulation/test_leafgreen_shiny_notification.py

The shiny Charmander summary was reached manually before
starting the controlled hunting experiment.

A capture-only macro was used for the shiny instance to
preserve the prepared encounter. The actual computer
vision pipeline evaluated the captured summary without
overriding classifier predictions.

A second instance targeting Bulbasaur continued hunting
using the existing automated reset macro.

### Classification Results

| Classifier | Shiny Charmander | Normal Bulbasaur |
|---|---|---|
| Border | Shiny | Normal |
| Star | Shiny | Normal |
| Palette | Shiny | Normal |
| Shiny votes | 3/3 | 0/3 |
| Final prediction | Shiny | Normal |

The shiny Charmander was successfully identified using
the existing FireRed and LeafGreen vision configuration
without additional classifier training data.

The shiny instance automatically stopped while the
Bulbasaur instance continued hunting.

### Functional Verification

| Verification | Result |
|---|---|
| Shiny summary validation | PASS |
| Shiny classification | PASS |
| Automatic shiny stopping | PASS |
| Shiny notification | PASS |
| Duplicate notification prevention | PASS |
| Original emulator core preservation | PASS |
| Original framebuffer preservation | PASS |
| Shiny screenshot preservation | PASS |
| Independent continued hunting | PASS |
| Battery save export | PASS |
| Export size validation | PASS |
| Temporary instance cleanup | PASS |
| Permanent profile integrity | PASS |
| Controlled source save integrity | PASS |
| Process exit code zero | PASS |

The exported battery save was successfully created with
a size of 131072 bytes.

The original permanent profile saves and metadata were
verified to remain unchanged through byte comparisons.

The controlled source save also remained unchanged.

## Implementation Changes

The following production file was modified:

- profiles/game_registry.py

The following experimental test was added:

- tests/emulation/test_leafgreen_shiny_notification.py

No modifications were required to the existing automation
macro, computer vision classifiers, summary validator,
instance manager, hunting controller, or graphical
interface.

## Experimental Limitations

The normal hunting experiment evaluated rotation
reliability and compatibility with the existing pipeline.

The 100% rotation success rate does not independently
establish classifier accuracy.

The controlled shiny experiment evaluated one shiny
Charmander encounter. Shiny Bulbasaur and shiny Squirtle
were not independently evaluated in LeafGreen.

The controlled shiny was prepared through save
manipulation rather than obtained through natural
hunting.

The capture-only rotation was excluded from hunting
performance measurements.

The exported LeafGreen battery save was not independently
reloaded after export.

The shared automation macro retains FireRed-specific
console messages. This is a cosmetic limitation and
does not affect LeafGreen hunting functionality.

## Conclusion

LeafGreen was successfully integrated into the existing
application through the addition of a game registry entry.

The normal hunting and controlled shiny experiments
demonstrated compatibility with the existing automation,
computer vision, concurrent instance management, and
shiny preservation systems.

These results demonstrate that additional compatible
games can be integrated without duplicating or modifying
the core application architecture.