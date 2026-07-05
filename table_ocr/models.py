from dataclasses import asdict, dataclass


@dataclass(slots=True)
class TableRow:
    source_image: str
    unit_no: str
    donor_name: str
    blood_group: str
    contact_no: str
    confidence: float
    needs_review: bool
    raw_ocr: str
    bag: str = ""

    def to_dict(self) -> dict[str, object]:
        return asdict(self)
