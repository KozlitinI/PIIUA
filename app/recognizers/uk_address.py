# Copyright 2026 Ihor Kozlitin
# SPDX-License-Identifier: Apache-2.0

from typing import List, Optional
from presidio_analyzer import PatternRecognizer, Pattern


class UkAddressRecognizer(PatternRecognizer):
    """
    Recognizer for Ukrainian geographic addresses in legal and mediation texts.
    Examples: м. Київ, вул. Хрещатик, буд. 1, кв. 10; смт Макарів, вулиця Лесі Українки 15; м. Львів, проспект Свободи, 28
    """
    PATTERNS = [
        # Street first address: вул. Університетська, будинок № 13-А, м. Київ, 03110 or вул. Північно-Сирецька, будинок № 1-3, м. Київ, 04136
        Pattern(
            name="uk_address_street_first",
            regex=r"\b(?:вул\.|вулиця|просп\.|проспект|пров\.|провулок|бульв\.|бульвар|площа|пл\.|наб\.|набережна)\s*[А-ЯІЇЄҐ][а-яіїєґ]+(?:-[А-ЯІЇЄҐ][а-яіїєґ]+)*(?:\s+[А-ЯІЇЄҐа-яіїєґ0-9]+)*(?:,\s*(?:буд\.|б\.|будинок)\s*(?:№|N)?\s*\d+(?:-[А-ЯІЇЄҐа-яіїєґA-Za-z]|\s*[-/]\s*\d+[а-яіїєґA-Za-z]?)?)?(?:,\s*(?:м\.|місто|смт|с\.|село)\s*[А-ЯІЇЄҐ][а-яіїєґ]+(?:-[А-ЯІЇЄҐ][а-яіїєґ]+)?)?(?:,\s*(?:кв\.|квартира|кабінет|каб\.|офіс|оф\.|приміщення|прим\.)\s*(?:№|N)?\s*\d+[а-яіїєґA-Za-z]?)?(?:,\s*\d{5})?\b",
            score=0.95,
        ),
        # City first address: м. Київ, вул. Хрещатик, будинок № 10, кв. 5, 01001
        Pattern(
            name="uk_address_city_first",
            regex=r"\b(?:м\.|місто|смт|с\.|село)\s*[А-ЯІЇЄҐ][а-яіїєґ]+(?:-[А-ЯІЇЄҐ][а-яіїєґ]+)*(?:,\s*(?:вул\.|вулиця|просп\.|проспект|пров\.|провулок|бульв\.|бульвар|площа|пл\.|наб\.|набережна)\s*[А-ЯІЇЄҐ][а-яіїєґ]+(?:-[А-ЯІЇЄҐ][а-яіїєґ]+)*(?:\s+[А-ЯІЇЄҐа-яіїєґ0-9]+)*)?(?:,\s*(?:буд\.|б\.|будинок)\s*(?:№|N)?\s*\d+(?:-[А-ЯІЇЄҐа-яіїєґA-Za-z]|\s*[-/]\s*\d+[а-яіїєґA-Za-z]?)?)?(?:,\s*(?:кв\.|квартира|кабінет|каб\.|офіс|оф\.|приміщення|прим\.)\s*(?:№|N)?\s*\d+[а-яіїєґA-Za-z]?)?(?:,\s*\d{5})?\b",
            score=0.95,
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
