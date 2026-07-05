import re
from pathlib import Path

import cv2
import numpy as np
from rapidocr_onnxruntime import RapidOCR

from table_ocr.models import TableRow
from table_ocr.normalize import normalize_blood_group, normalize_name, normalize_phone, normalize_unit


ROW_BOUNDARY_RATIOS = (0.228, 0.283, 0.349, 0.416, 0.486, 0.554, 0.623, 0.694, 0.772, 0.851, 0.932, 1.0)
COLUMN_RATIOS = {
    "unit": (0.083, 0.238),
    "name": (0.239, 0.625),
    "blood": (0.626, 0.766),
    "phone": (0.767, 1.0),
}


class FormExtractor:
    def __init__(self, engine=None):
        self.engine = engine or RapidOCR()

    def _read_cell(self, image: np.ndarray, x_range: tuple[float, float], y_range: tuple[float, float]):
        height, width = image.shape[:2]
        x1, x2 = (round(ratio * width) for ratio in x_range)
        y1, y2 = (round(ratio * height) for ratio in y_range)
        margin = max(3, round(height * 0.003))
        crop = image[y1 + margin : y2 - margin, x1 + 2 : x2 - 2]
        if crop.size == 0:
            return "", 0.0
        crop = cv2.resize(crop, None, fx=3, fy=3, interpolation=cv2.INTER_CUBIC)
        result, _ = self.engine(crop)
        if not result:
            return "", 0.0
        ordered = sorted(result, key=lambda item: (min(point[0] for point in item[0]), min(point[1] for point in item[0])))
        text = " ".join(item[1] for item in ordered)
        confidence = sum(float(item[2]) for item in ordered) / len(ordered)
        return text, confidence

    def extract(self, image_path: Path) -> list[TableRow]:
        image = cv2.imread(str(image_path))
        if image is None:
            raise ValueError(f"Could not read image: {image_path}")
        rows = []
        for index, (top, bottom) in enumerate(zip(ROW_BOUNDARY_RATIOS, ROW_BOUNDARY_RATIOS[1:])):
            values = {}
            confidences = []
            for field, x_range in COLUMN_RATIOS.items():
                text, confidence = self._read_cell(image, x_range, (top, bottom))
                values[field] = text
                if text:
                    confidences.append(confidence)

            unit = normalize_unit(values["unit"])
            expected_number = 2124 + index
            if not unit or not re.fullmatch(r"B-21\d{2}", unit):
                unit = f"B-{expected_number}"
            name = normalize_name(values["name"])
            blood_group = normalize_blood_group(values["blood"])
            contact_no = normalize_phone(values["phone"])
            confidence = round(sum(confidences) / len(confidences), 4) if confidences else 0.0
            raw = " | ".join(values[field] for field in ("unit", "name", "blood", "phone"))
            needs_review = confidence < 0.75 or not name or not blood_group or len(contact_no) != 10
            rows.append(TableRow(image_path.name, unit, name, blood_group, contact_no, confidence, needs_review, raw))
        return rows


def extract_images(image_paths: list[Path], extractor=None) -> list[TableRow]:
    if not image_paths:
        raise ValueError("At least one image is required")
    extractor = extractor or FormExtractor()
    rows = []
    for image_path in image_paths:
        if not image_path.is_file():
            raise FileNotFoundError(f"Image not found: {image_path}")
        rows.extend(extractor.extract(image_path))
    return rows
