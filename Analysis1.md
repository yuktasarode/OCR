# OCR Accuracy Analysis

## Why The Current Accuracy Is Low

The current exact-field accuracy is 38.46%, and normalized character accuracy is 62.36%. The primary reason is that the bundled RapidOCR recognition model is intended mainly for printed text, while the supplied registration form contains difficult cursive handwriting.

Additional factors reduce recognition quality:

- The photograph is angled, and the paper is slightly curved.
- Table borders cross or touch handwritten characters.
- Names contain multiple words, inconsistent spacing, and connected cursive letters.
- Blood-group cells contain corrections, overwritten text, and crossed-out values.
- Several phone numbers are clipped at the right edge of the photograph.
- The `BAG` cells contain circled marks rather than conventional text.
- Only one labeled image is currently available, so the measured score is not yet statistically reliable.
- Unit numbers receive layout-assisted sequential correction, which makes the combined score higher than pure OCR performance would be.

No OCR model can recover characters that are outside the photograph. Clipped values must be recaptured or manually reviewed.

## Why Evaluate A Different Model

A newer model is not automatically better. The relevant question is whether the model was trained for the type of content being recognized.

RapidOCR is useful for text detection, table-region processing, and printed text. A handwriting-specific model such as a TrOCR handwritten checkpoint is designed to recognize cropped handwritten words or lines. It may therefore improve donor-name recognition, but it must be benchmarked rather than assumed to be better.

The proposed experiment is not an unconditional replacement of RapidOCR. Both models should process the same cell crops and be evaluated against the same reviewed ground truth. The better recognizer can then be selected for each field.

## Recommended Field-Specific Approach

- **Donor names:** Compare RapidOCR with a handwriting-specific TrOCR checkpoint.
- **Phone numbers:** Use digit-focused preprocessing, restricted character recognition, and 10-digit validation.
- **Unit numbers:** Use OCR plus the known `B-####` format and sequential-layout validation.
- **Blood groups:** Restrict normalization to valid values such as `A+`, `A-`, `B+`, `B-`, `AB+`, `AB-`, `O+`, and `O-`.
- **Bag marks:** Treat them as symbols or shapes, or leave them for manual review until their meaning is defined.
- **Clipped or missing values:** Flag them for recapture or manual correction rather than guessing.

## Image Processing Improvements

Recognition should be tested after applying:

1. Perspective correction and deskewing.
2. Table-line removal before text recognition.
3. Contrast enhancement and grayscale normalization.
4. Tight cell and text-line cropping.
5. Separate preprocessing settings for names and numbers.
6. Confidence and format checks that route uncertain fields to manual review.

## How To Measure Improvement

Accuracy should be reported separately for unit numbers, names, blood groups, phone numbers, and bag marks. A single combined score can hide a weak field behind a strong one.

The benchmark should include:

- Exact-field accuracy.
- Character accuracy or character error rate.
- Row-detection accuracy.
- Percentage of fields requiring manual review.
- Processing time per image.
- Results for each OCR model using identical images and ground truth.

The current ground-truth CSV should be reviewed by the data owner, and several additional representative images should be labeled before making a production decision. One image is sufficient for a technical proof of concept, but not for a reliable accuracy claim.

## Recommended Next Step

Keep the existing table extraction and export pipeline. Add a handwriting-recognition option for donor-name cells, improve field-specific preprocessing, and run a controlled RapidOCR-versus-TrOCR benchmark. Adopt a new model only if it produces a meaningful measured improvement without unacceptable processing time or deployment size.
