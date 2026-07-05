from table_ocr.evaluate import evaluate_rows
from table_ocr.models import TableRow


def row(unit, name, blood, phone):
    return TableRow("sample.jpg", unit, name, blood, phone, 0.8, False, "")


def test_evaluate_rows_reports_exact_and_character_accuracy():
    expected = [row("B-1", "Leena Desai", "A+", "8369476756")]
    predicted = [row("B-1", "Leena Pesai", "A+", "8369476956")]

    report = evaluate_rows(expected, predicted)

    assert report["matched_rows"] == 1
    assert report["fields"]["blood_group"]["exact_accuracy"] == 1.0
    assert report["fields"]["donor_name"]["exact_accuracy"] == 0.0
    assert 0.8 < report["fields"]["donor_name"]["character_accuracy"] < 1.0
    assert report["overall_exact_field_accuracy"] == 0.5


def test_evaluate_rows_excludes_blank_ground_truth_fields():
    expected = [row("B-1", "Naresh", "", "")]
    predicted = [row("B-1", "Naresh", "O+", "123")]

    report = evaluate_rows(expected, predicted)

    assert report["evaluated_fields"] == 2
    assert report["overall_exact_field_accuracy"] == 1.0
