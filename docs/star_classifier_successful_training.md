## Star Classification Verification

The star classifier uses Histogram of Oriented Gradients (HOG)
features extracted from a fixed region of interest (ROI).
These features are passed to a Linear Support Vector Machine
(SVM) to determine whether the shiny star indicator is present.

### Configuration

| Parameter | Value |
|---|---|
| ROI | (100, 34, 12, 12) |
| Original ROI dimensions | 12 × 12 |
| Resized ROI dimensions | 32 × 32 |
| Interpolation | Nearest-neighbor |
| Color conversion | Grayscale |
| Block size | 16 × 16 |
| Block stride | 8 × 8 |
| Cell size | 8 × 8 |
| Orientation bins | 9 |
| Feature vector length | 324 |
| Classifier | Linear SVM |
| Regularization parameter (C) | 1.0 |
| Dataset | Six FireRed summary screenshots |

### Classification Results

| Pokémon | Expected | Predicted | Result |
|---|---|---|---|
| Bulbasaur | Normal | Normal | Pass |
| Charmander | Normal | Normal | Pass |
| Squirtle | Normal | Normal | Pass |
| Bulbasaur | Shiny | Shiny | Pass |
| Charmander | Shiny | Shiny | Pass |
| Squirtle | Shiny | Shiny | Pass |

### Extracted Features

Each image generates a HOG feature vector containing 324
values based on the following configuration:

- 9 overlapping blocks per detection window
- 4 cells per block
- 9 orientation bins per cell

Total features: 9 × 4 × 9 = 324

### Console Output

```text
Star classifier trained.

Image: normal/001.png
HOG feature count: 324
Expected: Normal
Predicted: Normal
Correct: True

Image: normal/004.png
HOG feature count: 324
Expected: Normal
Predicted: Normal
Correct: True

Image: normal/007.png
HOG feature count: 324
Expected: Normal
Predicted: Normal
Correct: True

Image: shiny/001.png
HOG feature count: 324
Expected: Shiny
Predicted: Shiny
Correct: True

Image: shiny/004.png
HOG feature count: 324
Expected: Shiny
Predicted: Shiny
Correct: True

Image: shiny/007.png
HOG feature count: 324
Expected: Shiny
Predicted: Shiny
Correct: True

Correct classifications: 6/6

Process finished with exit code 0
```

### Observations

The HOG feature extractor consistently generated 324 features
for each reference image. The Linear SVM successfully
distinguished between regions containing the shiny star
and regions without the shiny star.

Unlike the border classifier, which relies on color information,
the star classifier relies on the spatial distribution of
gradient orientations.

The selected ROI excludes the Pokémon sprite and variable
summary information, allowing classification without relying
on species-specific characteristics.

All six reference images were correctly classified. However,
the same images were used for training and verification.
These results establish initial implementation correctness
rather than independent classification accuracy.

### Role in Majority Voting

The star classifier provides one of three independent
classification votes in the shiny detection system.
A positive prediction contributes one shiny vote, while
a negative prediction contributes one normal vote.

The final classification requires at least two of the three
detectors to identify a shiny Pokémon.