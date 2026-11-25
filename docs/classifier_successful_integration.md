# Computer Vision Integration and Summary Validation

## Objective

Integrate the existing computer vision classifiers directly into emulator instances and implement a lightweight summary screen validation mechanism.

The validation mechanism determines whether an automated macro rotation has reached the expected Pokémon summary screen before shiny classification occurs. This prevents unsuccessful macro rotations and incorrect target species from being treated as valid encounters.

The implementation is designed to minimize processing overhead while supporting multiple concurrent emulator instances.

## Implementation

| Component | Responsibility |
|---|---|
| `instances/library_manager.py` | Live framebuffer retrieval, image conversion, and profile-driven classification. |
| `vision/shiny_detector.py` | Combined classifier initialization, summary validation interface, and majority voting. |
| `vision/summary_validator.py` | Summary screen and target species verification. |
| `vision/configurations/firered_leafgreen.json` | Classifier and validation region definitions. |
| `tests/vision/test_shiny_detector.py` | Reference classification, majority voting, and summary validation testing. |
| `tests/integration/test_vision_integration.py` | Live emulator integration and independent encounter evaluation. |

## Live Framebuffer Integration

Each emulator instance obtains its target species and computer vision configuration directly from its selected profile.

The shiny detector is initialized when classification is first requested and retained throughout the lifetime of the emulator instance. This avoids repeated classifier initialization between encounters.

Following macro execution, the framebuffer is retrieved directly from the emulator and converted from RGB to OpenCV's BGR color format.

```python
frame = self.screen.to_pil().convert("RGB")

image = cv2.cvtColor(
    np.asarray(frame),
    cv2.COLOR_RGB2BGR
)
```

The resulting image is supplied to the combined shiny detector alongside the configured target species.

Classification operates directly on the framebuffer without requiring the saved screenshot to be loaded from disk.

Screenshot generation is retained for experimental verification and diagnostic purposes.

### Classification Architecture

The existing three shiny classifiers remain unchanged:

| Classifier | Method |
|---|---|
| Border classifier | RGB mean color features and linear SVM |
| Star classifier | Histogram of Oriented Gradients and linear SVM |
| Palette classifier | Spatial RGB histogram comparison |

Each classifier independently produces a binary shiny prediction.

The final classification uses strict majority voting:

```python
is_shiny = votes >= 2
```

At least two classifiers must predict shiny for the combined detector to produce a shiny classification.

## Live Integration Verification

One automated encounter was executed for each FireRed starter to verify compatibility between profile management, macro execution, framebuffer retrieval, and computer vision classification.

| Species | Species ID | Border | Star | Palette | Shiny Votes | Prediction |
|---|---|---|---|---|---:|---|
| Bulbasaur | 001 | Normal | Normal | Normal | 0/3 | Normal |
| Charmander | 004 | Normal | Normal | Normal | 0/3 | Normal |
| Squirtle | 007 | Normal | Normal | Normal | 0/3 | Normal |

For each encounter, classification was performed using both the live framebuffer and the corresponding saved screenshot.

| Verification | Bulbasaur | Charmander | Squirtle |
|---|---|---|---|
| Macro execution | PASS | PASS | PASS |
| Live framebuffer classification | PASS | PASS | PASS |
| Live and saved classification agreement | PASS | PASS | PASS |
| Majority voting consistency | PASS | PASS | PASS |
| Temporary instance cleanup | PASS | PASS | PASS |
| Permanent save preservation | PASS | PASS | PASS |

### Live Classification Performance

Each framebuffer was classified repeatedly to measure the processing overhead associated with image retrieval, color conversion, classifier inference, and majority voting.

A total of 100 repeated classifications were performed for each starter.

| Species | Average Processing Time |
|---|---:|
| Bulbasaur | 0.2833 ms |
| Charmander | 0.2079 ms |
| Squirtle | 0.2231 ms |
| Overall average | 0.2381 ms |

These measurements exclude initial classifier initialization, macro execution, and screenshot generation.

The results demonstrate that direct framebuffer classification introduces minimal processing overhead during individual encounters.

## Summary Screen Validation

The shiny classifiers operate on predefined regions of interest and assume that the supplied image represents a valid Pokémon summary screen.

An unsuccessful macro rotation may instead produce an unrelated game screen. Applying the shiny classifiers directly to such an image could produce an invalid classification.

To address this limitation, a separate summary validation mechanism was implemented using fixed-region pixel comparison.

### Validation Regions

Static interface elements were identified using the existing normal and shiny reference captures.

The selected regions remain independent of the Pokémon's shiny appearance, nature, gender, and trainer information within the evaluated reference images.

