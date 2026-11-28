# Demo ROM Patch and Multiple Shiny Testing

## 1. Overview

Phase 10.8.2 focuses on verifying multiple shiny encounters within
a single hunting session, independent emulator preservation,
sequential manual takeovers, and individual battery save exports.

Under standard Generation III shiny odds of 1/8192, obtaining
multiple shiny encounters within a reasonable testing period is
impractical.

An increased shiny probability was therefore introduced through
a separate demonstration ROM to accelerate functional testing
and support the live project presentation.

The modified ROM is intended exclusively for testing and
demonstration purposes. Normal hunting continues to use
unmodified ROMs.

## 2. Initial ROM Patching Attempt

### 2.1 KiraPatch

KiraPatch was initially used to generate modified versions of
all four supported games with increased shiny odds.

The patched ROMs retained their original filenames to maintain
compatibility with the existing game registry and save profiles.

However, integrated testing revealed substantial compatibility
issues with the existing hunting macros.

### 2.2 Initial Compatibility Results

Ten concurrent hunting instances were configured using patched
LeafGreen, Ruby, and Sapphire ROMs.

| Game | Instances | Rotations | Valid Encounters | Failures |
|---|---:|---:|---:|---:|
| LeafGreen | 4 | 53 | 1 | 52 |
| Ruby | 3 | 294 | 0 | 294 |
| Sapphire | 3 | 293 | 0 | 293 |
| Total | 10 | 640 | 1 | 639 |

Overall encounter success rate: 0.16%.

One shiny Charmander was successfully detected using all three
FireRed and LeafGreen classification methods.

However, the remaining instances repeatedly failed encounter
validation.

The computer vision system correctly rejected invalid encounter
screenshots rather than treating them as valid shiny encounters.

The exact cause of the compatibility failures was not established,
but the results indicated that the patch interfered with the
existing automated hunting workflow.

### 2.3 Original ROM Regression

The original ROMs were restored and another ten-instance hunting
session was conducted.

| Game | Instances | Valid Encounters | Failures |
|---|---:|---:|---:|
| FireRed | 3 | 13 | 0 |
| LeafGreen | 3 | 12 | 0 |
| Ruby | 3 | 107 | 0 |
| Sapphire | 1 | 34 | 0 |
| Total | 10 | 166 | 0 |

Overall encounter success rate: 100%.

Restoring the original ROMs resolved the observed compatibility
issues without requiring changes to the application.

The KiraPatch ROMs were retained separately for reference but
removed from the active ROM directory.

## 3. Minimal Demonstration ROM Patch

### 3.1 Design

A smaller ROM modification was developed to increase the shiny
determination threshold without introducing additional RNG
reroll routines.

The intended shiny probability is 1/256 rather than the original
1/8192 probability.

The primary requirements were:

- Preserve existing macro compatibility.
- Preserve existing save profile compatibility.
- Preserve game menus and screenshot regions.
- Preserve computer vision classifier compatibility.
- Avoid changes to production application code.
- Preserve the original ROM.
- Allow accelerated shiny detection during testing.

Sapphire Rev 2 was selected for initial testing because its
hunting macro completes substantially faster than the FireRed
and LeafGreen macros.

### 3.2 Patching Utility

A separate utility was created:

tests/emulation/patch_demo_roms.py

The utility:

1. Loads the original Sapphire Rev 2 ROM.
2. Verifies its SHA-256 hash.
3. Validates the expected comparison instruction bytes.
4. Modifies four comparison threshold bytes.
5. Writes a separate demonstration ROM.
6. Reports the number of modified bytes.
7. Preserves the original ROM.

The utility does not modify the original ROM in place.

### 3.3 Sapphire ROM Modifications

Supported ROM:

Pokemon - Sapphire Version (USA, Europe) (Rev 2).gba

Original ROM SHA-256:

02ca41513580a8b780989dee428df747b52a0b1a55bec617886b4059eb1152fb

The following byte modifications were applied:

| ROM Offset | Original Byte | Modified Byte |
|---|---|---|
| 0x00040988 | 0x07 | 0xFF |
| 0x000409FE | 0x07 | 0xFF |
| 0x00040D14 | 0x07 | 0xFF |
| 0x0014189A | 0x07 | 0xFF |

Total modified bytes: 4

ROM size: 16,777,216 bytes

The patching utility completed successfully with exit code 0.

All expected instruction bytes and the original ROM hash passed
verification before the modified ROM was generated.

The intended probability assumes that the modified comparisons
operate on the standard Generation III shiny determination value.
The exact effective probability has not been independently
established through complete instruction-level analysis.

### 3.4 ROM Directory Organization

The ROM directories are organized as follows:

- roms/
    - Active ROMs used by the application.
- roms_shiny_patch/
    - Previously generated KiraPatch ROMs.
- roms_demo/
    - Minimal demonstration ROMs.

Original ROM backups are maintained separately before replacing
any active ROM with a demonstration version.

The demonstration ROM retains the original registered filename,
allowing the application to use it without modifications to the
game registry or existing save profiles.

ROM directories and modified ROM binaries are excluded from
version control.

