import numpy as np

from table_ocr.recognizers import RapidRecognizer


class FakeRapidEngine:
    def __call__(self, image):
        return [
            ([[50, 0], [90, 0], [90, 20], [50, 20]], "Desai", 0.8),
            ([[0, 0], [40, 0], [40, 20], [0, 20]], "Leena", 0.9),
        ], None


def test_rapid_recognizer_orders_fragments_left_to_right():
    text, confidence = RapidRecognizer(FakeRapidEngine()).recognize(np.zeros((20, 100, 3), dtype=np.uint8))

    assert text == "Leena Desai"
    assert confidence == 0.85
