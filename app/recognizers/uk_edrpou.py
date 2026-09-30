# Copyright 2026 Ihor Kozlitin
# SPDX-License-Identifier: Apache-2.0

from typing import List, Optional
from presidio_analyzer import PatternRecognizer, Pattern


def validate_edrpou_checksum(edrpou_str: str) -> bool:
    """
    Validates Ukrainian 8-digit EDRPOU (ЄДРПОУ) legal entity code checksum.
    """
    if len(edrpou_str) != 8 or not edrpou_str.isdigit():
        return False
    
    digits = [int(d) for d in edrpou_str]
    val = int(edrpou_str)
    
    w1 = [1, 2, 3, 4, 5, 6, 7]
    w2 = [3, 4, 5, 6, 7, 8, 9]

    if val > 30000000 and val < 60000000:
        w1 = [7, 1, 2, 3, 4, 5, 6]
        w2 = [9, 3, 4, 5, 6, 7, 8]

    total = sum(digits[i] * w1[i] for i in range(7))
    remainder = total % 11

    if remainder > 10:
        total = sum(digits[i] * w2[i] for i in range(7))
        remainder = total % 11

    if remainder < 10:
        return digits[7] == remainder
    else:
        return digits[7] == 0


class UkEdrpouRecognizer(PatternRecognizer):
    """
    Recognizer for Ukrainian EDRPOU (ЄДРПОУ / ЄГРПОУ) 8-digit codes.
    Recognizes standalone 8-digit numbers with context or preceded by 'ЄДРПОУ'.
    """
    PATTERNS = [
        Pattern(
            name="uk_edrpou_8_digits",
            regex=r"\b\d{8}\b",
            score=0.5,
        ),
    ]

    CONTEXT = [
        "єдрпоу", "код єдрпоу", "код за єдрпоу", "єгрпоу", "код єгрпоу"
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
            supported_entity="UK_EDRPOU",
            patterns=patterns,
            context=context,
            supported_language=supported_language,
        )

    def validate_result(self, pattern_text: str) -> Optional[bool]:
        """
        Validate 8-digit EDRPOU candidate checksum.
        """
        clean_text = pattern_text.strip()
        if len(clean_text) == 8 and clean_text.isdigit():
            if validate_edrpou_checksum(clean_text):
                return True
            return False
        return False
