## Palette Classification Verification

The palette classifier uses spatial RGB histograms extracted
from the Pokémon sprite region of interest (ROI). The extracted
histograms are compared against species-specific normal and
shiny reference histograms using Bhattacharyya distance.

The reference with the smaller distance determines the
classification.

### Configuration

| Parameter | Value |
|---|---|
| ROI | (24, 34, 72, 60) |
| ROI dimensions | 72 × 60 |
| Color space | RGB |
| Background removal | Species-specific foreground mask |
| Spatial grid | 2 × 2 |
| Color channels | 3 |
| Histogram bins per channel | 32 |
| Normalization | L1 |
| Feature vector length | 384 |
| Comparison method | Bhattacharyya distance |
| Dataset | Six FireRed summary screenshots |

### Foreground Mask Verification

Foreground masks are automatically generated using the normal
and shiny reference images for each Pokémon species. The
sprite region is extracted using the coordinates defined
in the game-specific JSON configuration.

White pixels represent the foreground pixels included in
histogram extraction, while black pixels represent the
excluded background.

| Pokémon | Sprite Isolation | Background Removal | Result |
|---|---|---|---|
| Bulbasaur | Successful | Successful | Pass |
| Charmander | Successful | Successful | Pass |
| Squirtle | Successful | Successful | Pass |

Visual verification confirmed that all three masks isolated
the Pokémon silhouettes without visible inclusion of the
border, shiny star, Poké Ball icon, or surrounding background.

This ensures that the palette classifier evaluates a
distinct visual indicator without relying on the features
used by the border and star classifiers.

### Classification Results

| Pokémon | Expected | Predicted | Result |
|---|---|---|---|
| Bulbasaur | Normal | Normal | Pass |
| Bulbasaur | Shiny | Shiny | Pass |
| Charmander | Normal | Normal | Pass |
| Charmander | Shiny | Shiny | Pass |
| Squirtle | Normal | Normal | Pass |
| Squirtle | Shiny | Shiny | Pass |

### Extracted Features

The Pokémon sprite ROI is divided into four spatial cells.
Each cell generates three normalized color histograms,
one for each RGB channel.

- 4 spatial cells
- 3 color channels per cell
- 32 histogram bins per channel

Total features: 4 × 3 × 32 = 384

Unlike a global RGB histogram, spatial histograms retain
some information regarding the distribution and location
of colors within the Pokémon sprite.

### Histogram Comparison Results

| Pokémon | Reference Distance |
|---|---:|
| Bulbasaur | 0.872202 |
| Charmander | 0.734454 |
| Squirtle | 0.705521 |

A Bhattacharyya distance of 0 represents identical
histograms, while a value approaching 1 represents
greater dissimilarity.

### Console Output

```text
Registered references: Bulbasaur
Registered references: Charmander
Registered references: Squirtle

Palette classifier initialized.

Pokemon: Bulbasaur
Histogram feature count: 384
Normal distance: 0.000000
Shiny distance: 0.872202
Expected: Normal
Predicted: Normal
Correct: True

Pokemon: Bulbasaur
Histogram feature count: 384
Normal distance: 0.872202
Shiny distance: 0.000000
Expected: Shiny
Predicted: Shiny
Correct: True

Pokemon: Charmander
Histogram feature count: 384
Normal distance: 0.000000
Shiny distance: 0.734454
Expected: Normal
Predicted: Normal
Correct: True

Pokemon: Charmander
Histogram feature count: 384
Normal distance: 0.734454
Shiny distance: 0.000000
Expected: Shiny
Predicted: Shiny
Correct: True

Pokemon: Squirtle
Histogram feature count: 384
Normal distance: 0.000000
Shiny distance: 0.705521
Expected: Normal
Predicted: Normal
Correct: True

Pokemon: Squirtle
Histogram feature count: 384
Normal distance: 0.705521
Shiny distance: 0.000000
Expected: Shiny
Predicted: Shiny
Correct: True

Correct classifications: 6/6

Process finished with exit code 0
```

### Observations

The spatial RGB histogram feature extractor consistently
generated 384 features for each reference image.

All three Pokémon exhibited substantial differences between
their normal and shiny reference histograms. Bulbasaur
exhibited the greatest histogram distance, followed by
Charmander and Squirtle.

Unlike the border and star classifiers, the palette
classifier requires species-specific reference data.

Visual verification of the automatically generated
foreground masks confirmed that all three Pokémon
silhouettes were successfully isolated from the
surrounding interface and background.

All six reference images were correctly classified. However,
the same images were used for reference generation and
verification. This explains the matching histogram distances
of 0.000000.

The current foreground masks also assume consistent sprite
positioning and rendering within the summary screen.

These results establish initial implementation correctness
rather than independent classification accuracy.

### Role in Majority Voting

The palette classifier provides one of three classification
votes in the shiny detection system. A positive prediction
contributes one shiny vote, while a negative prediction
contributes one normal vote.

The final classification requires at least two of the three
detectors to identify a shiny Pokémon.

This allows the system to tolerate a single incorrect
classification without interrupting the automated
hunting process.

### Verification Summary

| Verification | Result |
|---|---|
| Automatic ROI extraction | Pass |
| Foreground mask generation | Pass |
| Visual foreground mask verification | Pass |
| Background removal | Pass |
| Spatial histogram extraction | Pass |
| Feature vector consistency | Pass |
| Reference image classification | 6/6 |
| Independent evaluation | Pending |
| Majority voting integration | Pending |