from typing import List, Optional
from presidio_analyzer import PatternRecognizer, Pattern


LEGAL_TITLE_WORDS = {
    "позивач", "відповідач", "громадянин", "громадянка", "сторона", "медіатор",
    "представник", "адвокат", "фізична", "особа", "пан", "пані", "гр", "підписант",
    "директор", "менеджер", "заявник", "скаржник", "орендодавець", "орендар",
    "суд", "суддя", "печерський", "районний", "документ", "заяви", "заява"
}


class UkNameRecognizer(PatternRecognizer):
    """
    Recognizer for Ukrainian Full Names (ПІБ: Прізвище, Ім'я, По батькові) and Initials.
    Examples:
    - Шевченко Тарас Григорович
    - Коваленко Ольга Іванівна
    - Іваненко І.І.
    - В.О. Петренко
    """
    PATTERNS = [
        # Full 3-part Ukrainian Name: Capitalized Surname + Capitalized Given Name + Patronymic (-вич, -вна, -івна, -ївна, -евич, -ович)
        Pattern(
            name="uk_name_full_pib",
            regex=r"\b[А-ЯІЇЄҐ][а-яіїєґ]+(?:\s+[А-ЯІЇЄҐ][а-яіїєґ]+)\s+[А-ЯІЇЄҐ][а-яіїєґ]+(?:вич|вна|івна|ївна|евич|ович)\b",
            score=0.98,
        ),
        # Surname with Initials: Іваненко І. В. or Іваненко І.В.
        Pattern(
            name="uk_name_surname_initials",
            regex=r"\b[А-ЯІЇЄҐ][а-яіїєґ]+(?:\s+|-)[А-ЯІЇЄҐ]\.\s?[А-ЯІЇЄҐ]\.\b",
            score=0.92,
        ),
        # Initials before Surname: І. В. Іваненко or І.В. Іваненко
        Pattern(
            name="uk_name_initials_surname",
            regex=r"\b[А-ЯІЇЄҐ]\.\s?[А-ЯІЇЄҐ]\.\s+[А-ЯІЇЄҐ][а-яіїєґ]+\b",
            score=0.92,
        ),
        # 2-word Ukrainian Name (Given Name + Surname or Surname + Given Name)
        Pattern(
            name="uk_name_two_part",
            regex=r"\b[А-ЯІЇЄҐ][а-яіїєґ]+\s+[А-ЯІЇЄҐ][а-яіїєґ]+\b",
            score=0.5,
        ),
    ]

    CONTEXT = [
        "позивач", "відповідач", "громадянин", "громадянка", "сторона", "медіатор",
        "представник", "адвокат", "фізична особа", "пан", "пані", "гр.", "підписант",
        "директор", "менеджер", "заявник", "скаржник", "орендодавець", "орендар"
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
            supported_entity="PERSON",
            patterns=patterns,
            context=context,
            supported_language=supported_language,
        )

    def validate_result(self, pattern_text: str) -> Optional[bool]:
        """
        Validate that the matched text does not start with legal title words (e.g. 'Позивач').
        Return False to invalidate bad matches, None to preserve pattern confidence score.
        """
        words = pattern_text.strip().split()
        if not words:
            return False

        first_word = words[0].lower()
        if first_word in LEGAL_TITLE_WORDS:
            return False

        # Returning None preserves the pattern's score (e.g. 0.98) instead of forcing score to 1.0
        return None
