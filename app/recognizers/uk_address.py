from typing import List, Optional
from presidio_analyzer import PatternRecognizer, Pattern


class UkAddressRecognizer(PatternRecognizer):
    """
    Recognizer for Ukrainian geographic addresses in legal and mediation texts.
    Examples: м. Київ, вул. Хрещатик, буд. 1, кв. 10; смт Макарів, вулиця Лесі Українки 15; м. Львів, проспект Свободи, 28
    """
    PATTERNS = [
        # Full address chain: (м.|смт|с.) City, (вул.|просп.|пров.|бульв.) Street, (буд.|б.) House, (кв.) Apt
        Pattern(
            name="uk_address_full",
            regex=r"\b(?:м\.|смт|с\.)\s*[А-ЯІЇЄҐ][а-яіїєґ]+(?:-[А-ЯІЇЄҐ][а-яіїєґ]+)?(?:,\s*(?:вул\.|вулиця|просп\.|проспект|пров\.|провулок|бульв\.|бульвар|площа|пл\.)\s*[А-ЯІЇЄҐа-яіїєґ0-9\s\.\-]+)?(?:,\s*(?:буд\.|б\.)\s*\d+[а-яіїєґ]?)?(?:,\s*(?:кв\.|кабінет)\s*\d+)?\b",
            score=0.9,
        ),
        # Street level address: вул. Хрещатик, буд. 10
        Pattern(
            name="uk_address_street",
            regex=r"\b(?:вул\.|вулиця|просп\.|проспект|пров\.|провулок|бульвар|бульв\.)\s*[А-ЯІЇЄҐ][а-яіїєґ]+(?:\s+[А-ЯІЇЄҐа-яіїєґ]+)*(?:,\s*(?:буд\.|б\.|будинок)\s*\d+[а-яіїєґ]?)?(?:,\s*(?:кв\.|кфіра|кв)\s*\d+)?\b",
            score=0.8,
        ),
    ]

    CONTEXT = [
        "адреса", "мешкає", "проживає", "зареєстрований", "місце проживання",
        "місцезнаходження", "вулиця", "вул", "будинок", "квартира", "область", "район"
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
            supported_entity="UK_ADDRESS",
            patterns=patterns,
            context=context,
            supported_language=supported_language,
        )
