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


def test_uk_person_name_marko_lemmatization():
    text = "Позивач — Марко. Документ укладено з Марком. Позови від Марка було розглянуто."
    pseudo_text, mapping, entities = process_pseudonymization(text)

    # All inflected forms of "Марко" (Марко, Марком, Марка) must resolve to the same single token <PERSON_1>
    assert "<PERSON_1>" in pseudo_text
    assert "Марка" not in pseudo_text
    assert "Марком" not in pseudo_text
    assert "Марко" not in pseudo_text

    # The mapping should hold the base nominative form "Марко"
    assert mapping["<PERSON_1>"] == "Марко"


def test_uk_name_two_part_false_positives():
    false_positives = [
        "Власник компанії",
        "продажу будівельних",
        "яка розробляє",
        "корпоративні вебсистеми",
    ]
    for text in false_positives:
        results = analyze_text(text)
        person_results = [r for r in results if r.entity_type == "PERSON"]
        assert len(person_results) == 0, f"False positive detected for '{text}': {person_results}"

    # Verify legitimate two-part names are still recognized
    valid_names = ["Тарас Шевченко", "Ольга Коваленко"]
    for text in valid_names:
        results = analyze_text(text)
        person_results = [r for r in results if r.entity_type == "PERSON"]
        assert len(person_results) >= 1, f"Failed to recognize valid name '{text}'"


def test_uk_name_sample_case_sensitivity_and_initials():
    text = "Сторони медіації Козлітін Ігор Валерійович та Пожаров С.В. погодились розглянути додаткові документи і т.п. та вирішити судьбу автомобіля Москвич СО 2798 НВ."
    results = analyze_text(text)
    person_spans = [text[r.start:r.end] for r in results if r.entity_type == "PERSON"]
    
    # Must only match exact names, no false positives
    assert set(person_spans) == {"Козлітін Ігор Валерійович", "Пожаров С.В."}
    assert "С.В. погодились" not in person_spans
    assert "т.п. та" not in person_spans
    assert "судьбу автомобіля Москвич" not in person_spans


def test_uk_edrpou_mfo_and_ipn_recognition():
    text = (
        "Код ЄДРПОУ 35877574, "
        "МФО 300614, "
        "ІПН 358775726562, "
        "РНОКПП 3123456789."
    )
    pseudo_text, mapping, entities = process_pseudonymization(text)

    # Check mapping values
    values = set(mapping.values())
    assert "35877574" in values
    assert "300614" in values
    assert "358775726562" in values
    assert "3123456789" in values

    # Check tags in pseudonymized text
    assert "<EDRPOU_1>" in pseudo_text
    assert "<MFO_1>" in pseudo_text
    assert "<RNTRC_1>" in pseudo_text
    assert "<RNTRC_2>" in pseudo_text


def test_uk_complex_address_recognition():
    addr1 = "вул. Університетська, будинок № 13-А, м. Київ, 03110"
    addr2 = "вул. Північно-Сирецька, будинок № 1-3, м. Київ, 04136"

    pseudo1, mapping1, _ = process_pseudonymization(f"Адреса: {addr1}")
    assert "<ADDRESS_1>" in pseudo1
    assert mapping1["<ADDRESS_1>"] == addr1

    pseudo2, mapping2, _ = process_pseudonymization(f"Адреса: {addr2}")
    assert "<ADDRESS_1>" in pseudo2
    assert mapping2["<ADDRESS_1>"] == addr2


def test_uk_inflected_pib_recognition():
    t1 = "в особі Заступника Директора Брасло Олени Миколаївни, яка діє на підставі Довіреності"
    pseudo1, mapping1, entities1 = process_pseudonymization(t1)
    pib1_entities = [e for e in entities1 if e.entity_type == "PERSON"]
    assert len(pib1_entities) == 1
    assert pib1_entities[0].text == "Брасло Олени Миколаївни"

    t2 = "в особі Директора Агєєва Максима Юрійовича, який діє на підставі Статуту"
    pseudo2, mapping2, entities2 = process_pseudonymization(t2)
    pib2_entities = [e for e in entities2 if e.entity_type == "PERSON"]
    assert len(pib2_entities) == 1
    assert pib2_entities[0].text == "Агєєва Максима Юрійовича"





