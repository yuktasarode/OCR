import argparse
import json
from pathlib import Path

from table_ocr.evaluate import evaluate_rows
from table_ocr.export import export_rows
from table_ocr.extract import extract_images
from table_ocr.extract import FormExtractor
from table_ocr.io import load_rows
from table_ocr.recognizers import TrOCRRecognizer


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Convert photographed donor tables to CSV and XLSX using local OCR.")
    parser.add_argument("images", nargs="+", type=Path, help="One or more local image paths")
    parser.add_argument("--output", type=Path, default=Path("output/donors"), help="Output path without extension")
    parser.add_argument("--ground-truth", type=Path, help="Reviewed CSV used to calculate OCR accuracy")
    parser.add_argument("--name-engine", choices=("rapidocr", "trocr"), default="rapidocr", help="Recognizer for donor-name cells")
    parser.add_argument("--trocr-model", default="microsoft/trocr-small-handwritten", help="TrOCR checkpoint used for donor names")
    return parser


def main() -> int:
    args = build_parser().parse_args()
    name_recognizer = TrOCRRecognizer(args.trocr_model) if args.name_engine == "trocr" else None
    rows = extract_images(args.images, FormExtractor(name_recognizer=name_recognizer))
    csv_path, xlsx_path = export_rows(rows, args.output)
    print(f"Extracted {len(rows)} rows")
    print(f"CSV: {csv_path}")
    print(f"XLSX: {xlsx_path}")
    if args.ground_truth:
        report = evaluate_rows(load_rows(args.ground_truth), rows)
        report_path = args.output.with_name(f"{args.output.name}_accuracy.json")
        report_path.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
        print(f"Accuracy: {report_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
