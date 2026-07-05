import csv
from pathlib import Path

from table_ocr.models import TableRow


def load_rows(path: Path) -> list[TableRow]:
    with path.open(newline="", encoding="utf-8") as handle:
        return [
            TableRow(
                record.get("source_image", ""),
                record.get("unit_no", ""),
                record.get("donor_name", ""),
                record.get("blood_group", ""),
                record.get("contact_no", ""),
                float(record.get("confidence", 0) or 0),
                str(record.get("needs_review", "")).lower() == "true",
                record.get("raw_ocr", ""),
            )
            for record in csv.DictReader(handle)
        ]
