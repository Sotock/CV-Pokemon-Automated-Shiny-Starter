# Final Demo ROM Integration and Multiple-Shiny Regression

## 1. Overview

Phase 10.8 completed the final integrated shiny hunting regression
tests and introduced demonstration ROMs with increased shiny odds
for the live project presentation.

The demonstration ROMs allow the application to detect multiple
shiny encounters within a reasonable testing period without
requiring controlled shiny save manipulation.

All four supported games were successfully patched and tested
using the existing application architecture, hunting macros,
computer vision classifiers, and permanent save profiles.

No production hunting macro or computer vision classifier
modifications were required.

## 2. Demonstration ROM Patching

### 2.1 Supported ROMs

| Game | Revision | ROM Size | Modified Bytes |
|---|---|---:|---:|
| FireRed | Rev 1 | 16777216 bytes | 4 |
| LeafGreen | Rev 1 | 16777216 bytes | 4 |
| Ruby | Rev 2 | 16777216 bytes | 4 |
| Sapphire | Rev 2 | 16777216 bytes | 4 |

The intended shiny probability was increased from 1/8192 to
1/256 by modifying four comparison threshold bytes in each ROM.

Each modification replaces the original comparison value of
0x07 with 0xFF.

Unlike the initial KiraPatch implementation, the minimal patch
does not introduce additional RNG reroll routines.

### 2.2 Patch Locations

| Comparison | FireRed | LeafGreen | Ruby | Sapphire |
|---|---|---|---|---|
| 1 | 0x44134 | 0x44134 | 0x40988 | 0x40988 |
| 2 | 0x441AA | 0x441AA | 0x409FE | 0x409FE |
| 3 | 0x444C4 | 0x444C4 | 0x40D14 | 0x40D14 |
| 4 | 0xF17EE | 0xF17C6 | 0x14189A | 0x14189A |

The modifications preserve the original ROM sizes, internal
game identifiers, and revision numbers.

The exact effective shiny probability remains unverified through
complete instruction-level analysis.

### 2.3 Patching Utility

The demonstration ROM generation utility is located at:

tests/emulation/patch_demo_roms.py

The utility performs the following operations:

1. Loads each original ROM.
2. Validates the expected ROM size.
3. Verifies the original SHA-256 hash.
4. Validates the expected comparison instruction bytes.
5. Applies the four threshold modifications.
6. Verifies the number of modified bytes.
7. Writes the demonstration ROM to a separate directory.
8. Verifies the written output.
9. Reports successful and failed patch operations.

Original ROMs are not modified in place.

### 2.4 Directory Organization

The ROM directories are organized as follows:

| Directory | Purpose |
|---|---|
| roms/ | Active ROMs used by the application |
| roms_original/ | Unmodified ROM backups |
| roms_demo/ | Minimal demonstration ROMs |
| roms_shiny_patch/ | Previous KiraPatch ROMs |

All ROM directories containing game binaries must remain excluded
from version control.

The demonstration ROMs retain their original registered filenames.

### 2.5 Profile Compatibility

An initial attempt to redirect the game registry directly to
roms_demo/ resulted in profile validation failures.

The permanent profiles contain registered ROM paths that must
match the corresponding game registry configuration.

Changing the registered ROM directory caused all twelve existing
profiles to fail configuration validation.

The original registry paths were restored, and the demonstration
ROMs were copied into the active roms/ directory.

This resolved the configuration issue without modifying permanent
profile metadata or weakening profile validation.

A dedicated demonstration mode may be considered during the
final application review to eliminate manual ROM replacement.

## 3. Initial Patch Compatibility Comparison

### 3.1 KiraPatch Results

The initial KiraPatch implementation produced substantial
compatibility issues with the existing hunting macros.

| Metric | Result |
|---|---:|
| Configured instances | 10 |
| Completed rotations | 640 |
| Valid encounters | 1 |
| Failed rotations | 639 |
| Shiny encounters | 1 |
| Encounter success rate | 0.16% |

The computer vision system correctly rejected invalid encounter
screenshots.

The exact cause of the macro compatibility issues was not
independently established.

