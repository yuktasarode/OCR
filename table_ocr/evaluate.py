from collections import defaultdict

from table_ocr.models import TableRow


FIELDS = ("unit_no", "donor_name", "blood_group", "contact_no")


def _comparison_text(value: str) -> str:
    return "".join(character.lower() for character in value if character.isalnum())


def _levenshtein(left: str, right: str) -> int:
    previous = list(range(len(right) + 1))
    for left_index, left_character in enumerate(left, start=1):
        current = [left_index]
        for right_index, right_character in enumerate(right, start=1):
            current.append(
                min(
                    current[-1] + 1,
                    previous[right_index] + 1,
                    previous[right_index - 1] + (left_character != right_character),
                )
            )
        previous = current
    return previous[-1]


def evaluate_rows(expected: list[TableRow], predicted: list[TableRow]) -> dict[str, object]:
    predicted_by_unit = {row.unit_no: row for row in predicted if row.unit_no}
    stats = defaultdict(lambda: {"evaluated": 0, "exact": 0, "characters": 0, "distance": 0})
    matched_rows = 0

    for expected_row in expected:
        predicted_row = predicted_by_unit.get(expected_row.unit_no)
        if predicted_row is None:
            continue
        matched_rows += 1
        for field in FIELDS:
            expected_value = getattr(expected_row, field)
            if not expected_value:
                continue
            predicted_value = getattr(predicted_row, field)
            expected_text = _comparison_text(expected_value)
            predicted_text = _comparison_text(predicted_value)
            denominator = max(len(expected_text), len(predicted_text), 1)
            field_stats = stats[field]
            field_stats["evaluated"] += 1
            field_stats["exact"] += expected_text == predicted_text
            field_stats["characters"] += denominator
            field_stats["distance"] += _levenshtein(expected_text, predicted_text)

    field_report = {}
    total_evaluated = total_exact = total_characters = total_distance = 0
    for field in FIELDS:
        field_stats = stats[field]
        evaluated = field_stats["evaluated"]
        characters = field_stats["characters"]
        field_report[field] = {
            "evaluated": evaluated,
            "exact_accuracy": round(field_stats["exact"] / evaluated, 4) if evaluated else None,
            "character_accuracy": round(max(0, 1 - field_stats["distance"] / characters), 4) if characters else None,
        }
        total_evaluated += evaluated
        total_exact += field_stats["exact"]
        total_characters += characters
        total_distance += field_stats["distance"]

    return {
        "expected_rows": len(expected),
        "predicted_rows": len(predicted),
        "matched_rows": matched_rows,
        "evaluated_fields": total_evaluated,
        "overall_exact_field_accuracy": round(total_exact / total_evaluated, 4) if total_evaluated else None,
        "overall_character_accuracy": round(max(0, 1 - total_distance / total_characters), 4) if total_characters else None,
        "fields": field_report,
    }
