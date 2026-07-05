# Offline Table OCR MVP

This Python MVP converts one or more photographed donor-registration tables into CSV and Excel files without sending images to a hosted service. It uses the open-source RapidOCR ONNX Runtime stack and currently targets the layout of the supplied registration form.

## Setup

```bash
python3 -m venv .venv
.venv/bin/python -m pip install -r requirements.txt
```

## Run

```bash
.venv/bin/python -m table_ocr.cli \
  "WhatsApp Image 2026-07-05 at 4.22.41 PM.jpeg" \
  --output output/donors \
  --ground-truth ground_truth/sample.csv
```

The command creates `output/donors.csv`, `output/donors.xlsx`, and `output/donors_accuracy.json`. Rows with uncertain, missing, or malformed fields have `needs_review=true`.

For multiple pages, list each image before `--output`. Rows are combined and retain their source filename.

## Accuracy

OCR confidence is not accuracy. The JSON report compares OCR output against reviewed labels and reports exact-field and normalized character accuracy. Empty ground-truth fields are excluded because the supplied photograph clips some phone numbers at its right edge.

The included ground truth is a manual transcription and should be reviewed by the data owner before treating the score as a formal benchmark.

### Current sample baseline

- Rows detected: 11 of 11
- Exact field accuracy: 38.46%
- Character accuracy: 62.36%
- Name character accuracy: 53.47%
- Complete-phone character accuracy: 53.33%
- Rows requiring review: 11 of 11

Unit numbers use the form's known sequential numbering to repair OCR and therefore score 100%; this is layout-assisted extraction, not pure handwriting recognition. The current result validates the local workflow and output format, but its handwriting accuracy is too low for unattended use. A correction screen should be part of the mobile/web MVP.

## Test

```bash
.venv/bin/python -m pytest
```
