# Mixed-Game Integration Verification

## Overview

The final multi-game integration test was performed to verify
that all three supported games could operate concurrently within
the same graphical hunting dashboard.

The test included Pokemon FireRed, LeafGreen, and Sapphire,
with one hunting instance assigned to each supported starter.

This test also verified that the summary-based and battle-based
computer vision pipelines could operate independently within
the same application.

## Test Configuration

| Game | ROM Revision | Starters | Instances |
|---|---|---|---:|
| FireRed | Rev 1 | Bulbasaur, Charmander, Squirtle | 3 |
| LeafGreen | Rev 1 | Bulbasaur, Charmander, Squirtle | 3 |
| Sapphire | Rev 2 | Treecko, Torchic, Mudkip | 3 |
| Total | | | 9 |

All nine instances were configured through the graphical
application using existing permanent hunting profiles.

Each instance maintained its own temporary ROM, battery save,
emulator core, framebuffer, hunting controller, and computer
vision detector.

No production code modifications were required for this test.

## Concurrent Hunting

All nine instances successfully initialized and began automated
hunting within the same dashboard.

FireRed and LeafGreen used the summary-based detection pipeline,
which evaluates the following features:

- Border color using RGB features and a linear SVM.
- Shiny star using HOG features and a linear SVM.
- Pokemon sprite using spatial RGB histograms.

The final shiny prediction requires agreement between at least
two of the three classifiers.

Sapphire used the battle-based detection pipeline, which
performs the following operations:

- Battle screen validation using template matching.
- Target sprite validation using HOG features and a linear SVM.
- Shiny classification using spatial RGB histograms.

Each instance displayed the classification results appropriate
to its registered game's vision configuration.

![Mixed-game concurrent hunting](figures/gui/hunting_page/mixed_game_live_hunting.png)

*Figure: Nine concurrent hunting instances operating across
FireRed, LeafGreen, and Sapphire within the same dashboard.*

## Experimental Results

### Individual Instance Results

| Game | Starter | Rotations | Valid Encounters | Failures | Encounters/min |
|---|---|---:|---:|---:|---:|
| FireRed | Bulbasaur | 16 | 16 | 0 | 8.33 |
| FireRed | Charmander | 16 | 16 | 0 | 8.38 |
| FireRed | Squirtle | 16 | 16 | 0 | 8.34 |
| LeafGreen | Bulbasaur | 17 | 17 | 0 | 8.88 |
| LeafGreen | Charmander | 16 | 16 | 0 | 8.32 |
| LeafGreen | Squirtle | 16 | 16 | 0 | 8.33 |
| Sapphire | Mudkip | 116 | 116 | 0 | 60.91 |
| Sapphire | Torchic | 118 | 118 | 0 | 62.32 |
| Sapphire | Treecko | 116 | 115 | 1 | 60.59 |
| Total | | 447 | 446 | 1 | 274.40 |

### Combined Game Results

| Game | Rotations | Valid Encounters | Failures | Success Rate | Encounters/min |
|---|---:|---:|---:|---:|---:|
| FireRed | 48 | 48 | 0 | 100.00% | 25.05 |
| LeafGreen | 49 | 49 | 0 | 100.00% | 25.53 |
| Sapphire | 350 | 349 | 1 | 99.71% | 183.82 |
| Total | 447 | 446 | 1 | 99.78% | 274.40 |

A total of 447 automated hunting rotations were completed,
producing 446 valid encounters and one rejected encounter.

No shiny encounters were detected during this test.

All nine instances successfully responded to the Stop All
operation and retained their final encounter screenshots
and classification results.

![Mixed-game hunting results](figures/gui/hunting_page/mixed_game_stopped.png)

*Figure: All nine hunting instances stopped following 447
automated hunting rotations across three supported games.*

## Invalid Encounter Handling

One invalid encounter occurred during the Sapphire Treecko
instance's 111th hunting rotation.

| Property | Result |
|---|---|
| Instance ID | 95629c87 |
| Failed rotation | 111 |
| Battle validation | Failed |
| Sprite validation | Not evaluated |
| Palette classification | Not evaluated |
| Automatic retry | Successful |
| Subsequent valid encounters | 5 |
| Final consecutive failures | 0 |

