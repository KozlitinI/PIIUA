import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def test_health_endpoint():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok", "service": "PIIUA", "version": "1.0.0"}


def test_analyze_endpoint():
    payload = {
        "text": "Позивач Коваленко Олександр Сергійович, РНОКПП 3123456789.",
        "score_threshold": 0.4
    }
    response = client.post("/api/v1/analyze", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert "entities" in data
    assert len(data["entities"]) >= 2


def test_pseudonymize_endpoint():
    payload = {
        "text": "Позивач Коваленко Олександр Сергійович (РНОКПП 3123456789) надав IBAN UA123456789012345678901234567.",
        "score_threshold": 0.4
    }
    response = client.post("/api/v1/pseudonymize", json=payload)
    assert response.status_code == 200
    data = response.json()

    assert "<PERSON_1>" in data["pseudonymized_text"]
    assert "<RNTRC_1>" in data["pseudonymized_text"]
    assert "<IBAN_1>" in data["pseudonymized_text"]
    assert "Коваленко Олександр Сергійович" not in data["pseudonymized_text"]

    mapping = data["mapping"]
    assert mapping["<PERSON_1>"] == "Коваленко Олександр Сергійович"
    assert mapping["<RNTRC_1>"] == "3123456789"
    assert mapping["<IBAN_1>"] == "UA123456789012345678901234567"


def test_restore_endpoint():
    pseudo_text = "Згідно з позицією <PERSON_1>, борг виплачено на <IBAN_1>."
    mapping = {
        "<PERSON_1>": "Коваленко Олександр Сергійович",
        "<IBAN_1>": "UA123456789012345678901234567"
    }
    payload = {
        "text": pseudo_text,
        "mapping": mapping
    }
    response = client.post("/api/v1/restore", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["restored_text"] == "Згідно з позицією Коваленко Олександр Сергійович, борг виплачено на UA123456789012345678901234567."
