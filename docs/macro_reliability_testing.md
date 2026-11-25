# FireRed Macro Reliability Testing

**Date:** November 25, 2026  
**Game:** Pokémon FireRed (USA, Europe), Rev 1  
**Emulator:** libmGBA  
**Macro:** `macros/firered_main_macro.py`  
**Test:** `tests/emulation/test_multiple_instances.py`

## 1. Objective

Evaluate whether the automated starter hunting macro consistently acquires the selected starter and reaches its Pokémon summary screen. The summary screen is required for the subsequent border, star, and palette classifiers. This experiment evaluates macro navigation and encounter diversity, not shiny classification accuracy.

Bulbasaur was selected as the primary timing stress test because, in the project's prepared save setup, the rival walks the longest path to select Charmander after the player selects Bulbasaur. Charmander and Squirtle were tested separately to verify compatibility with the same macro.

## 2. Test methodology

Each test run used two concurrent emulator instances, each initialized from an isolated copy of the selected permanent save profile. The initial trial used five attempts per instance; subsequent trials used ten attempts per instance. Each attempt reset the emulator, executed the randomized frame-based input schedule, and captured a screenshot after the final input.

An attempt was considered successful when its screenshot displayed the expected starter's Pokémon summary screen. Screenshots were visually inspected. Nature and gender variation were also observed to assess whether randomized frame delays produced varied encounter characteristics.

The initial Bulbasaur profile was mistakenly named Squirtle and was subsequently renamed to reflect the actual starter. The original Charmander profile used trainer CHRIS, while the Bulbasaur and Squirtle profiles used trainer ASH. The Squirtle profile was prepared by repositioning the player and saving before the encounter, without modifying the permanent Bulbasaur profile.

## 3. Initial macro testing

The original macro held each button for one emulated frame and used a fixed base input schedule with cumulative randomized delays.

| Trial | Attempts | Successful | Failed | Success rate |
|---|---:|---:|---:|---:|
| Original macro | 10 | 8 | 2 | 80% |

Both failures ended on the nickname entry screen with a partially entered nickname (`AA`). All ten attempts had acquired Bulbasaur. The test log also confirmed unique instance IDs, successful temporary directory cleanup, and an unchanged permanent save.

The repeated nickname failure suggested that the input sequence might be reaching the Yes/No prompt before it was ready to accept the intended Down input. This was a hypothesis, not a confirmed root cause.

## 4. Timing adjustment

An additional 60 emulated frames were inserted before Step 8 (Down). Steps 8–14 were shifted by the same amount to preserve their relative timing. Randomized variance, reset delay, and screenshot delay remained unchanged.

| Step | Input | Original base frame | Revised base frame |
|---|---|---:|---:|
| 7 | A | 1298 | 1298 |
| 8 | Down | 1888 | 1948 |
| 9 | A | 1955 | 2015 |
| 10 | A | 2235 | 2295 |
| 11 | Start | 2634 | 2694 |
| 12 | A | 2720 | 2780 |
| 13 | A | 2803 | 2863 |
| 14 | A | 2874 | 2934 |

| Trial | Attempts | Successful | Failed | Success rate | Failure observed |
|---|---:|---:|---:|---:|---|
| Timing adjustment 1 | 20 | 19 | 1 | 95% | Starter selection confirmation |
| Timing adjustment 2 | 20 | 19 | 1 | 95% | Nickname entry |
| **Total** | **40** | **38** | **2** | **95%** | |

The observed success rate increased from 80% to 95%. However, the nickname failure recurred, and a separate attempt ended at the starter selection confirmation screen. Therefore, the timing adjustment alone was not sufficient.

During this stage, screenshot storage was reorganized into per-instance directories (`pictures/<instance_id>/attempt_<number>.png`) to simplify manual inspection. This was a logging change, not a macro timing change.

## 5. Button duration adjustment

The next modification increased button duration from one frame to five frames while retaining the 60-frame timing adjustment. The frame counter was incremented by five after each input rather than one, maintaining the scheduled start frames for subsequent inputs.

```python
core.add_keys(key)

for _ in range(5):
    core.run_frame()

core.clear_keys(key)

print(f"Step {step} executed at macro frame {current_frame}")

current_frame += 5
```

The hypothesis was that a single-frame input might occasionally be missed. Holding the input longer could improve registration. The experiment did not directly instrument input polling, so the precise failure mechanism remains unconfirmed.

## 6. Final validation

The revised macro was tested without further changes. Five Bulbasaur trials provided 100 stress-test attempts, followed by one 20-attempt trial for each remaining starter.