| Region | X | Y | Width | Height | Pixels |
|---|---:|---:|---:|---:|---:|
| Pokémon Info header | 2 | 2 | 76 | 12 | 912 |
| Information labels | 123 | 22 | 41 | 85 | 3,485 |
| Trainer Memo header | 5 | 103 | 75 | 10 | 750 |
| Species number | 166 | 22 | 20 | 11 | 220 |
| Total | | | | | 5,367 |

All coordinates correspond to the native 240 x 160 emulator framebuffer.

The validation regions are defined separately from the existing shiny classifier regions.

```json
"validation_regions": {
    "summary_header": [2, 2, 76, 12],
    "information_labels": [123, 22, 41, 85],
    "trainer_memo": [5, 103, 75, 10],
    "species_number": [166, 22, 20, 11]
}
```

### Template Initialization

The summary validator retrieves reference regions from the existing unmodified normal Pokémon captures.

Static summary templates are checked for consistency across the available reference species during initialization.

Species-specific templates are extracted from the Pokédex number region and associated with their respective species identifiers.

| Species | Identifier |
|---|---|
| Bulbasaur | 001 |
| Charmander | 004 |
| Squirtle | 007 |

All templates are cached in memory.

No additional reference image files or trained classifiers are required.

### Validation Method

The validator first verifies the framebuffer dimensions and confirms that the requested species has an available reference template.

Each static region is then compared against its corresponding cached reference using NumPy's exact array equality operation.

```python
np.array_equal(region, template)
```

If any static region fails comparison, the summary is rejected.

The species number region is subsequently compared against the expected target species template.

A summary is accepted only when all static regions and the expected species number match.

Exact pixel comparison was selected because emulator framebuffers provide native digital image data without photographic noise, perspective distortion, or lossy image compression.

This method avoids sliding-window template searches, image resizing, additional model training, and repeated disk access.

## Reference Image Verification

The summary validator was initially evaluated using the six existing normal and shiny reference captures.

These captures were also used during the original classifier initialization and therefore do not represent an independent evaluation dataset.

### Combined Detector Regression Results

| Verification | Successful | Total |
|---|---:|---:|
| Reference shiny classification | 6 | 6 |
| Majority voting combinations | 8 | 8 |
| Valid summary acceptance | 6 | 6 |
| Incorrect species rejection | 12 | 12 |

All three normal reference images produced zero shiny votes.

All three shiny reference images produced three shiny votes.

The existing majority voting implementation continued to produce the correct result for all eight possible binary classifier combinations.

### Reference Summary Acceptance

| Species | Normal Reference | Shiny Reference |
|---|---|---|
| Bulbasaur | PASS | PASS |
| Charmander | PASS | PASS |
| Squirtle | PASS | PASS |

Each reference image was also evaluated against the two incorrect starter species identifiers.

All 12 incorrect species comparisons were rejected.

### Reference Processing Performance

| Metric | Processing Time |
|---|---:|
| Detector and validator initialization | 13.115 ms |
| Average shiny classification | 0.1829 ms |
| Average summary validation | 0.0117 ms |
| Estimated combined processing time | 0.1946 ms |

The summary validation benchmark consisted of 1,000 repeated comparisons against a valid reference image.

The additional validation time represents approximately 6.4% of the measured classifier inference time.

The combined processing time is calculated from the separately measured averages rather than measured directly as a combined operation.

## Independent Encounter Evaluation

### Dataset

Previously generated screenshots from the final macro reliability experiment were reused to evaluate summary validation and shiny classification on encounters outside the original reference dataset.

The evaluation dataset consisted of 140 successful starter encounters generated through automated emulator instances.

| Species | Emulator Instances | Captures |
|---|---:|---:|
| Bulbasaur | 10 | 100 |
| Charmander | 2 | 20 |
| Squirtle | 2 | 20 |
| Total | 14 | 140 |

Each emulator instance contributed ten captures.

The screenshots were retained within their original instance-specific directories.

These images were not used during classifier training or validation template initialization.

The dataset includes naturally generated variation in Pokémon nature and gender.

### Evaluation Methodology

Each image was loaded at its original framebuffer resolution.

The expected species was assigned according to the target of its originating emulator instance.

The following operations were performed for each capture:

- Validate the summary against its expected species.
- Record whether the summary was accepted or rejected.
- Classify accepted summaries using the combined shiny detector.
- Record the final normal or shiny prediction.
- Evaluate the summary against both incorrect species identifiers.
- Measure summary validation and classification processing times.

The evaluation reused existing captures without executing additional emulator rotations or modifying the reference dataset.

### Summary Acceptance Results

| Species | Total Captures | Accepted | Rejected | Acceptance Rate |
|---|---:|---:|---:|---:|
| Bulbasaur | 100 | 100 | 0 | 100% |
| Charmander | 20 | 20 | 0 | 100% |
| Squirtle | 20 | 20 | 0 | 100% |
| Total | 140 | 140 | 0 | 100% |

