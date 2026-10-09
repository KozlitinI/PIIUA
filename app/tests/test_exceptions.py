import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.core.exceptions_db import add_exception, delete_exception, get_all_exceptions

client = TestClient(app)


def test_exceptions_crud():
    # Cleanup any existing test item
    for item in get_all_exceptions():
        if item["text"] in ("Тестовий Суд 123", "Оновлений Суд 123"):
            delete_exception(item["id"])

    # 1. Create exception
    payload = {"text": "Тестовий Суд 123"}
    resp = client.post("/api/v1/exceptions", json=payload)
    assert resp.status_code == 200
    data = resp.json()
    exc_id = data["id"]
    assert data["text"] == "Тестовий Суд 123"

    # 2. Prevent duplicate creation
    resp_dup = client.post("/api/v1/exceptions", json=payload)
    assert resp_dup.status_code == 400
    assert "вже існує" in resp_dup.json()["detail"]

    # 3. List exceptions
    resp_list = client.get("/api/v1/exceptions")
    assert resp_list.status_code == 200
    excs = resp_list.json()["exceptions"]
    assert any(item["id"] == exc_id for item in excs)

    # 4. Update exception
    update_payload = {"text": "Оновлений Суд 123"}
    resp_update = client.put(f"/api/v1/exceptions/{exc_id}", json=update_payload)
    assert resp_update.status_code == 200
    assert resp_update.json()["text"] == "Оновлений Суд 123"

    # 5. Delete exception
    resp_del = client.delete(f"/api/v1/exceptions/{exc_id}")
    assert resp_del.status_code == 200
    assert resp_del.json()["status"] == "ok"


def test_pseudonymization_respects_exceptions():
    # Cleanup any existing test item
    for item in get_all_exceptions():
        if item["text"] == "Коваленко Олександр Сергійович":
            delete_exception(item["id"])

    # Add exception fragment
    exc_text = "Коваленко Олександр Сергійович"
    added = add_exception(exc_text)
    exc_id = added["id"]

    try:
        payload = {
            "text": "Позивач Коваленко Олександр Сергійович, РНОКПП 3123456789.",
            "score_threshold": 0.4
        }
        resp = client.post("/api/v1/pseudonymize", json=payload)
        assert resp.status_code == 200
        data = resp.json()

        # The excluded name should NOT be tokenized
        assert "Коваленко Олександр Сергійович" in data["pseudonymized_text"]
        assert "<PERSON_1>" not in data["pseudonymized_text"]
        # RNTRC should still be tokenized
        assert "<RNTRC_1>" in data["pseudonymized_text"]

    finally:
        delete_exception(exc_id)


def test_fop_paktum_and_flydoc_exceptions():
    # Cleanup any existing test items
    for item in get_all_exceptions():
        if item["text"] in ("ФОППактум", "ФОПFlyDoc"):
            delete_exception(item["id"])

    exc1 = add_exception("ФОППактум")["id"]
    exc2 = add_exception("ФОПFlyDoc")["id"]

    try:
        contract_snippet = (
            "Оплата послуг ФОППактум та сервісу ФОПFlyDoc здійснюється згідно договору. "
            "Пакет ФОП Пактум та ФОП FlyDoc на місяць."
        )
        payload = {
            "text": contract_snippet,
            "score_threshold": 0.4
        }
        resp = client.post("/api/v1/pseudonymize", json=payload)
        assert resp.status_code == 200
        data = resp.json()

        pseudo_text = data["pseudonymized_text"]
        # None of the exception phrases should be replaced with tokens <ORG_...>
        assert "ФОППактум" in pseudo_text
        assert "ФОПFlyDoc" in pseudo_text
        assert "ФОП Пактум" in pseudo_text
        assert "ФОП FlyDoc" in pseudo_text
        assert "<ORG_1>" not in pseudo_text
        assert "<ORG_2>" not in pseudo_text
    finally:
        delete_exception(exc1)
        delete_exception(exc2)
