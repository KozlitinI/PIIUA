from typing import List, Optional
from presidio_analyzer import PatternRecognizer, Pattern


class UkPhoneRecognizer(PatternRecognizer):
    """
    Recognizer for Ukrainian phone numbers (mobile and landlines).
    Examples: +380501234567, 067-123-45-67, (044) 200-11-22, 093 123 45 67, +38 (050) 123 45 67
    """
    PATTERNS = [
        # Full international format with optional + prefix
        Pattern(
            name="uk_phone_intl",
            regex=r"(?:(?<=\s)|(?<=^)|(?<=\())?\+?38[\s\.-]?\(?0\d{2}\)?[\s\.-]?\d{3}[\s\.-]?\d{2}[\s\.-]?\d{2}\b",
            score=0.85,
        ),
        # Local 10-digit format: 0501234567 or (044) 200-11-22
        Pattern(
            name="uk_phone_local",
            regex=r"\b\(?0\d{2}\)?[\s\.-]?\d{3}[\s\.-]?\d{2}[\s\.-]?\d{2}\b",
            score=0.6,
        ),
    ]

    CONTEXT = [
        "телефон", "тел", "мобільний", "вайбер", "viber", "telegram",
        "телефону", "дзвінок", "контакт", "зв'язок", "номер"
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
            supported_entity="UK_PHONE",
            patterns=patterns,
            context=context,
            supported_language=supported_language,
        )
