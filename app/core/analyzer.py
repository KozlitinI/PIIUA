import logging
from typing import List, Optional
from presidio_analyzer import (
    AnalyzerEngine,
    RecognizerRegistry,
    RecognizerResult,
    PatternRecognizer,
    Pattern,
)
from presidio_analyzer.nlp_engine import NlpEngineProvider

from app.recognizers.uk_rntrc import UkRntrcRecognizer
from app.recognizers.uk_passport import UkPassportRecognizer
from app.recognizers.uk_iban import UkIbanRecognizer
from app.recognizers.uk_phone import UkPhoneRecognizer
from app.recognizers.uk_case_number import UkCaseNumberRecognizer
from app.recognizers.uk_address import UkAddressRecognizer
from app.recognizers.uk_vehicle import UkVehicleRecognizer
from app.recognizers.uk_names import UkNameRecognizer

logger = logging.getLogger("piiua.analyzer")

# Email recognizer for Ukrainian/English
UK_EMAIL_RECOGNIZER = PatternRecognizer(
    supported_entity="EMAIL_ADDRESS",
    patterns=[
        Pattern(
            name="email",
            regex=r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b",
            score=1.0,
        )
    ],
    supported_language="uk",
)


def create_uk_analyzer_engine() -> AnalyzerEngine:
    """
    Creates and configures Presidio AnalyzerEngine with Ukrainian recognizers.
    """
    registry = RecognizerRegistry(supported_languages=["uk", "en"])
    registry.load_predefined_recognizers(languages=["en"])
    
    # Try initializing NLP engine with Ukrainian spacy model if available
    nlp_engine = None
    try:
        provider = NlpEngineProvider(
            nlp_configuration={
                "nlp_engine_name": "spacy",
                "models": [{"lang_code": "uk", "model_name": "uk_core_news_sm"}],
            }
        )
        nlp_engine = provider.create_engine()
        logger.info("Successfully loaded spacy model 'uk_core_news_sm' for NLP engine.")
    except Exception as e:
        logger.warning(f"Could not load spacy 'uk_core_news_sm' model ({e}). Fallback to pattern-based Ukrainian analysis.")
        registry.add_recognizer(UkNameRecognizer())

    # Register custom Ukrainian recognizers
    registry.add_recognizer(UkRntrcRecognizer())
    registry.add_recognizer(UkPassportRecognizer())
    registry.add_recognizer(UkIbanRecognizer())
    registry.add_recognizer(UkPhoneRecognizer())
    registry.add_recognizer(UkCaseNumberRecognizer())
    registry.add_recognizer(UkAddressRecognizer())
    registry.add_recognizer(UkVehicleRecognizer())
    registry.add_recognizer(UK_EMAIL_RECOGNIZER)

    analyzer = AnalyzerEngine(
        registry=registry,
        nlp_engine=nlp_engine,
        supported_languages=["uk", "en"],
    )
    return analyzer


# Singleton instance
_analyzer_instance: Optional[AnalyzerEngine] = None


def get_analyzer_engine() -> AnalyzerEngine:
    global _analyzer_instance
    if _analyzer_instance is None:
        _analyzer_instance = create_uk_analyzer_engine()
    return _analyzer_instance


def analyze_text(text: str, score_threshold: float = 0.4, language: str = "uk") -> List[RecognizerResult]:
    """
    Analyzes input text for PII entities.
    """
    engine = get_analyzer_engine()
    results = engine.analyze(
        text=text,
        language=language,
        score_threshold=score_threshold,
        return_decision_process=False,
    )
    return results
