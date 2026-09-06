from typing import Dict, List, Tuple
from presidio_anonymizer import AnonymizerEngine
from presidio_analyzer import RecognizerResult

from app.core.analyzer import analyze_text
from app.core.mapper import pseudonymize_text_with_mapping, restore_text_from_mapping
from app.schemas.api import DetectedEntity


def process_pseudonymization(
    text: str,
    score_threshold: float = 0.4,
    language: str = "uk"
) -> Tuple[str, Dict[str, str], List[DetectedEntity]]:
    """
    Analyzes text and applies reversible structured token pseudonymization.
    """
    raw_results = analyze_text(text=text, score_threshold=score_threshold, language=language)
    pseudo_text, mapping, entities = pseudonymize_text_with_mapping(text, raw_results)
    return pseudo_text, mapping, entities


def process_restoration(
    pseudonymized_text: str,
    mapping: Dict[str, str]
) -> str:
    """
    Restores original PII into the pseudonymized text using mapping.
    """
    return restore_text_from_mapping(pseudonymized_text, mapping)
