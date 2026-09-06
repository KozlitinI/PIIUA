from typing import List, Optional
from presidio_analyzer import PatternRecognizer, Pattern


class UkPassportRecognizer(PatternRecognizer):
    """
    Recognizer for Ukrainian Passport (paper series + number) and ID-cards (9 digits).
    Examples: КМ 123456, АА123456, ID-картка № 001234567, запис № 19900101-00123
    """
    PATTERNS = [
        # Paper passport: 2 Cyrillic uppercase letters + optional space + 6 digits
        Pattern(
            name="uk_passport_paper",
            regex=r"\b[А-ЯІЇЄҐ]{2}\s?\d{6}\b",
            score=0.85,
        ),
        # ID-card 9 digits with explicit prefix or standalone when context present
        Pattern(
            name="uk_passport_id_card",
            regex=r"\b\d{9}\b",
            score=0.45,
        ),
        # Record number (Номер запису у Дdemграфічному реєстрі): YYYYMMDD-XXXXX (13 chars)
        Pattern(
            name="uk_demographic_record",
            regex=r"\b\d{8}-\d{5}\b",
            score=0.9,
        ),
    ]

    CONTEXT = [
        "паспорт", "паспорта", "паспорту", "id-картка", "айді",
        "паспорт громадянина", "серія", "номер документа",
        "виданий", "орган", "запис", "демографічний реєстр"
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
            supported_entity="UK_PASSPORT",
            patterns=patterns,
            context=context,
            supported_language=supported_language,
        )
