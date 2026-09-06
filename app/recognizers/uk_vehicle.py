from typing import List, Optional
from presidio_analyzer import PatternRecognizer, Pattern


class UkVehicleRecognizer(PatternRecognizer):
    """
    Recognizer for Ukrainian vehicle plates (AA 1234 BK, KA1234CB) and 17-digit VIN numbers.
    """
    PATTERNS = [
        # Ukrainian vehicle license plate: 2 Cyrillic letters + 4 digits + 2 Cyrillic letters
        Pattern(
            name="uk_license_plate",
            regex=r"\b[А-ЯІЇЄҐA-Z]{2}\s?\d{4}\s?[А-ЯІЇЄҐA-Z]{2}\b",
            score=0.75,
        ),
        # Vehicle Identification Number (VIN): 17 alphanumerics (excluding I, O, Q)
        Pattern(
            name="uk_vin_code",
            regex=r"\b[A-HJ-NPR-Z0-9]{17}\b",
            score=0.85,
        ),
    ]

    CONTEXT = [
        "автомобіль", "авто", "транспортний засіб", "днз", "номерний знак",
        "vin", "кузов", "шасі", "марка", "модель", "техпаспорт"
    ]

    def __init__(
        self,
        patterns: Optional[List[Pattern]] = None,
        context: Optional[List[str]] = None,
        supported_language: str = "uk",
    ):
        patterns = patterns if patterns else self.PATTERNS
        context = context if context else self.CONTEXT
        super().__init__(
            supported_entity="UK_VEHICLE",
            patterns=patterns,
            context=context,
            supported_language=supported_language,
        )
