# Offline Table OCR MVP

This Python MVP converts one or more photographed donor-registration tables into CSV and Excel files without sending images to a hosted service. It uses the open-source RapidOCR ONNX Runtime stack and currently targets the layout of the supplied registration form.

## Current Status

- Outputs: `output/donors.csv`, `output/donors.xlsx`
- Accuracy: 41.03% exact fields, 76.70% character accuracy. See `reports/sample_accuracy.json`
- Tests: 13 passed

The local OCR pipeline is implemented. The frontend, upload API, hosting, and Play Store release described later in this README are the planned next phases.

## Prerequisites

- Python 3.11 or newer (currently tested with Python 3.13)
- Linux, macOS, or Windows with enough disk space for the local ONNX OCR dependencies
- No hosted OCR account or API key is required

## Local Setup

From the project directory, create a virtual environment and install the pinned dependencies:

```bash
python3 -m venv .venv
.venv/bin/python -m pip install -r requirements-handwriting.txt
```

On Windows PowerShell, activate the environment with `.venv\Scripts\Activate.ps1` and use `python` in place of `.venv/bin/python` in the commands below.

The first TrOCR run downloads the open-source handwriting model into `.models`. Later runs can set `HF_HUB_OFFLINE=1` to prevent all model-network checks.

## Run The Sample

```bash
HF_HOME=.models .venv/bin/python -m table_ocr.cli \
  sample.jpeg \
  --output output/donors \
  --ground-truth ground_truth/sample.csv \
  --name-engine trocr
```

The command creates `output/donors.csv`, `output/donors.xlsx`, and `output/donors_accuracy.json`. Rows with uncertain, missing, or malformed fields have `needs_review=true`.

Open `output/donors.xlsx` with Excel or LibreOffice. The `Data` sheet contains extracted rows, and the `Summary` sheet contains row counts, review counts, average OCR confidence, and blood-group totals.

## Run With Multiple Images

List all input images before the options. Rows are combined into one CSV/workbook and retain their source filename.

```bash
.venv/bin/python -m table_ocr.cli \
  page-1.jpg page-2.jpg page-3.png \
  --output output/all-donors
```

To calculate accuracy, first prepare a reviewed CSV using the columns in `ground_truth/sample.csv`, then add:

```bash
--ground-truth ground_truth/your-reviewed-data.csv
```

## Accuracy

OCR confidence is not accuracy. The JSON report compares OCR output against reviewed labels and reports exact-field and normalized character accuracy. Empty ground-truth fields are excluded because the supplied photograph clips some phone numbers at its right edge.

The included ground truth is a manual transcription and should be reviewed by the data owner before treating the score as a formal benchmark.

### Current sample result

- Rows detected: 11 of 11
- Exact accuracy: 38.46% -> 41.03%
- Character accuracy: 62.36% -> 76.70%
- Name accuracy: 53.47% -> 69.74%
- Phone accuracy: 53.33% -> 80.00%
- Tests: 13 passed
- Rows requiring review: 11 of 11

Compared with the original RapidOCR-only baseline, exact accuracy increased from 38.46% to 41.03%, and character accuracy increased from 62.36% to 76.70%. The original result is retained in `reports/sample_accuracy_baseline.json`.

After the model has been downloaded once, run without model network access:

```bash
HF_HOME=.models HF_HUB_OFFLINE=1 .venv/bin/python -m table_ocr.cli \
  sample.jpeg \
  --output output/donors \
  --ground-truth ground_truth/sample.csv \
  --name-engine trocr
```

Unit numbers use the form's known sequential numbering to repair OCR and therefore score 100%; this is layout-assisted extraction, not pure handwriting recognition. The current result validates the local workflow and output format, but its handwriting accuracy is too low for unattended use. A correction screen should be part of the mobile/web MVP.

## Run Tests

```bash
.venv/bin/python -m pytest
```

The current suite contains 13 tests covering preprocessing, recognizer routing, normalization, accuracy calculations, multi-image handling, error handling, CSV export, and XLSX export.

## Output Columns

| Column | Meaning |
| --- | --- |
| `source_image` | Input image that produced the row |
| `bag` | Raw OCR value from the form's `BAG` column |
| `unit_no` | Extracted registration unit number |
| `donor_name` | Extracted handwritten donor name |
| `blood_group` | Normalized blood group such as `B+` |
| `contact_no` | Extracted contact number |
| `confidence` | OCR model confidence, not measured accuracy |
| `needs_review` | `true` when a person should verify the row |
| `raw_ocr` | Unmodified OCR fragments used to produce the row |

## Frontend Plan

The recommended frontend is Expo with React Native so most UI code can be shared between Android and the web through React Native Web.

1. Create an Expo application with camera and gallery permissions.
2. Let the user select or photograph one or more pages.
3. Show selected images, allow removal/reordering, and submit them as one job.
4. Display extracted rows in an editable review table before export.
5. Highlight every `needs_review=true` field and validate 10-digit phone numbers.
6. Download/share the corrected CSV or XLSX file.
7. Add job progress, retry behavior, privacy messaging, and automatic deletion details.

React Native does not automatically make an Android application usable as a website. Expo/React Native Web must be configured and each camera, file-picker, download, and sharing feature must be tested separately in Android and web browsers. A responsive PWA is another option if Play Store distribution is not initially required.

## Backend Plan

The existing `table_ocr` package remains the OCR core. A thin API can be added without moving extraction logic into the frontend.

1. Add a FastAPI service with a multipart `POST /jobs` endpoint for one or more images.
2. Run OCR in a background job and expose `GET /jobs/{id}` for progress and results.
3. Add a correction endpoint so reviewed values can be exported and retained as evaluation data.
4. Return CSV/XLSX downloads using the existing export module.
5. Enforce file type, file size, image count, authentication, rate limits, and short retention periods.
6. Delete uploaded donor data after export and avoid logging names or phone numbers.
7. Package the API and OCR model in Docker and add API/integration tests.

For the first hosted version, one API process can handle small jobs synchronously. Add a queue and worker only when concurrent requests or OCR timeouts make it necessary.

## Deployment Plan

### Web MVP

1. Deploy the FastAPI Docker image to a service with persistent CPU and enough memory for ONNX Runtime.
2. Deploy the Expo web build to static hosting.
3. Configure HTTPS, API CORS for the frontend domain, upload limits, and environment-based API URLs.
4. Store files only temporarily on the API host or in private object storage with automatic expiry.
5. Run an end-to-end test from a real phone browser before sharing the URL.

Static-only hosting cannot execute this Python OCR pipeline. The website can be static, but it still needs the hosted API unless OCR is later replaced with an on-device/browser-compatible model.

### Android And Play Store

1. Build the Expo Android application and point it to the production HTTPS API.
2. Test camera/gallery selection, large uploads, correction, download, and sharing on physical Android devices.
3. Add app identity, icons, screenshots, privacy policy, support contact, and data-deletion policy.
4. Create a signed Android App Bundle with EAS Build or the native Android toolchain.
5. Complete Play Console data-safety declarations and use an internal testing track first.
6. Promote to closed testing and production after OCR review flows and privacy controls are verified.

## Recommended Delivery Order

1. Review and correct `ground_truth/sample.csv`, then rerun the baseline.
2. Improve handwriting and table extraction until target field-level accuracy is agreed.
3. Build the FastAPI upload/export API locally.
4. Build the Expo review UI against the local API.
5. Deploy a private web MVP for real-device testing.
6. Package Android and start Play Store internal testing.
