import logging
from typing import List, Optional
import spacy

# Explicitly import all spacy_curated_transformers components & architectures to register them into spaCy's global registry for PyInstaller frozen mode
try:
    import spacy_curated_transformers
    import spacy_curated_transformers.pipeline
    import spacy_curated_transformers.pipeline.transformer
    import spacy_curated_transformers.models
    import spacy_curated_transformers.models.listeners
    import spacy_curated_transformers.models.architectures
    import spacy_curated_transformers.models.pooling
    import spacy_curated_transformers.models.scalar_weight
    import spacy_curated_transformers.models.with_non_ws_tokens
    import spacy_curated_transformers.models.with_strided_spans
    import spacy_curated_transformers.models.remove_eos_bos
    import spacy_curated_transformers.tokenization
except ImportError:
    pass

try:
    import spacy_legacy
except ImportError:
    pass

try:
    import spacy_loggers
except ImportError:
    pass

from presidio_analyzer import (
    AnalyzerEngine,
    RecognizerRegistry,
    RecognizerResult,
    PatternRecognizer,
    Pattern,
)
from presidio_analyzer.nlp_engine import SpacyNlpEngine

from app.recognizers.uk_rntrc import UkRntrcRecognizer
from app.recognizers.uk_passport import UkPassportRecognizer
from app.recognizers.uk_iban import UkIbanRecognizer
from app.recognizers.uk_phone import UkPhoneRecognizer
from app.recognizers.uk_case_number import UkCaseNumberRecognizer
from app.recognizers.uk_address import UkAddressRecognizer
from app.recognizers.uk_vehicle import UkVehicleRecognizer
from app.recognizers.uk_names import UkNameRecognizer
from app.recognizers.uk_organization import UkOrganizationRecognizer

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
    Safely loads spaCy models in standalone PyInstaller environments without triggering spacy.cli.download.
    """
    registry = RecognizerRegistry(supported_languages=["uk", "en"])
    try:
        registry.load_predefined_recognizers(languages=["en"])
    except Exception as e:
        logger.warning(f"Could not load predefined recognizers: {e}")
    
    # 1. Load Ukrainian spaCy model directly via package import or spacy.load fallback
    nlp_uk = None
    model_name_uk = "none"

    try:
        import uk_core_news_trf
        nlp_uk = uk_core_news_trf.load()
        model_name_uk = "uk_core_news_trf"
        logger.info("Successfully loaded spacy model 'uk_core_news_trf' via direct package import.")
    except Exception as e1:
        logger.warning(f"Could not import uk_core_news_trf directly ({e1}). Trying uk_core_news_sm...")
        try:
            import uk_core_news_sm
            nlp_uk = uk_core_news_sm.load()
            model_name_uk = "uk_core_news_sm"
            logger.info("Successfully loaded spacy model 'uk_core_news_sm' via direct package import.")
        except Exception as e2:
            logger.warning(f"Could not import uk_core_news_sm directly ({e2}). Trying spacy.load...")
            try:
                nlp_uk = spacy.load("uk_core_news_trf")
                model_name_uk = "uk_core_news_trf"
            except Exception:
                try:
                    nlp_uk = spacy.load("uk_core_news_sm")
                    model_name_uk = "uk_core_news_sm"
                except Exception as e3:
                    logger.warning(f"Could not load spaCy Ukrainian model ({e3}). Fallback to blank model.")

    if nlp_uk is None:
        nlp_uk = spacy.blank("uk")

    # 2. Load or fallback English model to prevent Presidio from calling spacy.cli.download
    try:
        nlp_en = spacy.load("en_core_web_sm")
    except Exception:
        nlp_en = spacy.blank("en")

    # 3. Construct SpacyNlpEngine with explicitly assigned loaded spaCy pipelines
    nlp_engine = SpacyNlpEngine(models={"uk": model_name_uk, "en": "en"})
    nlp_engine.nlp = {"uk": nlp_uk, "en": nlp_en}

    # Register custom Ukrainian recognizers
    registry.add_recognizer(UkOrganizationRecognizer())
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
