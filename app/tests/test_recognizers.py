import pytest
from app.core.analyzer import analyze_text
from app.core.anonymizer import process_pseudonymization, process_restoration
from app.recognizers.uk_rntrc import validate_rntrc_checksum


def test_rntrc_checksum():
    # Valid Ukrainian RNTRC checksum test
    assert validate_rntrc_checksum("3123456789") is True
    # Invalid RNTRC checksum
    assert validate_rntrc_checksum("1234567890") is False


def test_uk_rntrc_recognition():
    text = "Громадянин з РНОКПП 3123456789 є платником податків."
    results = analyze_text(text)
    rntrc_results = [r for r in results if r.entity_type == "UK_RNTRC"]
    assert len(rntrc_results) == 1
    assert text[rntrc_results[0].start:rntrc_results[0].end] == "3123456789"


def test_uk_passport_recognition():
    text = "Паспорт громадянина серії КМ 987654 виданий у м. Києві."
    results = analyze_text(text)
    passport_results = [r for r in results if r.entity_type == "UK_PASSPORT"]
    assert len(passport_results) >= 1
    assert "КМ 987654" in text[passport_results[0].start:passport_results[0].end]


def test_uk_iban_recognition():
    text = "Сплатити за договором на IBAN UA123456789012345678901234567 у банку."
    results = analyze_text(text)
    iban_results = [r for r in results if r.entity_type == "UK_IBAN"]
    assert len(iban_results) == 1
    assert text[iban_results[0].start:iban_results[0].end] == "UA123456789012345678901234567"


def test_uk_phone_recognition():
    text = "Контактний телефон відповідача: +380501234567."
    results = analyze_text(text)
    phone_results = [r for r in results if r.entity_type == "UK_PHONE"]
    assert len(phone_results) == 1
    assert "+380501234567" in text[phone_results[0].start:phone_results[0].end]


def test_uk_case_number_recognition():
    text = "Печерський суд розглядає справу № 757/12345/23-ц за позовом."
    results = analyze_text(text)
    case_results = [r for r in results if r.entity_type == "UK_CASE_NUMBER"]
    assert len(case_results) >= 1
    assert "757/12345/23-ц" in text[case_results[0].start:case_results[0].end]


def test_uk_name_recognition():
    text = "Позивач Шевченко Тарас Григорович звернувся до суду."
    results = analyze_text(text)
    person_results = [r for r in results if r.entity_type == "PERSON"]
    assert len(person_results) >= 1
    assert "Шевченко Тарас Григорович" in text[person_results[0].start:person_results[0].end]


def test_uk_organization_recognition():
    text = "Договір укладено з ТОВ \"Агропром-Трейд\" та ФОП Іваненко І.В."
    results = analyze_text(text)
    org_results = [r for r in results if r.entity_type == "ORGANIZATION"]
    assert len(org_results) >= 1
    org_texts = [text[r.start:r.end] for r in org_results]
    assert any("ТОВ" in t or "Агропром" in t for t in org_texts)


def test_user_sample_organization_pseudonymization():
    text = """Сторони:
ТОВ «Альфа-Трейд» — компанія, що продає побутову техніку.
ТОВ «ВебСофт» — IT-компанія, яка розробляє для «Альфа-Трейд» новий інтернет-магазин.

Ситуація:
За договором «ВебСофт» мав запустити новий сайт до 1 вересня. Вартість проєкту — 800 000 грн. «Альфа-Трейд» уже сплатив 70% суми."""

    pseudo_text, mapping, entities = process_pseudonymization(text)

    # Check that ALL occurrences of «Альфа-Трейд» and «ВебСофт» are pseudonymized
    assert "Альфа-Трейд" not in pseudo_text
    assert "ВебСофт" not in pseudo_text
    assert "<ORG_1>" in pseudo_text
    assert "<ORG_2>" in pseudo_text

    # Verify that full restoration restores the company names into text
    restored = process_restoration(pseudo_text, mapping)
    assert "Альфа-Трейд" in restored
    assert "ВебСофт" in restored


def test_full_pipeline_pseudonymize_and_restore():
    original = "Позивач Шевченко Тарас Григорович, РНОКПП 3123456789, телефон +380501234567."
    pseudo_text, mapping, entities = process_pseudonymization(original)

    # Check tags present in pseudo_text
    assert "<PERSON_1>" in pseudo_text
    assert "<RNTRC_1>" in pseudo_text
    assert "<PHONE_1>" in pseudo_text
    assert "Шевченко Тарас Григорович" not in pseudo_text
    assert "3123456789" not in pseudo_text

    # Check mapping
    assert mapping["<PERSON_1>"] == "Шевченко Тарас Григорович"
    assert mapping["<RNTRC_1>"] == "3123456789"

    # Check restoration
    restored = process_restoration(pseudo_text, mapping)
    assert restored == original


def test_uk_person_name_lemmatization():
    text = "Позивач — Андрій Мельник. Документ укладено з Андрієм Мельником. Позови до Андрія Мельника відхилено."
    pseudo_text, mapping, entities = process_pseudonymization(text)

    # All inflected forms of "Андрій Мельник" must resolve to the same single token <PERSON_1>
    assert "<PERSON_1>" in pseudo_text
    assert "Андрія Мельника" not in pseudo_text
    assert "Андрій Мельник" not in pseudo_text
    assert "Андрієм Мельником" not in pseudo_text

    # The mapping should hold the base nominative form
    assert mapping["<PERSON_1>"] == "Андрій Мельник"
