import re


def normalize_unit(value: str) -> str:
    compact = re.sub(r"\s+", "", value.upper())
    compact = compact.replace(")", "1").replace("I", "1").replace("L", "1")
    compact = re.sub(r"^[38](?=-)", "B", compact)
    match = re.search(r"B[-_]?([0-9]{3,5})", compact)
    return f"B-{match.group(1)}" if match else ""


def normalize_phone(value: str) -> str:
    translation = str.maketrans({"O": "0", "o": "0", "I": "1", "i": "1", "l": "1", "|": "1"})
    digits = re.sub(r"\D", "", value.translate(translation))
    if len(digits) > 10:
        digits = digits[-10:]
    return digits


def normalize_blood_group(value: str) -> str:
    compact = re.sub(r"[^A-Z0-9+-]", "", value.upper())
    compact = compact.replace("0", "O")
    group_match = re.search(r"(AB|A|B|O)", compact)
    if not group_match:
        return ""
    suffix = "-" if "NEG" in compact or compact.endswith("-") else "+"
    return f"{group_match.group(1)}{suffix}"


def normalize_name(value: str) -> str:
    value = re.sub(r"[^A-Za-z. '\-]", " ", value)
    value = re.sub(r"\s+", " ", value).strip(" .-")
    return value.title()
