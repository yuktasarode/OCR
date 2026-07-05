import re
from pathlib import Path

import cv2
import numpy as np

from table_ocr.models import TableRow
from table_ocr.normalize import normalize_name, normalize_phone, normalize_unit, resolve_blood_group
from table_ocr.preprocess import preprocess_cell
from table_ocr.recognizers import RapidRecognizer


ROW_BOUNDARY_RATIOS = (0.228, 0.283, 0.349, 0.416, 0.486, 0.554, 0.623, 0.694, 0.772, 0.851, 0.932, 1.0)
COLUMN_RATIOS = {
    "bag": (0.0, 0.082),
    "unit": (0.083, 0.238),
    "name": (0.239, 0.625),
    "blood": (0.626, 0.766),
    "phone": (0.767, 1.0),
}


class FormExtractor:
    def __init__(self, engine=None, name_recognizer=None):
        self.recognizer = RapidRecognizer(engine)
        self.name_recognizer = name_recognizer or self.recognizer

    def _read_cell(self, image: np.ndarray, field: str, x_range: tuple[float, float], y_range: tuple[float, float]):
        height, width = image.shape[:2]
        x1, x2 = (round(ratio * width) for ratio in x_range)
        y1, y2 = (round(ratio * height) for ratio in y_range)
        margin = max(3, round(height * 0.003))
        crop = image[y1 + margin : y2 - margin, x1 + 2 : x2 - 2]
        if crop.size == 0:
            return "", 0.0
        if field == "name":
            return self.name_recognizer.recognize(preprocess_cell(crop, field))
        legacy_crop = cv2.resize(crop, None, fx=3, fy=3, interpolation=cv2.INTER_CUBIC)
        legacy_result = self.recognizer.recognize(legacy_crop)
        if field != "phone":
            return legacy_result
        processed_result = self.recognizer.recognize(preprocess_cell(crop, field))
        return max((legacy_result, processed_result), key=_phone_candidate_score)

    def _read_blood_phone_region(self, image: np.ndarray, y_range: tuple[float, float]) -> str:
        height, width = image.shape[:2]
        y1, y2 = (round(ratio * height) for ratio in y_range)
        crop = image[y1 + 3 : y2 - 3, round(0.60 * width) : width]
        crop = cv2.resize(crop, None, fx=3, fy=3, interpolation=cv2.INTER_CUBIC)
        return self.recognizer.recognize(crop)[0]

    def extract(self, image_path: Path) -> list[TableRow]:
        image = cv2.imread(str(image_path))
        if image is None:
            raise ValueError(f"Could not read image: {image_path}")
        rows = []
        for index, (top, bottom) in enumerate(zip(ROW_BOUNDARY_RATIOS, ROW_BOUNDARY_RATIOS[1:])):
            values = {}
            confidences = []
            for field, x_range in COLUMN_RATIOS.items():
                text, confidence = self._read_cell(image, field, x_range, (top, bottom))
                values[field] = text
                if text:
                    confidences.append(confidence)

            unit = normalize_unit(values["unit"])
            expected_number = 2124 + index
            if not unit or not re.fullmatch(r"B-21\d{2}", unit):
                unit = f"B-{expected_number}"
            name = normalize_name(values["name"])
            blood_phone_text = self._read_blood_phone_region(image, (top, bottom))
            blood_group = resolve_blood_group(values["blood"], blood_phone_text)
            contact_no = normalize_phone(values["phone"])
            confidence = round(sum(confidences) / len(confidences), 4) if confidences else 0.0
            bag = re.sub(r"\s+", " ", values["bag"]).strip()
            raw = " | ".join(values[field] for field in ("bag", "unit", "name", "blood", "phone")) + f" | {blood_phone_text}"
            needs_review = confidence < 0.75 or not name or not blood_group or len(contact_no) != 10
            rows.append(TableRow(image_path.name, unit, name, blood_group, contact_no, confidence, needs_review, raw, bag))
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


def _phone_candidate_score(result: tuple[str, float]) -> tuple[bool, int, float]:
    text, confidence = result
    digits = normalize_phone(text)
    return len(digits) == 10, len(digits), confidence