### 3.2 Original ROM Regression

Restoring the original ROMs resolved the observed failures.

| Game | Instances | Valid Encounters | Failures |
|---|---:|---:|---:|
| FireRed | 3 | 13 | 0 |
| LeafGreen | 3 | 12 | 0 |
| Ruby | 3 | 107 | 0 |
| Sapphire | 1 | 34 | 0 |
| Total | 10 | 166 | 0 |

Overall encounter success rate: 100%.

No application modifications were required to restore normal
hunting functionality.

## 4. Initial Minimal Sapphire Patch Testing

### 4.1 Test Configuration

Test date: November 27, 2026

Nine concurrent Sapphire instances were configured:

- Three Mudkip instances.
- Three Torchic instances.
- Three Treecko instances.

The demonstration ROM was tested directly through main.py using
existing permanent hunting profiles.

No controlled shiny source saves were used.

### 4.2 Recorded Seven-Shiny Checkpoint

| Starter | Rotations | Valid Encounters | Failures | Shinies |
|---|---:|---:|---:|---:|
| Mudkip | 846 | 843 | 3 | 2 |
| Torchic | 419 | 417 | 2 | 3 |
| Treecko | 866 | 864 | 2 | 2 |
| Total | 2131 | 2124 | 7 | 7 |

Encounter success rate: 99.67%.

Observed shiny frequency: approximately 1/303.43.

All three Sapphire shiny starter variants were successfully
detected during the same hunting session.

Seven shiny instances were independently preserved while the
remaining two instances continued hunting.

This checkpoint established the functional compatibility of
the minimal Sapphire demonstration ROM.

## 5. Multiple-Shiny Takeover and Export Regression

### 5.1 Test Configuration

Test date: November 28, 2026

A second nine-instance Sapphire session was conducted to verify
sequential manual takeovers and individual save exports.

Three instances were configured for each supported Sapphire
starter.

### 5.2 Recorded Encounter Results

| Starter | Rotations | Valid Encounters | Failures | Shinies |
|---|---:|---:|---:|---:|
| Mudkip | 598 | 593 | 5 | 2 |
| Torchic | 528 | 528 | 0 | 3 |
| Treecko | 598 | 595 | 3 | 2 |
| Total | 1724 | 1716 | 8 | 7 |

Encounter success rate: 99.54%.

Observed shiny frequency: approximately 1/245.14.

These results represent the recorded seven-shiny checkpoint
during the second save export.

### 5.3 Sequential Manual Takeover

Two independently preserved shiny instances were selected for
manual takeover.

| Starter | Instance ID | Valid Encounters | Result |
|---|---|---:|---|
| Treecko | 1374c078 | 22 | Save Exported |
| Mudkip | 89a6e3b4 | 27 | Save Exported |

The user completed the encounters, saved in-game, and exported
the resulting battery saves.

Additional shiny encounters were detected while manual takeover
was active.

This verified that manual gameplay does not prevent other
hunting instances from continuing their automated workflows.

### 5.4 Post-Export Verification

Both exported instances retained their shiny dashboard styling.

Verified behavior included:

- Gold instance borders.
- Ultra Ball watermarks.
- Save Exported status.
- Preserved final gameplay framebuffer.
- Preserved shiny classification results.
- Correct cumulative shiny notification count.
- Continued hunting by unrelated instances.
- Independent export of multiple shiny saves.

After closing the dashboard, temporary instance cleanup and
exported save persistence were confirmed.

Permanent profile byte integrity was not independently rechecked
during this session. Previous controlled regression testing
successfully verified permanent profile preservation.

### 5.5 Regression Results

| Verification | Result |
|---|---|
| Multiple simultaneous shiny discoveries | PASS |
| Independent shiny preservation | PASS |
| Sequential manual takeovers | PASS |
| Continued hunting during manual takeover | PASS |
| Additional shiny detection during takeover | PASS |
| Individual battery save exports | PASS |
| Post-export dashboard styling | PASS |
| Cumulative dashboard counters | PASS |
| Temporary instance cleanup | PASS |
| Export persistence after closure | PASS |

