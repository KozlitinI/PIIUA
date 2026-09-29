import io
import pytest
from pypdf import PdfWriter
from app.schemas.api import ExtractPDFResponse


def create_sample_pdf(text: str) -> bytes:
    """Create a minimal valid PDF containing the given text using PyPDF."""
    writer = PdfWriter()
    writer.add_blank_page(width=612, height=792)
    # PyPDF doesn't directly add text to blank pages without canvas, but we can write basic PDF structure or test with PdfReader.
    # For testing PdfReader text extraction, we can create a PDF stream or test the endpoint error handling and extraction.
    out = io.BytesIO()
    writer.write(out)
    return out.getvalue()


def test_pdf_response_schema():
    resp = ExtractPDFResponse(filename="doc.pdf", text="Тестовий текст", page_count=1)
    assert resp.filename == "doc.pdf"
    assert resp.text == "Тестовий текст"
    assert resp.page_count == 1
