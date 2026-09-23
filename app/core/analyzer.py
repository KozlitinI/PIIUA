import logging
import warnings
warnings.filterwarnings("ignore", category=FutureWarning)
warnings.filterwarnings("ignore", message=".*torch.jit.script.*")
warnings.filterwarnings("ignore", category=UserWarning)

try:
    import spacy
except Exception as _e_spacy:
    spacy = None

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


def create_uk_analyzer_engine(model_name: str = "uk_core_news_trf") -> AnalyzerEngine:
    """
    Creates and configures Presidio AnalyzerEngine with Ukrainian recognizers.
    Safely loads requested spaCy model (uk_core_news_trf or uk_core_news_sm).
    """
    registry = RecognizerRegistry(supported_languages=["uk", "en"])
    try:
        registry.load_predefined_recognizers(languages=["en"])
    except Exception as e:
        logger.warning(f"Could not load predefined recognizers: {e}")
    
    # 1. Load requested Ukrainian spaCy model
    nlp_uk = None
    model_name_uk = "none"
    requested_model = model_name if model_name in ("uk_core_news_trf", "uk_core_news_sm") else "uk_core_news_trf"

    # Try loading requested model
    if requested_model == "uk_core_news_trf":
        try:
            import uk_core_news_trf
            nlp_uk = uk_core_news_trf.load()
            model_name_uk = "uk_core_news_trf"
            logger.info("Successfully loaded spacy model 'uk_core_news_trf' via direct package import.")
        except Exception as e1:
            try:
                nlp_uk = spacy.load("uk_core_news_trf")
                model_name_uk = "uk_core_news_trf"
                logger.info("Successfully loaded spacy model 'uk_core_news_trf' via spacy.load.")
            except Exception as e2:
                logger.warning(f"Could not load uk_core_news_trf ({e1}, {e2}). Trying fallback to uk_core_news_sm...")
                requested_model = "uk_core_news_sm"

    if requested_model == "uk_core_news_sm" and nlp_uk is None:
        try:
            import uk_core_news_sm
            nlp_uk = uk_core_news_sm.load()
            model_name_uk = "uk_core_news_sm"
            logger.info("Successfully loaded spacy model 'uk_core_news_sm' via direct package import.")
        except Exception as e1:
            try:
                nlp_uk = spacy.load("uk_core_news_sm")
                model_name_uk = "uk_core_news_sm"
                logger.info("Successfully loaded spacy model 'uk_core_news_sm' via spacy.load.")
            except Exception as e2:
                logger.warning(f"Could not load uk_core_news_sm ({e1}, {e2}). Fallback to blank model.")

    if nlp_uk is None:
        if spacy is not None:
            try:
                nlp_uk = spacy.blank("uk")
            except Exception:
                nlp_uk = None
        model_name_uk = "none"

    # 2. Load or fallback English model to prevent Presidio from calling spacy.cli.download
    nlp_en = None
    if spacy is not None:
        try:
            nlp_en = spacy.load("en_core_web_sm")
        except Exception:
            try:
                nlp_en = spacy.blank("en")
            except Exception:
                nlp_en = None

    # 3. Construct SpacyNlpEngine with explicitly assigned loaded spaCy pipelines
    nlp_engine = None
    if nlp_uk is not None:
        try:
            nlp_engine = SpacyNlpEngine(models={"uk": model_name_uk, "en": "en"})
            nlp_engine.nlp = {"uk": nlp_uk, "en": nlp_en or nlp_uk}
        except Exception as _e_nlp:
            logger.warning(f"Could not initialize SpacyNlpEngine ({_e_nlp}). Fallback to pattern-based analysis.")
            nlp_engine = None

    # Register custom Ukrainian recognizers
    #registry.add_recognizer(UkNameRecognizer())
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


# Cache of analyzer engine instances per model name
_analyzer_instances: Dict[str, AnalyzerEngine] = {}


def get_analyzer_engine(model_name: str = "uk_core_news_trf") -> AnalyzerEngine:
    global _analyzer_instances
    key = model_name if model_name in ("uk_core_news_trf", "uk_core_news_sm") else "uk_core_news_trf"
    if key not in _analyzer_instances:
        _analyzer_instances[key] = create_uk_analyzer_engine(model_name=key)
    return _analyzer_instances[key]


def analyze_text(
    text: str,
    score_threshold: float = 0.4,
    language: str = "uk",
    model_name: str = "uk_core_news_trf"
) -> List[RecognizerResult]:
    """
    Analyzes input text for PII entities using requested spaCy model.
    """
    engine = get_analyzer_engine(model_name=model_name)
    results = engine.analyze(
        text=text,
        language=language,
        score_threshold=score_threshold,
        return_decision_process=False,
    )
    return results