Phase 10.8.2 functional regression completed successfully.

## 6. Final Mixed-Game Demonstration ROM Regression

### 6.1 Test Configuration

Test date: November 28, 2026

All four minimal demonstration ROMs were placed in the active
ROM directory.

Ten concurrent hunting instances were configured through the
main application.

| Game | Configured Instances |
|---|---:|
| FireRed | 3 |
| LeafGreen | 3 |
| Ruby | 3 |
| Sapphire | 1 |
| Total | 10 |

FireRed, LeafGreen, and Ruby each included all three supported
starters.

The Sapphire instance targeted Mudkip.

The test used existing permanent save profiles and unmodified
production hunting macros.

### 6.2 Final Instance Results

The following results were recorded from the final dashboard
screenshot before closure.

| Game | Starter | Rotations | Valid | Failures | Shinies | Encounters/min | Final State |
|---|---|---:|---:|---:|---:|---:|---|
| FireRed | Bulbasaur | 147 | 147 | 0 | 0 | 10.38 | Stopped |
| FireRed | Charmander | 108 | 108 | 0 | 1 | 10.08 | Shiny Found |
| FireRed | Squirtle | 124 | 124 | 0 | 1 | 10.14 | Shiny Found |
| LeafGreen | Bulbasaur | 146 | 146 | 0 | 0 | 10.31 | Stopped |
| LeafGreen | Charmander | 13 | 13 | 0 | 1 | 9.43 | Shiny Found |
| LeafGreen | Squirtle | 147 | 147 | 0 | 0 | 10.40 | Stopped |
| Ruby | Mudkip | 55 | 55 | 0 | 1 | 64.50 | Shiny Found |
| Ruby | Torchic | 107 | 107 | 0 | 1 | 64.69 | Shiny Found |
| Ruby | Treecko | 186 | 186 | 0 | 1 | 66.74 | Shiny Found |
| Sapphire | Mudkip | 16 | 16 | 0 | 1 | 55.21 | Shiny Found |

### 6.3 Results by Game

| Game | Instances | Rotations | Valid Encounters | Failures | Shinies |
|---|---:|---:|---:|---:|---:|
| FireRed | 3 | 379 | 379 | 0 | 2 |
| LeafGreen | 3 | 306 | 306 | 0 | 1 |
| Ruby | 3 | 348 | 348 | 0 | 3 |
| Sapphire | 1 | 16 | 16 | 0 | 1 |
| Total | 10 | 1049 | 1049 | 0 | 7 |

Overall encounter success rate: 100%.

Overall failed rotation rate: 0%.

All four supported demonstration ROMs successfully produced
shiny encounters.

### 6.4 Results by Game Family

| Game Family | Instances | Valid Encounters | Failures | Shinies |
|---|---:|---:|---:|---:|
| FireRed and LeafGreen | 6 | 685 | 0 | 3 |
| Ruby and Sapphire | 4 | 364 | 0 | 4 |
| Total | 10 | 1049 | 0 | 7 |

Both computer vision classification pipelines operated
successfully within the same hunting session.

### 6.5 Shiny Detection Results

| Game | Starter | Encounters Before Shiny | Classification |
|---|---|---:|---|
| FireRed | Charmander | 108 | 3/3 shiny votes |
| FireRed | Squirtle | 124 | 3/3 shiny votes |
| LeafGreen | Charmander | 13 | 3/3 shiny votes |
| Ruby | Mudkip | 55 | Valid battle, valid sprite, shiny palette |
| Ruby | Torchic | 107 | Valid battle, valid sprite, shiny palette |
| Ruby | Treecko | 186 | Valid battle, valid sprite, shiny palette |
| Sapphire | Mudkip | 16 | Valid battle, valid sprite, shiny palette |

All seven detected shiny encounters displayed the expected
shiny coloration in their preserved screenshots.

Five of the six unique supported starter species were detected
as shiny during this session.

Bulbasaur was not detected as shiny before the remaining
instances were manually stopped.

Previous controlled FireRed and LeafGreen evaluations included
successful shiny Bulbasaur classification.

### 6.6 FireRed and LeafGreen Classification

