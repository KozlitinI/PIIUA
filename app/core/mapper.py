import re
from typing import Dict, List, Optional, Tuple
import pymorphy3
from presidio_analyzer import RecognizerResult
from app.schemas.api import DetectedEntity

_morph_analyzer: Optional[pymorphy3.MorphAnalyzer] = None


def get_morph_analyzer() -> pymorphy3.MorphAnalyzer:
    global _morph_analyzer
    if _morph_analyzer is None:
        _morph_analyzer = pymorphy3.MorphAnalyzer(lang='uk')
    return _morph_analyzer


def normalize_uk_person_name(raw_name: str) -> str:
    """
    Normalizes Ukrainian person names from any grammatical case to base nominative case (називний відмінок).
    Examples:
      - 'Андрія Мельника' -> 'Андрій Мельник'
      - 'Андрієм Мельником' -> 'Андрій Мельник'
      - 'Шевченка Тараса Григоровича' -> 'Шевченко Тарас Григорович'
    """
    clean = raw_name.strip()
    if not clean:
        return clean

    morph = get_morph_analyzer()
    words = clean.split()
    norm_words = []

    for w in words:
        # Preserve initials like І., І.В., В.
        if re.match(r'^[А-ЯІЇЄҐ]\.?(?:[А-ЯІЇЄҐ]\.?)?$', w, re.IGNORECASE):
            norm_words.append(w.upper())
            continue

        # Handle hyphenated names like Гулака-Артемовського
        if '-' in w:
            parts = w.split('-')
            norm_parts = []
            for p in parts:
                parses = morph.parse(p)
                lemma = parses[0].normal_form if parses else p
                norm_parts.append(lemma.capitalize())
            norm_words.append('-'.join(norm_parts))
            continue

        parses = morph.parse(w)
        lemma = parses[0].normal_form if parses else w
        norm_words.append(lemma.capitalize())

    return ' '.join(norm_words)


ENTITY_TAG_PREFIXES = {
    "PERSON": "PERSON",
    "ORGANIZATION": "ORG",
    "ORG": "ORG",
    "UK_RNTRC": "RNTRC",
    "UK_PASSPORT": "PASSPORT",
    "UK_IBAN": "IBAN",
    "UK_PHONE": "PHONE",
    "UK_CASE_NUMBER": "CASE_NUM",
    "UK_ADDRESS": "ADDRESS",
    "UK_VEHICLE": "VEHICLE",
    "EMAIL_ADDRESS": "EMAIL",
}


def resolve_overlapping_entities(results: List[RecognizerResult]) -> List[RecognizerResult]:
    """
    Filters out overlapping entity spans, prioritizing higher scores and longer spans.
    """
    if not results:
        return []

    # Primary sort by score descending, secondary by span length descending, tertiary by start index ascending
    sorted_by_priority = sorted(
        results,
        key=lambda r: (-r.score, -(r.end - r.start), r.start)
    )

    filtered: List[RecognizerResult] = []
    for current in sorted_by_priority:
        overlap = False
        for kept in filtered:
            # Check if current overlaps with kept
            if not (current.end <= kept.start or current.start >= kept.end):
                overlap = True
                break
        if not overlap:
            filtered.append(current)

    # Final sort strictly by start character index ascending
    return sorted(filtered, key=lambda r: r.start)