The battle validator rejected the captured frame before
sprite validation and shiny classification were performed.

The hunting controller recorded the failed rotation and
automatically initiated another hunting attempt.

The instance subsequently completed five additional valid
encounters without further failures.

This verified that an invalid encounter does not produce
a shiny prediction or unnecessarily terminate the hunting
process.

The exact cause of the invalid battle frame could not be
determined because the screenshot was replaced during the
subsequent hunting rotation.

No production code modifications were made in response
to this isolated failure.

## Performance

The nine concurrent hunting instances achieved a combined
displayed encounter rate of 274.40 encounters per minute.

| Game | Instances | Combined Encounters/min | Average Encounters/min per Instance |
|---|---:|---:|---:|
| FireRed | 3 | 25.05 | 8.35 |
| LeafGreen | 3 | 25.53 | 8.51 |
| Sapphire | 3 | 183.82 | 61.27 |
| Total | 9 | 274.40 | 30.49 |

Sapphire achieved a substantially higher encounter rate
than FireRed and LeafGreen during the mixed-game test.

The Sapphire hunting macro requires fewer menu interactions
because classification occurs directly within the initial
battle. FireRed and LeafGreen require additional interactions
to obtain the starter and navigate to its summary screen.

The combined encounter rate represents the sum of the
individual encounter rates displayed by the dashboard.

These results demonstrate concurrent hunting performance
under a mixed-game workload rather than a controlled
performance comparison between individual games.

## Shutdown and Cleanup

All nine hunting instances successfully responded to the
Stop All operation.

The dashboard reported the following final session status:

| Property | Result |
|---|---:|
| Configured instances | 9 |
| Active instances | 0 |
| Finished instances | 9 |
| Shinies detected | 0 |

Following dashboard closure, all nine emulator instances
were successfully closed.

The application terminated with exit code 0 and no
unhandled exceptions.

The temporary directory was inspected following shutdown.
All temporary instance directories associated with this
test were removed.

Pre-existing temporary directories and controlled shiny
test resources remained unaffected.

All permanent hunting profiles and saves remained available
following application termination.

## Verification Summary

| Verification | Result |
|---|---|
| FireRed concurrent hunting | Passed |
| LeafGreen concurrent hunting | Passed |
| Sapphire concurrent hunting | Passed |
| All nine supported starters | Passed |
| Mixed-game instance initialization | Passed |
| Concurrent summary-based detection | Passed |
| Concurrent battle-based detection | Passed |
| Game-specific classification displays | Passed |
| Independent live framebuffers | Passed |
| Independent encounter statistics | Passed |
| Invalid encounter rejection | Passed |
| Automatic recovery following rejection | Passed |
| Stop All operation | Passed |
| Emulator instance closure | Passed |
| Temporary instance cleanup | Passed |
| Permanent profile persistence | Passed |
| Application termination | Passed |

## Experimental Limitations

The observed encounter validation success rate of 99.78%
represents the proportion of completed hunting rotations
that produced valid encounter frames.

This value does not represent shiny classification accuracy.

No naturally occurring shiny encounters were detected
during the mixed-game test. Shiny detection and preservation
were evaluated separately through controlled shiny tests
for each supported game.

The cause of the single rejected battle frame remains
undetermined, although automatic recovery was successfully
verified.

Permanent profile persistence was confirmed through
filesystem inspection rather than a byte-for-byte comparison
during this test.

The reported encounter rates were obtained from a single
mixed-game hunting session and should not be interpreted
as average performance across repeated experiments.

## Conclusion

The mixed-game integration test successfully demonstrated
that all three supported games and all nine supported
starters can operate concurrently within the same
graphical hunting application.

Both computer vision detection pipelines operated
independently without requiring separate interfaces or
game-specific hunting controllers.

The application successfully completed 446 valid encounters
across 447 hunting rotations, automatically recovered from
an invalid encounter, and safely terminated all nine
emulator instances without removing permanent hunting
profiles.

Together with the previous game-specific integration and
controlled shiny preservation tests, these results complete
the multi-game functional integration phase of the project.