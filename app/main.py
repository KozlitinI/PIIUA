from pathlib import Path
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from app.schemas.api import (
    AnalyzeRequest,
    AnalyzeResponse,
    PseudonymizeRequest,
    PseudonymizeResponse,
    RestoreRequest,
    RestoreResponse,
    DetectedEntity,
)
from app.core.analyzer import analyze_text
from app.core.anonymizer import process_pseudonymization, process_restoration

app = FastAPI(
    title="PIIUA - Ukrainian PII Pseudonymization & Restoration Service for Mediation/ODR",
    description="Privacy-preserving system for de-identifying personal data in Ukrainian legal and dispute texts using Presidio.",
    version="1.0.0",
)

# CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

BASE_DIR = Path(__file__).resolve().parent
STATIC_DIR = BASE_DIR / "static"

if STATIC_DIR.exists():
    app.mount("/static", StaticFiles(directory=str(STATIC_DIR)), name="static")


@app.get("/", include_in_schema=False)
async def serve_index():
    index_file = STATIC_DIR / "index.html"
    if index_file.exists():
        return FileResponse(str(index_file))
    return {"message": "PIIUA API is running. Access /docs for API documentation."}


@app.get("/health")
async def health_check():
    return {"status": "ok", "service": "PIIUA", "version": "1.0.0"}


@app.post("/api/v1/analyze", response_model=AnalyzeResponse)
async def analyze_pii(request: AnalyzeRequest):
    """
    Detect PII entities in Ukrainian text without modifying the text.
    """
    try:
        raw_results = analyze_text(text=request.text, score_threshold=request.score_threshold)
        entities = [
            DetectedEntity(
                entity_type=r.entity_type,
                start=r.start,
                end=r.end,
                score=round(r.score, 2),
                text=request.text[r.start:r.end],
            )
            for r in raw_results
        ]
        return AnalyzeResponse(entities=entities)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/v1/pseudonymize", response_model=PseudonymizeResponse)
async def pseudonymize_pii(request: PseudonymizeRequest):
    """
    Pseudonymize Ukrainian text by replacing PII entities with structured reversible tokens (<PERSON_1>, <RNTRC_1>, etc.).
    Returns the pseudonymized text, the bidirectional token mapping dictionary, and detected entities.
    """
    try:
        pseudo_text, mapping, entities = process_pseudonymization(
            text=request.text,
            score_threshold=request.score_threshold
        )
        return PseudonymizeResponse(
            pseudonymized_text=pseudo_text,
            mapping=mapping,
            entities=entities
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/v1/restore", response_model=RestoreResponse)
async def restore_pii(request: RestoreRequest):
    """
    Restore original PII values back into LLM responses or pseudonymized texts using the token mapping dictionary.
    """
    try:
        restored = process_restoration(
            pseudonymized_text=request.text,
            mapping=request.mapping
        )
        return RestoreResponse(restored_text=restored)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