## 4. Integrated Demonstration ROM Testing

### 4.1 Test Configuration

Test date: November 27, 2026

The modified Sapphire ROM was tested directly through the main
application rather than through a controlled shiny save test.

Nine concurrent hunting instances were configured:

- Three Sapphire Mudkip instances.
- Three Sapphire Torchic instances.
- Three Sapphire Treecko instances.

All instances used existing permanent save profiles.

No controlled shiny source saves were required for this test.

The application continued to use its existing:

- Emulator instance manager.
- Sapphire hunting macro.
- Battle validation classifier.
- Sprite validation classifier.
- Palette classifier.
- Hunting controller.
- Hunting worker.
- Shiny notification system.
- Manual takeover functionality.
- Battery save export functionality.

No production application changes were required to support the
demonstration ROM.

### 4.2 Initial Shiny Detection

The first shiny encounter was detected by a Torchic instance
after three valid encounters.

The instance successfully:

- Completed its automated hunting macro.
- Captured a valid battle screenshot.
- Passed battle validation.
- Passed sprite validation.
- Passed shiny palette classification.
- Automatically stopped hunting.
- Preserved its emulator state.
- Displayed the shiny notification banner.
- Displayed the gold border and Ultra Ball watermark.

The initial shiny notification sound was not heard.

Subsequent shiny notification sounds played successfully,
indicating that audio playback remained functional.

The cause of the initial missed sound remains unverified.

### 4.3 Multiple Shiny Detection

Additional shiny encounters were detected while the remaining
instances continued hunting independently.

The first three shiny encounters were:

| Starter | Instance ID | Valid Encounters |
|---|---|---:|
| Torchic | 588ead9e | 3 |
| Torchic | 4d637f3e | 100 |
| Mudkip | 9a562193 | 111 |

All three shiny instances remained independently preserved.

The dashboard correctly displayed:

- Nine configured instances.
- Six active instances.
- Three finished instances.
- Three shiny encounters.

The notification banner updated its cumulative shiny count
and displayed the most recently detected shiny.

Multiple shiny encounters originating from the same permanent
save profile were also successfully preserved.

## 5. Seven-Shiny Verification

### 5.1 Instance Results

The hunting session continued until seven of the nine instances
had successfully detected shiny starters.

The following results were recorded from the dashboard:

| Starter | Instance ID | Rotations | Valid | Failures | Shinies | State |
|---|---|---:|---:|---:|---:|---|
| Mudkip | 9a562193 | 111 | 111 | 0 | 1 | Shiny Found |
| Mudkip | b03e8753 | 463 | 463 | 0 | 0 | Hunting |
| Mudkip | eb2db830 | 272 | 269 | 3 | 1 | Shiny Found |
| Torchic | 4d637f3e | 100 | 100 | 0 | 1 | Shiny Found |
| Torchic | 588ead9e | 3 | 3 | 0 | 1 | Shiny Found |
| Torchic | 67a44ae4 | 316 | 314 | 2 | 1 | Shiny Found |
| Treecko | c726f631 | 133 | 133 | 0 | 1 | Shiny Found |
| Treecko | 9dec20ed | 459 | 458 | 1 | 0 | Hunting |
| Treecko | ba5a38b3 | 274 | 273 | 1 | 1 | Shiny Found |

### 5.2 Results by Starter

| Starter | Rotations | Valid Encounters | Failures | Shinies |
|---|---:|---:|---:|---:|
| Mudkip | 846 | 843 | 3 | 2 |
| Torchic | 419 | 417 | 2 | 3 |
| Treecko | 866 | 864 | 2 | 2 |
| Total | 2131 | 2124 | 7 | 7 |

Overall encounter success rate: 99.67%.

Overall failed rotation rate: 0.33%.

All three supported Sapphire shiny starter variants were
successfully detected during the same hunting session.

### 5.3 Observed Shiny Frequency

Total valid encounters: 2124

Total shiny encounters: 7

Observed shiny frequency:

7 / 2124 = 0.003296

Observed shiny percentage: approximately 0.33%.

Observed shiny rate: approximately 1/303.4.

Intended demonstration shiny rate: 1/256.

Original Generation III shiny rate: 1/8192.

The observed shiny frequency is consistent with the intended
increased shiny probability.

However, the sample size is insufficient to establish the exact
effective probability, and encounter RNG independence has not
been independently verified.

These results demonstrate accelerated shiny generation rather
than establish a statistically precise shiny probability.

### 5.4 Dashboard Verification

At the recorded seven-shiny checkpoint, the dashboard displayed:

- Configured instances: 9
- Active instances: 2
- Finished instances: 7
- Shinies found: 7

All seven shiny instances displayed:

- Shiny Found status.
- Gold instance borders.
- Ultra Ball watermarks.
- Preserved shiny battle screenshots.
- Valid battle classification.
- Valid sprite classification.
- Shiny palette classification.
- Enabled Manual Takeover buttons.
- Disabled Stop buttons.
- Disabled Export Save buttons until manual takeover completion.

The remaining two instances continued hunting normally.

The notification banner correctly displayed the cumulative
shiny count and most recent shiny encounter.

