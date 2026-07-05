import cv2
import numpy as np

from table_ocr.preprocess import preprocess_cell


def test_name_preprocessing_removes_long_table_lines_and_adds_padding():
    cell = np.full((40, 120, 3), 255, dtype=np.uint8)
    cv2.line(cell, (0, 2), (119, 2), (0, 0, 0), 2)
    cv2.line(cell, (0, 37), (119, 37), (0, 0, 0), 2)
    cv2.putText(cell, "Name", (20, 27), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 0), 1)

    processed = preprocess_cell(cell, "name")

    assert processed.shape[0] > cell.shape[0]
    assert processed.shape[1] > cell.shape[1]
    assert np.mean(processed[2]) > 240
    assert np.min(processed) < 100


def test_phone_preprocessing_returns_high_contrast_rgb_image():
    cell = np.full((30, 100, 3), 210, dtype=np.uint8)
    cv2.putText(cell, "9876", (5, 23), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (40, 40, 40), 2)

    processed = preprocess_cell(cell, "phone")

    assert processed.ndim == 3
    assert processed.shape[2] == 3
    assert processed.max() == 255
    assert processed.min() == 0
