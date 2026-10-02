# Copyright 2026 Ihor Kozlitin
# SPDX-License-Identifier: Apache-2.0

from typing import List, Optional
from presidio_analyzer import PatternRecognizer, Pattern


class UkUrlRecognizer(PatternRecognizer):
    """
    Recognizer for web URLs and internet addresses.
    Examples: http://its.1c.ua/, https://portal.1c.eu/, http://its.bas-soft.eu, https://dl.bas-soft.eu/, www.example.com
    """
    PATTERNS = [
        # Full URLs with protocol (http, https, ftp, ftps) or www prefix
        Pattern(
            name="url_protocol",
            regex=r"(?i)\b(?:https?://|ftps?://|www\.)[^\s()<>]+(?:\([\w\d]+\)|[^\s`!()\[\]{};:\'\".,<>?«»“”])",
            score=0.95,
        ),
        # Domain names with paths or common TLDs without explicit protocol
        Pattern(
            name="url_domain",
            regex=r"(?i)\b(?:[a-z0-9](?:[a-z0-9-]{0,61}[a-z0-9])?\.)+(?:ua|eu|com|org|net|group|gov|edu|uk|io|biz|info|site|online)\b(?:/[^\s()<>]+(?:\([\w\d]+\)|[^\s`!()\[\]{};:\'\".,<>?«»“”]))?",
            score=0.7,
        ),
    ]

    def __init__(
        self,
        patterns: Optional[List[Pattern]] = None,
        context: Optional[List[str]] = None,
        supported_language: str = "uk",
    ):
        patterns = patterns if patterns else self.PATTERNS
        super().__init__(
            supported_entity="URL",
            patterns=patterns,
            context=context,
            supported_language=supported_language,
        )
