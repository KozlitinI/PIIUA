# Copyright 2026 Ihor Kozlitin
# SPDX-License-Identifier: Apache-2.0

from typing import List, Optional
from presidio_analyzer import PatternRecognizer, Pattern


class UkMfoRecognizer(PatternRecognizer):
    """
    Recognizer for Ukrainian MFO (МФО / МФО банку) 6-digit codes.
    Examples: МФО 300614, МФО: 300001
    """
    PATTERNS = [
        Pattern(
            name="uk_mfo_6_digits",
            regex=r"\b\d{6}\b",
            score=0.4,
        ),
    ]

    CONTEXT = [
        "мфо", "мфо банку", "код мфо", "код банку", "мфо:"
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
            supported_entity="UK_MFO",
            patterns=patterns,
            context=context,
            supported_language=supported_language,
        )

    def validate_result(self, pattern_text: str) -> Optional[bool]:
        """
        Validate 6-digit MFO candidate.
        """
        clean_text = pattern_text.strip()
        if len(clean_text) == 6 and clean_text.isdigit():
            return True
        return False