All three detected FireRed and LeafGreen shiny encounters
received unanimous shiny classifications from the following
methods:

- Border classifier.
- Star classifier.
- Palette classifier.

Each shiny encounter exceeded the required two-of-three
majority voting threshold.

Normal encounters continued to receive normal classifications.

### 6.7 Ruby and Sapphire Classification

All four detected Ruby and Sapphire shiny encounters passed:

- Battle screen validation.
- Target sprite validation.
- Shiny palette classification.

The battle-based classification pipeline successfully detected
all three Ruby starter variants and the Sapphire Mudkip variant.

### 6.8 Observed Shiny Frequency

Total valid encounters: 1049

Total shiny encounters: 7

Observed shiny frequency:

7 / 1049 = 0.006673

Observed shiny percentage: approximately 0.67%.

Observed shiny rate: approximately 1/149.86.

Intended demonstration shiny rate: 1/256.

The observed frequency demonstrates accelerated shiny generation
but does not establish the exact effective shiny probability.

### 6.9 Hunting Performance

FireRed and LeafGreen:

- Minimum displayed instance rate: 9.43 encounters/min.
- Maximum displayed instance rate: 10.40 encounters/min.
- Mean displayed instance rate: 10.12 encounters/min.

Ruby and Sapphire:

- Minimum displayed instance rate: 55.21 encounters/min.
- Maximum displayed instance rate: 66.74 encounters/min.
- Mean displayed instance rate: 62.79 encounters/min.

The Ruby and Sapphire instances achieved substantially higher
encounter rates due to their shorter automated hunting macros.

The mean displayed Ruby and Sapphire instance rate was
approximately 6.21 times the FireRed and LeafGreen rate.

These rates were measured over individual instance hunting
durations. Since instances stopped at different times, their
displayed rates should not be summed and interpreted as
sustained simultaneous throughput.

Ruby and Sapphire remain the preferred games for the live
demonstration due to their faster encounter generation.

### 6.10 Final Dashboard State

The final dashboard displayed:

- Configured instances: 10
- Active instances: 0
- Finished instances: 10
- Shinies found: 7

Seven instances stopped automatically after detecting shiny
encounters.

Three remaining normal instances were manually stopped.

All seven shiny instances retained:

- Preserved encounter screenshots.
- Gold instance borders.
- Ultra Ball watermarks.
- Shiny classification results.
- Enabled Manual Takeover buttons.
- Disabled Stop buttons.

The stopped normal instances displayed muted Pokeball watermarks
and disabled action buttons.

The cumulative notification banner correctly displayed seven
shiny encounters.

The latest notification identified the FireRed Squirtle
encounter detected after 124 valid encounters.

## 7. Combined Minimal Patch Evaluation

### 7.1 Recorded Session Results

| Session | Instances | Rotations | Valid | Failures | Shinies |
|---|---:|---:|---:|---:|---:|
| Initial Sapphire regression | 9 | 2131 | 2124 | 7 | 7 |
| Sapphire takeover regression | 9 | 1724 | 1716 | 8 | 7 |
| Final mixed-game regression | 10 | 1049 | 1049 | 0 | 7 |
| Total | 28 | 4904 | 4889 | 15 | 21 |

The combined results include recorded checkpoints from two
Sapphire sessions and the final mixed-game session.

The checkpoints are from separate hunting sessions and are
not cumulative screenshots from the same session.

### 7.2 Aggregate Metrics

Total recorded rotations: 4904

Total valid encounters: 4889

Total failed rotations: 15

Total shiny encounters: 21

Overall encounter success rate:

4889 / 4904 * 100 = 99.69%

Overall failed rotation rate:

15 / 4904 * 100 = 0.31%

Observed shiny frequency:

21 / 4889 = 0.004295

Observed shiny percentage: approximately 0.43%.

Observed shiny rate: approximately 1/232.81.

The combined observed shiny frequency is consistent with the
intended increased shiny probability of approximately 1/256.

However, encounter RNG independence has not been established,
and the recorded results do not constitute a controlled
statistical probability experiment.

### 7.3 Comparison with Initial Patching Attempt

