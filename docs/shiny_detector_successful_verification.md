## Combined Shiny Detector Verification

The shiny detection system combines three separate computer
vision classifiers through a majority voting algorithm.
Each classifier evaluates a distinct visual indicator
within the Pokémon summary screen.

The final classification requires at least two of the three
classifiers to identify a shiny Pokémon.

### Classifier Configuration

| Detector | Feature Extraction | Classification | Features |
|---|---|---|---:|
| Border | Mean RGB | Linear SVM | 3 |
| Star | HOG | Linear SVM | 324 |
| Palette | Spatial RGB histograms | Bhattacharyya distance | 384 |

Each classifier operates on its respective region of
interest (ROI), as defined in the game-specific JSON
configuration.

### Combined Classification Results

| Pokémon | Expected | Border | Star | Palette | Shiny Votes | Result |
|---|---|---|---|---|---:|---|
| Bulbasaur | Normal | False | False | False | 0/3 | Pass |
| Charmander | Normal | False | False | False | 0/3 | Pass |
| Squirtle | Normal | False | False | False | 0/3 | Pass |
| Bulbasaur | Shiny | True | True | True | 3/3 | Pass |
| Charmander | Shiny | True | True | True | 3/3 | Pass |
| Squirtle | Shiny | True | True | True | 3/3 | Pass |

All three classifiers agreed on the classification of
each reference image.

### Computational Performance

| Metric | Result |
|---|---:|
| Initialization time | 9.495 ms |
| Average classification time | 0.2006 ms |
| Minimum classification time | 0.1699 ms |
| Maximum classification time | 0.2753 ms |
| Reference classifications | 6/6 |
| Correct voting decisions | 8/8 |

Initialization includes loading the game configuration,
loading reference images, training both Linear SVM models,
generating foreground masks, and constructing the
reference histograms.

Classification time includes feature extraction, individual
classifier predictions, and majority voting.

### Individual Classification Times

| Pokémon | Classification | Processing Time (ms) |
|---|---|---:|
| Bulbasaur | Normal | 0.2140 |
| Charmander | Normal | 0.1778 |
| Squirtle | Normal | 0.1699 |
| Bulbasaur | Shiny | 0.2753 |
| Charmander | Shiny | 0.1947 |
| Squirtle | Shiny | 0.1718 |
| **Average** | | **0.2006** |

All six classifications completed in less than one
millisecond during this verification test.

### Majority Voting Verification

The majority voting algorithm combines three Boolean
predictions, where 0 represents a normal classification
and 1 represents a shiny classification.

A Pokémon is classified as shiny when the sum of the
three predictions is greater than or equal to two.

| Border | Star | Palette | Shiny Votes | Decision | Result |
|---:|---:|---:|---:|---|---|
| 0 | 0 | 0 | 0/3 | Normal | Pass |
| 0 | 0 | 1 | 1/3 | Normal | Pass |
| 0 | 1 | 0 | 1/3 | Normal | Pass |
| 0 | 1 | 1 | 2/3 | Shiny | Pass |
| 1 | 0 | 0 | 1/3 | Normal | Pass |
| 1 | 0 | 1 | 2/3 | Shiny | Pass |
| 1 | 1 | 0 | 2/3 | Shiny | Pass |
| 1 | 1 | 1 | 3/3 | Shiny | Pass |

All eight possible voting combinations produced the
expected decision.

### Automated Hunting Decisions

| Shiny Votes | Classification | Intended Action |
|---:|---|---|
| 0/3 | Normal | Reset and continue |
| 1/3 | Normal | Reset and continue |
| 2/3 | Shiny | Stop hunting |
| 3/3 | Shiny | Stop hunting |

The majority voting algorithm allows a single classifier
to produce an incorrect prediction without changing the
final classification, provided the other two predictions
are correct.

Manual verification is not required during the automated
hunting process.

### Console Output

```text
Shiny detector initialized.
Initialization time: 0.009495 seconds

--- Reference Image Classification ---

Image: normal/001.png
Border: False
Star: False
Palette: False
Shiny votes: 0/3
Expected: Normal
Predicted: Normal
Processing time: 0.2140 ms
Correct: True

Image: normal/004.png
Border: False
Star: False
Palette: False
Shiny votes: 0/3
Expected: Normal
Predicted: Normal
Processing time: 0.1778 ms
Correct: True

Image: normal/007.png
Border: False
Star: False
Palette: False
Shiny votes: 0/3
Expected: Normal
Predicted: Normal
Processing time: 0.1699 ms
Correct: True

Image: shiny/001.png
Border: True
Star: True
Palette: True
Shiny votes: 3/3
Expected: Shiny
Predicted: Shiny
Processing time: 0.2753 ms
Correct: True

Image: shiny/004.png
Border: True
Star: True
Palette: True
Shiny votes: 3/3
Expected: Shiny
Predicted: Shiny
Processing time: 0.1947 ms
Correct: True

Image: shiny/007.png
Border: True
Star: True
Palette: True
Shiny votes: 3/3
Expected: Shiny
Predicted: Shiny
Processing time: 0.1718 ms
Correct: True

Correct classifications: 6/6
Average processing time: 0.2006 ms

--- Majority Voting Verification ---

Border: 0 | Star: 0 | Palette: 0 | Result: Normal | Correct: True
Border: 0 | Star: 0 | Palette: 1 | Result: Normal | Correct: True
Border: 0 | Star: 1 | Palette: 0 | Result: Normal | Correct: True
Border: 0 | Star: 1 | Palette: 1 | Result: Shiny | Correct: True
Border: 1 | Star: 0 | Palette: 0 | Result: Normal | Correct: True
Border: 1 | Star: 0 | Palette: 1 | Result: Shiny | Correct: True
Border: 1 | Star: 1 | Palette: 0 | Result: Shiny | Correct: True
Border: 1 | Star: 1 | Palette: 1 | Result: Shiny | Correct: True

Correct voting decisions: 8/8
```

### Observations

The combined shiny detection system successfully classified
all six reference images using three complementary computer
vision techniques.

The average classification time of 0.2006 milliseconds
demonstrates that the combined detection system introduces
minimal computational overhead during this initial test.

The classifiers are initialized once and reused for
subsequent predictions, eliminating the need to retrain
the SVM models or reconstruct reference histograms during
each hunting attempt.

The majority voting algorithm introduces redundancy into
the classification process. A single incorrect prediction
can be tolerated without changing the final decision.

### Limitations

- The same reference images were used for classifier
  initialization and verification.
- The measured classification times exclude emulator
  execution, image acquisition, and framebuffer conversion.
- Processing times were obtained from a single test run
  containing six classifications.
- Majority voting verification establishes logical fault
  tolerance rather than empirical classification reliability.
- All three classifiers rely on the same captured image.
  An incorrect capture could affect multiple classifiers.
- Two incorrect classifier predictions can result in an
  incorrect final classification.
- Concurrent classification and automatic stop-on-shiny
  behavior have not yet been verified.

Independent evaluation is necessary to establish
classification accuracy, precision, recall, false-positive
rates, and false-negative rates.

### Verification Summary

| Verification | Result |
|---|---|
| Game configuration loading | Pass |
| Reference dataset loading | Pass |
| Border classifier initialization | Pass |
| Star classifier initialization | Pass |
| Palette classifier initialization | Pass |
| Combined classification | 6/6 |
| Majority voting combinations | 8/8 |
| Single incorrect vote tolerance | Pass |
| Classification timing | Recorded |
| Independent dataset evaluation | Pending |
| Concurrent classification | Pending |
| Emulator integration | Pending |
| Automatic stop-on-shiny | Pending |