# Progress

## Checklist

- [x] Parameters acquired; auto mode selected.
- [x] Workspace and sample image inspected.
- [x] Documentation structure created in writable fallback location.
- [x] Requirements, dependencies, and test strategy documented.
- [x] Tests written and RED state recorded.
- [x] Extraction and export implementation completed.
- [x] Tests and build validation passed.
- [x] Sample output and accuracy report generated.
- [ ] Git commit created (blocked: workspace `.git` directory is read-only).

## Setup Notes

- `.agents` is mounted read-only; `.code-assist` is the documentation fallback.
- No Git repository exists yet.
- Initial dependency installation used `.vendor`; after user feedback, a proper `.venv` was created and all subsequent commands use it.
- Raw RapidOCR confirms detection of most rows but shows expected cursive handwriting errors and merged columns.

## TDD Cycle

- RED: test collection failed with `ModuleNotFoundError: table_ocr`, confirming the implementation was absent.
- GREEN: implemented normalization, extraction orchestration, evaluation, and export; 9 tests pass.
- REFACTOR: aligned the accuracy report key with the public `donor_name` schema and kept OCR engine injection available for deterministic tests.

## Sample Result

- Detected 11 of 11 expected rows.
- Overall exact field accuracy: 38.46% across 39 available fields.
- Overall normalized character accuracy: 62.36%.
- Unit exact accuracy: 100% (layout-assisted sequential repair).
- Donor-name character accuracy: 53.47%.
- Complete-contact character accuracy: 53.33%.
- All 11 rows require review, demonstrating that confidence thresholds prevent silent acceptance of this weak handwriting baseline.

## Commit Status

- `git init` failed because the workspace-provided `.git/hooks` path is read-only.
- No commit was created; all implementation and validation work is present in the working directory.

## Decisions

- Use RapidOCR ONNX Runtime as the open-source, offline runtime baseline.
- Report ground-truth accuracy separately from model confidence.
- Score blank ground-truth fields as unavailable, not incorrect, because several values are clipped in the photograph.
