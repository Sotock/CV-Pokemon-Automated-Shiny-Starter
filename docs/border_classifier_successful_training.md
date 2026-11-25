## Border Classification Verification

The border classifier uses normalized mean RGB values extracted
from a fixed region of interest (ROI). These features are passed
to a Linear Support Vector Machine (SVM) to classify the Pokémon
as normal or shiny.

### Configuration

- ROI: (20, 20, 17, 11)
- Feature extraction: Mean RGB
- Normalization: [0, 1]
- Classifier: Linear SVM
- Regularization parameter (C): 1.0
- Dataset: Six FireRed summary screenshots

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

| Classification | Red | Green | Blue |
|---|---:|---:|---:|
| Normal | 0.80784315 | 0.67843140 | 0.93725490 |
| Shiny | 0.41960785 | 0.90588236 | 0.90588236 |

### Console Output

```text
Border classifier trained.

Image: normal/001.png
RGB features: [0.80784315 0.6784314  0.9372549 ]
Expected: Normal
Predicted: Normal
Correct: True

Image: normal/004.png
RGB features: [0.80784315 0.6784314  0.9372549 ]
Expected: Normal
Predicted: Normal
Correct: True

Image: normal/007.png
RGB features: [0.80784315 0.6784314  0.9372549 ]
Expected: Normal
Predicted: Normal
Correct: True

Image: shiny/001.png
RGB features: [0.41960785 0.90588236 0.90588236]
Expected: Shiny
Predicted: Shiny
Correct: True

Image: shiny/004.png
RGB features: [0.41960785 0.90588236 0.90588236]
Expected: Shiny
Predicted: Shiny
Correct: True

Image: shiny/007.png
RGB features: [0.41960785 0.90588236 0.90588236]
Expected: Shiny
Predicted: Shiny
Correct: True

Correct classifications: 6/6
```

### Observations

The extracted RGB features remained consistent across all three
Pokémon species within their respective classifications.
The Linear SVM successfully distinguished between the normal
purple border and the shiny teal border.

All six reference images were correctly classified. However,
the same images were used for training and verification.
These results establish initial implementation correctness
rather than independent classification accuracy.