class TokenMapper:
    """
    Manages consistent token assignment and reversible mapping for PII de-identification.
    """

    def __init__(self):
        self.entity_counts: Dict[str, int] = {}
        self.value_to_token: Dict[str, str] = {}
        self.token_to_value: Dict[str, str] = {}

    def get_or_create_token(self, entity_type: str, raw_value: str) -> str:
        clean_value = raw_value.strip()

        # Person name lemmatization/normalization to base nominative form
        if entity_type == "PERSON":
            normalized_name = normalize_uk_person_name(clean_value)
            lookup_key = f"PERSON::{normalized_name.lower()}"

            if lookup_key in self.value_to_token:
                token = self.value_to_token[lookup_key]
                # Ensure mapping dictionary holds the normalized base name
                self.token_to_value[token] = normalized_name
                return token

            prefix = ENTITY_TAG_PREFIXES.get(entity_type, entity_type.upper())
            count = self.entity_counts.get(prefix, 0) + 1
            self.entity_counts[prefix] = count

            token = f"<{prefix}_{count}>"
            self.value_to_token[lookup_key] = token
            self.token_to_value[token] = normalized_name
            return token
        
        # Core key normalization for organizations to unify variants (e.g. ТОВ «Альфа-Трейд» vs «Альфа-Трейд»)
        elif entity_type in ("ORGANIZATION", "ORG"):
            core_name = re.sub(r"^(?:ТОВ|ТзОВ|ПП|ПрАТ|ПАТ|АТ|ДП|ГО|ОСББ|БФ|ФОП)\s*", "", clean_value)
            core_name = core_name.strip(" \"«'“»'”").lower()
            lookup_key = f"ORGANIZATION::{core_name}"
            
            if lookup_key in self.value_to_token:
                token = self.value_to_token[lookup_key]
                # Upgrade mapping value to fuller form if current clean_value is longer (e.g., contains ТОВ prefix)
                if len(clean_value) > len(self.token_to_value[token]):
                    self.token_to_value[token] = clean_value
                return token
        else:
            lookup_key = f"{entity_type}::{clean_value.lower()}"
            if lookup_key in self.value_to_token:
                return self.value_to_token[lookup_key]

        prefix = ENTITY_TAG_PREFIXES.get(entity_type, entity_type.upper())
        count = self.entity_counts.get(prefix, 0) + 1
        self.entity_counts[prefix] = count

        token = f"<{prefix}_{count}>"
        self.value_to_token[lookup_key] = token
        self.token_to_value[token] = clean_value
        return token


def pseudonymize_text_with_mapping(
    text: str,
    results: List[RecognizerResult]
) -> Tuple[str, Dict[str, str], List[DetectedEntity]]:
    """
    Pseudonymizes text using Presidio analyzer results, returning:
    1. Pseudonymized text with tags (<PERSON_1>, <PHONE_1>, etc.)
    2. Token mapping dictionary (token -> original value)
    3. List of DetectedEntity objects
    """
    filtered_results = resolve_overlapping_entities(results)
    mapper = TokenMapper()
    detected_entities: List[DetectedEntity] = []

    chars = list(text)
    
    # Collect entities info first
    for res in filtered_results:
        raw_val = text[res.start:res.end]
        detected_entities.append(
            DetectedEntity(
                entity_type=res.entity_type,
                start=res.start,
                end=res.end,
                score=round(res.score, 2),
                text=raw_val,
            )
        )

    # Replace from back to front
    for res in sorted(filtered_results, key=lambda r: r.start, reverse=True):
        raw_val = text[res.start:res.end]
        token = mapper.get_or_create_token(res.entity_type, raw_val)
        chars[res.start:res.end] = list(token)

    pseudonymized_text = "".join(chars)
    return pseudonymized_text, mapper.token_to_value, detected_entities


def restore_text_from_mapping(
    pseudonymized_text: str,
    mapping: Dict[str, str]
) -> str:
    """
    Restores original PII values in pseudonymized text using the mapping dictionary.
    Handles tags with or without angle brackets.
    """
    if not pseudonymized_text or not mapping:
        return pseudonymized_text

    result_text = pseudonymized_text

    # Sort mapping keys by length descending to avoid partial tag replacements
    sorted_items = sorted(mapping.items(), key=lambda item: len(item[0]), reverse=True)

    for token, orig_value in sorted_items:
        # Standard token with brackets, e.g. <PERSON_1>
        if token in result_text:
            result_text = result_text.replace(token, orig_value)

        # Unbracketed token variant if LLM stripped brackets, e.g. PERSON_1
        bare_token = token.strip("<>")
        if bare_token in result_text and token not in result_text:
            result_text = result_text.replace(bare_token, orig_value)

    return result_text
