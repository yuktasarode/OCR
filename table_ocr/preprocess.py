import cv2
import numpy as np


def _remove_table_lines(binary: np.ndarray) -> np.ndarray:
    height, width = binary.shape
    horizontal_kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (max(20, width // 3), 1))
    vertical_kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (1, max(15, height // 2)))
    horizontal = cv2.morphologyEx(255 - binary, cv2.MORPH_OPEN, horizontal_kernel)
    vertical = cv2.morphologyEx(255 - binary, cv2.MORPH_OPEN, vertical_kernel)
    cleaned = binary.copy()
    cleaned[(horizontal > 0) | (vertical > 0)] = 255
    return cleaned


def preprocess_cell(cell: np.ndarray, field: str) -> np.ndarray:
    gray = cv2.cvtColor(cell, cv2.COLOR_BGR2GRAY) if cell.ndim == 3 else cell.copy()
    gray = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8)).apply(gray)
    binary = cv2.adaptiveThreshold(
        gray,
        255,
        cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
        cv2.THRESH_BINARY,
        31,
        15,
    )
    binary = _remove_table_lines(binary)
    if field == "phone":
        binary = cv2.morphologyEx(binary, cv2.MORPH_CLOSE, np.ones((2, 2), dtype=np.uint8))
    padded = cv2.copyMakeBorder(binary, 10, 10, 10, 10, cv2.BORDER_CONSTANT, value=255)
    scale = 2 if field == "name" else 3
    resized = cv2.resize(padded, None, fx=scale, fy=scale, interpolation=cv2.INTER_CUBIC)
    return cv2.cvtColor(resized, cv2.COLOR_GRAY2RGB)
