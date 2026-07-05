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
    compact = re.sub(r"[^A-Z0-9+-]", "", value.upper()).replace("0", "O")
    match = re.fullmatch(r"(AB|A|B|O)(.*)", compact)
    if not match:
        return ""
    group, polarity = match.groups()
    negative_tokens = {"-", "N", "NE", "NEG", "NEGATIVE", "VE", "-VE"}
    positive_tokens = {"", "+", "P", "PO", "POS", "POSITIVE", "PE", "PC", "PES", "A"}
    if polarity in negative_tokens:
        return f"{group}-"
    if polarity in positive_tokens or re.fullmatch(r"P[A-Z]{0,2}", polarity):
        return f"{group}+"
    return ""


def resolve_blood_group(cell_text: str, row_text: str = "") -> str:
    cell_group = normalize_blood_group(cell_text)
    if cell_group:
        return cell_group
    compact_cell = re.sub(r"[^A-Z]", "", cell_text.upper())
    if compact_cell in {"P", "PO", "POS", "POSITIVE"}:
        return "O+"
    for token in re.findall(r"[A-Za-z0-9+-]+", row_text):
        group = normalize_blood_group(token)
        if group:
            return group
    return ""


def normalize_name(value: str) -> str:
    value = re.sub(r"[^A-Za-z. '\-]", " ", value)
    value = re.sub(r"\s+", " ", value).strip(" .-'")
    return value.title()
