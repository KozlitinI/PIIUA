from typing import Dict, List, Optional
from pydantic import BaseModel, Field


class DetectedEntity(BaseModel):
    entity_type: str = Field(..., description="Type of PII entity (e.g. PERSON, UK_RNTRC, UK_IBAN)")
    start: int = Field(..., description="Start character index")
    end: int = Field(..., description="End character index")
    score: float = Field(..., description="Confidence score")
    text: str = Field(..., description="Extracted raw entity value")


class AnalyzeRequest(BaseModel):
    text: str = Field(..., description="Raw text to analyze for PII")
    score_threshold: Optional[float] = Field(0.4, description="Minimum confidence threshold")
    model_name: Optional[str] = Field("uk_core_news_trf", description="spaCy Ukrainian model name (uk_core_news_trf, uk_core_news_lg, or uk_core_news_sm)")


class AnalyzeResponse(BaseModel):
    entities: List[DetectedEntity] = Field(default_factory=list)


class PseudonymizeRequest(BaseModel):
    text: str = Field(..., description="Document or text to pseudonymize")
    score_threshold: Optional[float] = Field(0.4, description="Minimum confidence threshold")
    model_name: Optional[str] = Field("uk_core_news_trf", description="spaCy Ukrainian model name (uk_core_news_trf, uk_core_news_lg, or uk_core_news_sm)")


class PseudonymizeResponse(BaseModel):
    pseudonymized_text: str = Field(..., description="Text with PII replaced by structured tokens (<PERSON_1>, etc.)")
    mapping: Dict[str, str] = Field(..., description="Bidirectional token-to-original PII dictionary for local restoration")
    entities: List[DetectedEntity] = Field(default_factory=list, description="List of detected PII items")


class RestoreRequest(BaseModel):
    text: str = Field(..., description="Text returned by LLM containing PII tokens (<PERSON_1>, etc.)")
    mapping: Dict[str, str] = Field(..., description="Token mapping dictionary returned during pseudonymization")


class RestoreResponse(BaseModel):
    restored_text: str = Field(..., description="Final text with original PII restored")
