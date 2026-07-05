from table_ocr.normalize import normalize_blood_group, normalize_name, normalize_phone, normalize_unit


def test_normalize_unit_repairs_common_ocr_characters():
    assert normalize_unit("B-213)") == "B-2131"
    assert normalize_unit("3-2133") == "B-2133"


def test_normalize_phone_keeps_digits_and_repairs_digit_like_text():
    assert normalize_phone("98I93 40l17") == "9819340117"


def test_normalize_blood_group_returns_canonical_value():
    assert normalize_blood_group("B Pos") == "B+"
    assert normalize_blood_group("o neg") == "O-"


def test_normalize_name_removes_recognizer_punctuation_at_edges():
    assert normalize_name("' Vinod K. Pandule.") == "Vinod K. Pandule"
