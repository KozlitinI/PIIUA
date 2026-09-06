from typing import List, Optional
from presidio_analyzer import PatternRecognizer, Pattern


class UkCaseNumberRecognizer(PatternRecognizer):
    """
    Recognizer for Ukrainian court case identifiers and proceeding numbers.
    Examples: справа № 757/12345/23-ц, провадження № 1-кс/757/100/23, справа N 123/4567/22, № 757/12345/23-ц
    """
    PATTERNS = [
        # Full explicit court case pattern: 757/12345/23-ц or 2-a/123/45/22
        Pattern(
            name="uk_case_number_explicit",
            regex=r"\b(?:справ[аи]|провадження)\s*(?:№|N)?\s*(?:\d+-[а-яяіїєґ]+/)?\d{3,4}/\d{1,6}/\d{2,4}(?:-[а-яяіїєґ]+)?\b",
            score=0.95,
        ),
        # Standalone case index format (e.g. 757/12345/23-ц)
        Pattern(
            name="uk_case_number_format",
            regex=r"\b\d{3,4}/\d{1,6}/\d{2,4}(?:-[а-яяіїєґ]+)?\b",
            score=0.75,
        ),
    ]

    CONTEXT = [
        "справа", "справи", "провадження", "суд", "судовий", "ухвала",
        "рішення", "позов", "позивач", "відповідач", "районний суд"
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
            supported_entity="UK_CASE_NUMBER",
            patterns=patterns,
            context=context,
            supported_language=supported_language,
        )
