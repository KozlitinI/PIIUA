import io
import pytest
from docx import Document
from fastapi.testclient import TestClient
from app.main import app
from app.schemas.api import ExtractWordResponse

client = TestClient(app)


def create_sample_docx(text: str) -> bytes:
    """Create a minimal valid docx file containing the given text."""
    doc = Document()
    doc.add_paragraph(text)
    out = io.BytesIO()
    doc.save(out)
    return out.getvalue()


def test_word_response_schema():
    resp = ExtractWordResponse(filename="test.docx", text="Тестовий текст Word")
    assert resp.filename == "test.docx"
    assert resp.text == "Тестовий текст Word"


def test_extract_word_endpoint_success():
    docx_bytes = create_sample_docx("Позовна заява від Шевченка О.В.")
    response = client.post(
        "/api/v1/extract-word",
        files={"file": ("document.docx", docx_bytes, "application/vnd.openxmlformats-officedocument.wordprocessingml.document")}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["filename"] == "document.docx"
    assert "Позовна заява від Шевченка О.В." in data["text"]


def test_extract_word_endpoint_invalid_file_type():
    response = client.post(
        "/api/v1/extract-word",
        files={"file": ("test.txt", b"Hello world", "text/plain")}
    )
    assert response.status_code == 400
    assert "не є Word-документом" in response.json()["detail"]


def test_extract_word_endpoint_empty_file():
    response = client.post(
        "/api/v1/extract-word",
        files={"file": ("empty.docx", b"", "application/vnd.openxmlformats-officedocument.wordprocessingml.document")}
    )
    assert response.status_code == 400
    assert "порожній" in response.json()["detail"]
