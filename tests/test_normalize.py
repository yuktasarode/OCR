from table_ocr.normalize import normalize_blood_group, normalize_name, normalize_phone, normalize_unit, resolve_blood_group


def test_normalize_unit_repairs_common_ocr_characters():
    assert normalize_unit("B-213)") == "B-2131"
    assert normalize_unit("3-2133") == "B-2133"


def test_normalize_phone_keeps_digits_and_repairs_digit_like_text():
    assert normalize_phone("98I93 40l17") == "9819340117"


def test_normalize_blood_group_returns_canonical_value():
    assert normalize_blood_group("B Pos") == "B+"
    assert normalize_blood_group("o neg") == "O-"
    assert normalize_blood_group("AB-ve") == "AB-"
    assert normalize_blood_group("0 positive") == "O+"
    assert normalize_blood_group("A+") == "A+"


def test_normalize_blood_group_rejects_unrelated_words():
    assert normalize_blood_group("Manojkumar") == ""
    assert normalize_blood_group("blood") == ""
    assert normalize_blood_group("positive") == ""


def test_resolve_blood_group_uses_polarity_and_wider_row_fallback():
    assert resolve_blood_group("", "BPos 8369637681") == "B+"
    assert resolve_blood_group("Pos", "") == "O+"
    assert resolve_blood_group("", "BPCA 932018") == "B+"


def test_normalize_name_removes_recognizer_punctuation_at_edges():
    assert normalize_name("' Vinod K. Pandule.") == "Vinod K. Pandule"