### 5.5 Hunting Performance

| Instance ID | Starter | Encounters per Minute |
|---|---|---:|
| 9a562193 | Mudkip | 64.60 |
| b03e8753 | Mudkip | 77.19 |
| eb2db830 | Mudkip | 70.68 |
| 4d637f3e | Torchic | 62.05 |
| 588ead9e | Torchic | 70.86 |
| 67a44ae4 | Torchic | 72.94 |
| c726f631 | Treecko | 66.88 |
| 9dec20ed | Treecko | 76.45 |
| ba5a38b3 | Treecko | 71.66 |

The two remaining active instances displayed a combined hunting
speed of 153.64 encounters per minute.

Individual instance speeds were calculated over their respective
hunting durations. Since instances stopped at different times,
summing all nine displayed rates would not represent the
current combined hunting throughput.

The minimal ROM patch maintained substantially better macro
compatibility than the initial KiraPatch implementation.

## 6. Patch Compatibility Comparison

| Metric | KiraPatch | Minimal Sapphire Patch |
|---|---:|---:|
| Concurrent instances | 10 | 9 |
| Completed rotations | 640 | 2131 |
| Valid encounters | 1 | 2124 |
| Failed rotations | 639 | 7 |
| Encounter success rate | 0.16% | 99.67% |
| Shiny encounters | 1 | 7 |

The minimal Sapphire patch achieved a high encounter success
rate while allowing repeated shiny discoveries.

The comparison is a functional compatibility comparison rather
than a controlled performance benchmark because the initial
KiraPatch session included multiple game families.

Occasional invalid Sapphire encounters were previously observed
using the original ROM. The seven failed rotations in the
demonstration session do not independently establish a new
patch-related failure mechanism.

## 7. Multiple-Shiny Regression Status

| Verification | Result |
|---|---|
| Minimal Sapphire ROM generation | PASS |
| Original ROM preservation during patching | PASS |
| Existing save profile compatibility | PASS |
| Existing Sapphire macro compatibility | PASS |
| Battle validation | PASS |
| Sprite validation | PASS |
| Shiny palette classification | PASS |
| Shiny Mudkip detection | PASS |
| Shiny Torchic detection | PASS |
| Shiny Treecko detection | PASS |
| Multiple simultaneous preserved shinies | PASS |
| Multiple shinies from the same profile | PASS |
| Independent shiny instance stopping | PASS |
| Continued hunting by normal instances | PASS |
| Cumulative shiny notification count | PASS |
| Latest shiny notification updates | PASS |
| Repeated audio notifications | PASS |
| Initial audio notification | NOT HEARD |
| Independent shiny dashboard styling | PASS |
| Sequential manual takeovers | PENDING |
| Individual shiny save exports | PENDING |
| Post-export dashboard verification | PENDING |
| Final temporary instance cleanup | PENDING |
| Final permanent profile integrity | PENDING |

The seven-shiny checkpoint represents an intermediate result
within the ongoing regression session.

Final session statistics and export verification will be
documented after the remaining testing is completed.

## 8. Live Demonstration Application

The minimal Sapphire patch provides a practical environment
for demonstrating the complete application within the available
presentation time.

The demonstration can show:

- Concurrent emulator instances.
- Automated starter encounters.
- Real-time framebuffer updates.
- Encounter statistics.
- Computer vision classification.
- Automatic shiny detection.
- Independent instance stopping.
- Visual and audio notifications.
- Preservation of multiple shiny encounters.
- Manual gameplay takeover.
- Battery save export.

The presentation must explicitly disclose that the demonstration
ROM uses an increased shiny probability.

The ROM modification does not replace the computer vision
classification system. The application continues to identify
shiny encounters through captured game screenshots rather than
reading the game's internal shiny determination values.

The increased probability only reduces the expected waiting
time before a shiny encounter becomes available for detection.

## 9. Limitations

The demonstration ROM is not intended for legitimate shiny
hunting.

Pokemon generated using the modified shiny threshold may not
remain shiny when transferred to an unmodified ROM.

The following limitations remain:

- Exact effective shiny probability is not independently proven.
- Encounter RNG independence has not been established.
- Exported shiny compatibility with original ROMs is unverified.
- The initial missed audio notification remains unexplained.
- Minimal patches for FireRed, LeafGreen, and Ruby are pending.
- Sequential manual takeover and export testing is incomplete.
- Final cleanup and permanent profile integrity verification
  remain pending for this session.

The original ROMs remain the standard environment for production
hunting and final application compatibility verification.

## 10. Remaining Steps

1. Complete the ongoing nine-instance Sapphire hunting session.
2. Perform sequential manual takeovers on preserved shiny
   instances.
3. Verify individual battery save exports.
4. Verify dashboard behavior following multiple exports.
5. Close the dashboard and verify temporary instance cleanup.
6. Verify permanent save profiles remain unchanged.
7. Record final session statistics.
8. Extend the minimal patching utility to the remaining supported
   ROM revisions if needed for the presentation.
9. Complete Phase 10.8.2.
10. Proceed to Phase 11 source code and documentation review.