| Metric | KiraPatch | Minimal Demo Patches |
|---|---:|---:|
| Recorded rotations | 640 | 4904 |
| Valid encounters | 1 | 4889 |
| Failed rotations | 639 | 15 |
| Encounter success rate | 0.16% | 99.69% |
| Shiny encounters | 1 | 21 |

The minimal demonstration ROM patches maintained substantially
better compatibility with the existing automated hunting
workflow.

The comparison demonstrates functional compatibility rather
than a controlled performance benchmark.

The final mixed-game session achieved 100% encounter success
without requiring changes to the existing macros or classifiers.

## 8. Demonstration ROM Verification Summary

| Verification | FireRed | LeafGreen | Ruby | Sapphire |
|---|---|---|---|---|
| Minimal patch generation | PASS | PASS | PASS | PASS |
| Existing profile compatibility | PASS | PASS | PASS | PASS |
| Automated macro compatibility | PASS | PASS | PASS | PASS |
| Normal encounter classification | PASS | PASS | PASS | PASS |
| Shiny encounter classification | PASS | PASS | PASS | PASS |
| Automatic shiny stopping | PASS | PASS | PASS | PASS |
| Shiny dashboard styling | PASS | PASS | PASS | PASS |
| Mixed-game concurrent hunting | PASS | PASS | PASS | PASS |

All four supported demonstration ROMs are functionally verified.

## 9. Live Demonstration Readiness

The application can now demonstrate the following functionality
using accelerated shiny encounter generation:

- Support for four Generation III Pokemon games.
- Twelve supported game and starter combinations.
- Six unique supported starter species.
- Up to ten concurrent hunting instances.
- Automated starter encounter generation.
- Real-time emulator framebuffer updates.
- Encounter statistics and failure tracking.
- Two game-family-specific computer vision pipelines.
- Automatic shiny classification.
- Independent shiny instance stopping.
- Multiple simultaneous preserved shiny encounters.
- Visual and audio shiny notifications.
- Manual gameplay takeover.
- Individual battery save exports.
- Successful export fanfare.
- Temporary instance cleanup.
- Persistent exported saves.

The demonstration ROMs only accelerate shiny encounter
availability.

The application continues to classify shiny encounters through
captured screenshots rather than reading internal game values.

The increased shiny probability must be explicitly disclosed
during the live presentation and in the final project report.

## 10. Limitations

The demonstration ROMs are intended exclusively for functional
testing and academic demonstration.

The following limitations apply:

- Exact effective shiny probabilities remain unverified.
- Encounter RNG independence has not been established.
- Observed shiny frequencies are descriptive measurements.
- The modified shiny threshold may produce Pokemon that are
  not shiny when loaded into an unmodified ROM.
- Exported demonstration saves have not been independently
  verified against the original ROMs.
- An initial shiny notification sound was not heard during
  Sapphire testing, although subsequent notifications played.
- Permanent profile byte integrity was not independently
  rechecked during the multiple-shiny export session.
- Final mixed-game cleanup was not yet recorded at the time
  of the final dashboard screenshot.
- The final mixed-game session did not produce a shiny
  Bulbasaur before manual stopping.
- Demonstration ROM selection currently requires replacing
  the active ROM files while preserving their registered paths.

The original ROMs remain the standard environment for normal
hunting and production compatibility verification.

## 11. Phase Completion

Phase 10.8.2:

Multiple-shiny detection, preservation, sequential manual
takeover, and individual save export regression completed.

Phase 10.8.3:

Minimal demonstration ROM patch generation and integrated
compatibility testing completed for all four supported games.

The final mixed-game regression achieved:

- Ten configured hunting instances.
- 1049 valid encounters.
- Zero failed rotations.
- Seven shiny discoveries.
- Successful shiny detection across all four games.
- 100% encounter success rate.

The application is functionally ready for the live demonstration.

The remaining project work consists primarily of comprehensive
source code review, documentation review, dependency management,
final application packaging, and standalone laptop verification.

Phase 11 will focus on reviewing and refining the completed
application without introducing unnecessary changes to verified
functionality.