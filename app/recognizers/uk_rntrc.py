# Copyright 2026 Ihor Kozlitin
# SPDX-License-Identifier: Apache-2.0

from typing import List, Optional
from presidio_analyzer import PatternRecognizer, Pattern, RecognizerResult


def validate_rntrc_checksum(rntrc_str: str) -> bool:
    """
    Validates Ukrainian 10-digit RNTRC (РНОКПП/ІПН) checksum algorithm.
    """
    if len(rntrc_str) != 10 or not rntrc_str.isdigit():
        return False
    
    digits = [int(d) for d in rntrc_str]
    weights = [-1, 5, 7, 9, 4, 6, 10, 5, 7]
    
    total = sum(digits[i] * weights[i] for i in range(9))
    checksum = total % 11
    if checksum == 10:
        checksum = checksum % 10
        
    return digits[9] == checksum


class UkRntrcRecognizer(PatternRecognizer):
    """
    Recognizer for Ukrainian RNTRC (РНОКПП / ІПН) tax numbers (10 digits for individuals, 12 digits for VAT/legal entities).
    Includes checksum validation logic and context matching.
    """
    PATTERNS = [
        # 10-digit РНОКПП/ІПН
        Pattern(
            name="rntrc_10_digits",
            regex=r"\b\d{10}\b",
            score=0.5,
        ),
        # 12-digit ІПН (платника ПДВ / юридичної особи / ФОП)
        Pattern(
            name="rntrc_12_digits",
            regex=r"\b\d{12}\b",
            score=0.5,
        ),
    ]

    CONTEXT = [
        "рнокопп", "іпн", "податковий", "ідентифікаційний",
        "код", "рнокпп", "картка платника", "платник податків", "іпн платника пдв"
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
            supported_entity="UK_RNTRC",
            patterns=patterns,
            context=context,
            supported_language=supported_language,
        )

    def validate_result(self, pattern_text: str) -> Optional[bool]:
        """
        Validate candidate 10-digit RNTRC checksum or 12-digit IPN format.
        """
        clean_text = pattern_text.strip()
        if len(clean_text) == 10 and clean_text.isdigit():
            if validate_rntrc_checksum(clean_text):
                return True
            return False
        if len(clean_text) == 12 and clean_text.isdigit():
            return True
        return False
