from typing import List, Optional
from presidio_analyzer import PatternRecognizer, Pattern


class UkIbanRecognizer(PatternRecognizer):
    """
    Recognizer for Ukrainian IBAN bank accounts (UA + 27 digits = 29 characters).
    Example: UA123456789012345678901234567 or formatted UA12 3456 7890 1234 5678 9012 3456 7
    """
    PATTERNS = [
        # Standard contiguous IBAN
        Pattern(
            name="uk_iban_contiguous",
            regex=r"\bUA\d{27}\b",
            score=0.95,
        ),
        # Space-separated IBAN
        Pattern(
            name="uk_iban_spaced",
            regex=r"\bUA\d{2}(?:\s?\d{4}){6}\s?\d{1}\b",
            score=0.85,
        ),
    ]

    CONTEXT = [
        "iban", "рахунок", "банк", "р/р", "поточний рахунок",
        "картка", "реквізити", "приватбанк", "монобанк", "ощадбанк", "банківський"
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
            supported_entity="UK_IBAN",
            patterns=patterns,
            context=context,
            supported_language=supported_language,
        )
