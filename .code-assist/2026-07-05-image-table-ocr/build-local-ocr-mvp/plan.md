# Plan

## Test Scenarios

1. Normalize `B-213)` to `B-2131`, phone-like OCR characters to digits, and blood groups to canonical values.
2. Parse OCR detections into ordered table rows and retain unrecognized text for review.
3. Given expected and predicted rows aligned by unit number, return exact and character accuracy per field and overall.
4. Given rows from multiple images, write one CSV and an XLSX with Data and Summary sheets.
5. Reject missing image paths and empty input lists with actionable errors.
6. Use a fake OCR engine in tests so tests are deterministic and do not test a third-party model.

## Implementation

- Define a stable row record and canonical field normalizers.
- Detect table row bands and crop cells using normalized coordinates for the known form.
- Combine cell OCR with full-line OCR fallback and confidence-based review flags.
- Expose extraction, export, and evaluation through one CLI.
- Add a reviewed sample ground-truth file containing only fully visible fields.
- Run the sample, inspect outputs, and document measured limitations.

## Test Implementation

- Normalization tests cover common OCR substitutions in units, phones, and blood groups.
- Evaluation tests cover exact/character metrics and unavailable ground-truth fields.
- Export tests open the generated workbook and verify its sheets and data.
- Extraction orchestration tests cover multiple images, empty input, and missing files without invoking the third-party model.

## Risks and Mitigations

- Cursive OCR errors: retain raw text and mark low-confidence rows for human review.
- Clipped values: leave unknown expected fields blank and exclude them from field denominators.
- Layout coupling: isolate layout ratios in one configuration object for later replacement.
- Privacy: process locally and avoid network calls at runtime.