All 140 independently generated valid summaries were accepted.

The observed encounter-specific variations did not interfere with the selected validation regions.

### Incorrect Species Rejection Results

Each accepted summary was evaluated against both incorrect starter species identifiers.

| Actual Species | Incorrect Species Comparisons | Rejected | Incorrectly Accepted |
|---|---:|---:|---:|
| Bulbasaur | 200 | 200 | 0 |
| Charmander | 40 | 40 | 0 |
| Squirtle | 40 | 40 | 0 |
| Total | 280 | 280 | 0 |

All 280 incorrect species comparisons were rejected.

The results demonstrate that the species number region successfully distinguishes the three supported FireRed starters within the evaluated dataset.

### Independent Shiny Classification Results

| Species | Captures | Normal Predictions | Shiny Predictions |
|---|---:|---:|---:|
| Bulbasaur | 100 | 100 | 0 |
| Charmander | 20 | 20 | 0 |
| Squirtle | 20 | 20 | 0 |
| Total | 140 | 140 | 0 |

The combined shiny detector produced normal predictions for all 140 independent encounter captures.

These predictions are consistent with the previously observed normal appearances of the captured encounters.

Assuming the original visual ground-truth labels are correct, the observed normal classification accuracy is 100%, with no observed false-positive shiny predictions.

The independent dataset does not contain confirmed shiny-positive encounters. Consequently, independent shiny recall and overall balanced classification accuracy cannot be established from this experiment alone.

### Independent Processing Performance

Processing times were recorded separately for summary validation and shiny classification.

| Metric | Average Processing Time |
|---|---:|
| Summary validation | 0.0331 ms |
| Shiny classification | 0.1992 ms |
| Estimated combined processing time | 0.2323 ms |

The combined processing time was calculated by summing the independently measured averages.

These measurements exclude screenshot loading, emulator execution, framebuffer conversion, incorrect species comparisons, and concurrent processing contention.

The results demonstrate that summary validation and shiny classification can be performed with minimal per-encounter computational overhead.

## Aggregate Verification Results

| Evaluation | Successful | Total |
|---|---:|---:|
| Reference shiny classification | 6 | 6 |
| Majority voting verification | 8 | 8 |
| Reference summary acceptance | 6 | 6 |
| Reference incorrect species rejection | 12 | 12 |
| Independent summary acceptance | 140 | 140 |
| Independent incorrect species rejection | 280 | 280 |
| Independent normal predictions | 140 | 140 |

Reference image results and independent encounter results are reported separately because the reference images were used during classifier and template initialization.

Incorrect species comparisons also represent repeated evaluations of existing images rather than additional independent encounters.

## Concurrent Execution Considerations

The application is intended to support multiple simultaneous hunting instances, including mixed FireRed and Sapphire workloads.

The current design targets up to ten concurrent emulator instances.

The computer vision implementation supports this objective through:

- Detector initialization once per hunting instance.
- Cached summary validation templates.
- Direct framebuffer classification.
- Fixed-region pixel comparisons.
- Lightweight feature extraction and classifier inference.
- Avoidance of repeated screenshot loading during hunting.

The measured computer vision processing times suggest that emulator execution and system resource contention are more likely to limit overall hunting throughput than individual classification operations.

However, concurrent performance at the ten-instance target has not yet been established experimentally.

## Limitations

- Independent validation has been conducted using successful FireRed summary captures.
- Representative failed macro screenshots have not yet been evaluated using the summary validator.
- Incorrect species rejection does not establish rejection accuracy for unrelated game screens.
- Independent shiny-positive classification remains unverified.
- Exact pixel matching may reject otherwise valid summaries if the expected interface appearance changes.
- Summary validation has been implemented and tested separately but has not yet been connected to automatic macro restart behavior.
- Continuous hunting, automatic shiny stopping, and encounter statistics require additional integration.
- Sapphire requires its own validation regions, reference captures, and classification evaluation.
- Ten-instance concurrent performance remains a design objective rather than a verified experimental result.

## Conclusion

The existing computer vision system was successfully integrated with live emulator framebuffers without modifying the established shiny classification methods or majority voting mechanism.

A lightweight summary validation mechanism was implemented using fixed-region pixel comparison and cached reference templates.

The validator accepted all 140 independently generated valid summary captures and rejected all 280 incorrect species comparisons. The combined shiny detector produced normal predictions for all 140 independent encounters.

The measured average summary validation time of 0.0331 ms and average classification time of 0.1992 ms demonstrate minimal per-encounter processing overhead.

These results establish successful live computer vision integration and provide independent evidence supporting summary acceptance, species verification, and normal encounter classification.