| Starter | Trial | Instances | Attempts | Successful | Failed | Success rate |
|---|---:|---:|---:|---:|---:|---:|
| Bulbasaur | 1 | 2 | 20 | 20 | 0 | 100% |
| Bulbasaur | 2 | 2 | 20 | 20 | 0 | 100% |
| Bulbasaur | 3 | 2 | 20 | 20 | 0 | 100% |
| Bulbasaur | 4 | 2 | 20 | 20 | 0 | 100% |
| Bulbasaur | 5 | 2 | 20 | 20 | 0 | 100% |
| Charmander | 1 | 2 | 20 | 20 | 0 | 100% |
| Squirtle | 1 | 2 | 20 | 20 | 0 | 100% |
| **Total** | **7** | | **140** | **140** | **0** | **100%** |

All final validation screenshots displayed the expected Pokémon summary screen. No starter-specific macro changes were required.

## 7. Encounter diversity

Nature counts were manually transcribed from the final validation screenshot thumbnails. The Bulbasaur counts were recounted for this document; Naive occurred 13 times and Naughty occurred five times. Both male and female encounters were observed for each starter.

| Nature | Bulbasaur | Charmander | Squirtle | Total |
|---|---:|---:|---:|---:|
| Adamant | 3 | 1 | 2 | 6 |
| Bashful | 4 | 1 | 1 | 6 |
| Bold | 2 | 1 | 0 | 3 |
| Brave | 2 | 1 | 0 | 3 |
| Calm | 3 | 0 | 0 | 3 |
| Careful | 3 | 1 | 0 | 4 |
| Docile | 6 | 3 | 3 | 12 |
| Gentle | 6 | 0 | 1 | 7 |
| Hardy | 3 | 0 | 0 | 3 |
| Hasty | 2 | 1 | 1 | 4 |
| Impish | 3 | 1 | 1 | 5 |
| Jolly | 4 | 1 | 0 | 5 |
| Lax | 1 | 0 | 0 | 1 |
| Lonely | 3 | 2 | 1 | 6 |
| Mild | 3 | 2 | 0 | 5 |
| Modest | 5 | 0 | 0 | 5 |
| Naive | 13 | 0 | 1 | 14 |
| Naughty | 5 | 0 | 0 | 5 |
| Quiet | 3 | 2 | 1 | 6 |
| Quirky | 7 | 2 | 2 | 11 |
| Rash | 4 | 1 | 1 | 6 |
| Relaxed | 4 | 0 | 1 | 5 |
| Sassy | 4 | 0 | 2 | 6 |
| Serious | 3 | 0 | 2 | 5 |
| Timid | 4 | 0 | 0 | 4 |
| **Total** | **100** | **20** | **20** | **140** |

| Metric | Bulbasaur | Charmander | Squirtle |
|---|---:|---:|---:|
| Unique natures | 25/25 | 14/25 | 14/25 |
| Nature coverage | 100% | 56% | 56% |

All 25 possible natures were observed during the Bulbasaur stress test. The diversity in nature and gender supports the conclusion that the randomized frame delays generate encounters with varied observable characteristics. It does not establish that every encounter is unique, that the random number generator is statistically uniform, or that shiny odds were measured.

## 8. Overall results

| Macro configuration | Attempts | Successful | Failed | Observed success rate |
|---|---:|---:|---:|---:|
| Original (one-frame inputs) | 10 | 8 | 2 | 80% |
| Additional 60-frame delay | 40 | 38 | 2 | 95% |
| Additional delay + five-frame inputs | 140 | 140 | 0 | 100% |
| **Total documented executions** | **190** | **186** | **4** | |

The final configuration improved the observed success rate by 20 percentage points relative to the original trial and completed all 140 validation attempts without a visible macro failure. The original and intermediate trials used Bulbasaur; the final pooled result also includes the two compatibility tests. The corresponding final Bulbasaur-only result was 100/100.

## 9. Conclusion and limitations

The revised FireRed macro successfully navigated from the prepared pre-encounter save to the expected summary screen for all three supported starters. Increasing the delay before the nickname selection sequence and subsequently increasing button duration produced a substantial observed reliability improvement.

The final result is an observed success rate under the tested conditions, not a guarantee of perfect reliability. The tests used specific prepared saves, one ROM revision, and two concurrent instances. Other text speed settings, save conditions, larger instance counts, and long-running hunting sessions were not independently evaluated here. The precise causes of the earlier failures were not conclusively established. Shiny detection and stop-on-shiny behavior require separate integration testing.

Representative screenshots of the nickname entry failure, starter selection confirmation failure, and successful summary screens may be retained in `docs/figures/` for the presentation and report. The bulk encounter screenshots remain test outputs rather than required runtime assets.