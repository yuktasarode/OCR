# Context

## Summary

Build an offline Python MVP that extracts a photographed handwritten donor table into CSV and XLSX. The future Android app is outside this iteration, but the CLI and output schema should be reusable by it.

## Workspace

- The initial workspace contains one 899x1599 JPEG and no source code or Git repository.
- No `CODEASSIST.md`, README, or other project instructions were present.
- The requested `.agents` documentation directory is read-only, so workflow artifacts live under `.code-assist`.
- Python 3.13 is available. Dependencies are isolated in `.venv`.

## Functional Requirements

- Accept one or more local JPEG/PNG images.
- Run OCR locally with an open-source engine and no hosted API.
- Extract unit number, donor name, blood group, contact number, confidence, and review status.
- Write a combined CSV and XLSX workbook.
- Preserve raw OCR text to support human correction.
- Compare predictions with user-supplied ground truth and write an accuracy report.
- Fail clearly for missing or unreadable input.

## Acceptance Criteria

- A CLI invocation produces readable CSV and XLSX files from the sample image.
- Multiple input paths append rows while retaining source-image identity.
- Accuracy includes exact field accuracy and character accuracy, rather than OCR confidence alone.
- Automated tests cover parsing, normalization, scoring, exports, and errors.
- The project runs entirely from `.venv` after dependency installation.

## Architecture and Dependencies

`CLI -> image loader -> RapidOCR -> fixed-form row/cell parser -> normalization -> CSV/XLSX`

`ground truth + extracted rows -> unit-number alignment -> exact/character metrics -> JSON report`

- RapidOCR ONNX Runtime: Apache-2.0 OCR implementation with bundled local models.
- OpenCV/Pillow: image loading and preprocessing.
- OpenPyXL: XLSX output.
- Pytest: automated tests.

## Implementation Paths

- `table_ocr/`: extraction, normalization, evaluation, export, and CLI modules.
- `tests/`: unit and integration-style tests using a fake OCR engine.
- `ground_truth/`: manually reviewed labels used only for evaluation.
- `output/`: generated MVP artifacts, excluded from source control.

## Uncertainties

- The source image clips several contact numbers at the right edge; those cells cannot be fairly scored as complete values.
- Handwritten cursive recognition is substantially harder than printed OCR. Confidence is not accuracy and must not be presented as such.
- The initial extractor targets this registration-form layout; a production app will need layout detection and a correction UI.
