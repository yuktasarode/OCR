from pathlib import Path

import pytest

from table_ocr.extract import extract_images


class FakeExtractor:
    def extract(self, image_path):
        return [image_path.name]


def test_extract_images_combines_multiple_sources(tmp_path):
    first = tmp_path / "one.jpg"
    second = tmp_path / "two.png"
    first.write_bytes(b"image")
    second.write_bytes(b"image")

    assert extract_images([first, second], FakeExtractor()) == ["one.jpg", "two.png"]


def test_extract_images_rejects_missing_file():
    with pytest.raises(FileNotFoundError, match="Image not found"):
        extract_images([Path("missing.jpg")], FakeExtractor())


def test_extract_images_rejects_empty_input():
    with pytest.raises(ValueError, match="At least one image"):
        extract_images([], FakeExtractor())
