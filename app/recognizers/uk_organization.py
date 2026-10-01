# Copyright 2026 Ihor Kozlitin
# SPDX-License-Identifier: Apache-2.0

import re
from typing import List, Optional
from presidio_analyzer import PatternRecognizer, Pattern, RecognizerResult, AnalysisExplanation
from presidio_analyzer.nlp_engine import NlpArtifacts


def validate_edrpou_checksum(edrpou_str: str) -> bool:
    """
    Validates Ukrainian 8-digit EDRPOU (ЄДРПОУ) legal entity code checksum.
    """
    if len(edrpou_str) != 8 or not edrpou_str.isdigit():
        return False
    
    digits = [int(d) for d in edrpou_str]
    val = int(edrpou_str)
    
    w1 = [1, 2, 3, 4, 5, 6, 7]
    w2 = [3, 4, 5, 6, 7, 8, 9]

    if val > 30000000 and val < 60000000:
        w1 = [7, 1, 2, 3, 4, 5, 6]
        w2 = [9, 3, 4, 5, 6, 7, 8]

    total = sum(digits[i] * w1[i] for i in range(7))
    remainder = total % 11

    if remainder > 10:
        total = sum(digits[i] * w2[i] for i in range(7))
        remainder = total % 11

EXCLUDED_CONTRACT_TERMS = {
    # Contract roles & job titles (Постачальник, Покупець, Директор, Бухгалтер, etc.)
    "постачальник", "постачальника", "постачальнику", "постачальником", "постачальниці", "постачальницею", "постачальники", "постачальників",
    "покупець", "покупця", "покупцеві", "покупцю", "покупцем", "покупці", "покупців",
    "замовник", "замовника", "замовникові", "замовником", "замовники", "замовників",
    "виконавець", "виконавця", "виконавцеві", "виконавцем", "виконавці", "виконавців",
    "продавець", "продавця", "продавцеві", "продавцем", "продавці", "продавців",
    "орендодавець", "орендодавця", "орендар", "орендаря",
    "позивач", "позивача", "відповідач", "відповідача",
    "підписант", "підписанта", "заявник", "заявника", "скаржник",

    # Corporate job positions
    "директор", "директора", "директору", "директором", "директорові", "директори", "директорів",
    "заступник директора", "заступника директора", "заступнику директора", "заступником директора", "заступникові директора",
    "генеральний директор", "генерального директора", "генеральному директору", "генеральним директором",
    "виконавчий директор", "виконавчого директора", "виконавчому директору", "виконавчим директором",
    "фінансовий директор", "фінансового директора", "фінансовому директору", "фінансовим директором",
    "комерційний директор", "комерційного директора", "комерційному директору", "комерційним директором",
    "технічний директор", "технічного директора", "технічному директору", "технічним директором",
    "голова правління", "голови правління", "голові правління", "головою правління",
    "президент", "президента", "президенту", "президентом",
    "керуючий", "керуючого", "керуючому", "керуючим",
    "уповноважена особа", "уповноваженої особи", "уповноваженій особі", "уповноважену особу", "уповноваженою особою",
    "бухгалтер", "бухгалтера", "бухгалтеру", "бухгалтером", "бухгалтери", "бухгалтерів",
    "головний бухгалтер", "головного бухгалтера", "головному бухгалтеру", "головним бухгалтером", "головной бухгалтер",
    "керівник", "керівника", "керівникові", "керівником", "менеджер", "менеджера",
    "юрист", "юрисконсульт", "представник", "представника", "адвокат", "адвоката",

    # Parties
    "сторона", "сторони", "сторін", "сторону", "сторонам", "сторонами", "стороні",

    # Contract document terms
    "договір", "договору", "договором", "договорі", "договори", "договорів", "договорам", "договорами",
    "акт", "акту", "актом", "акті", "акти", "актів", "актам", "актами",
    "заявка", "заявки", "заявку", "заявкам", "заявками",
    "додаток", "додатка", "додатку", "додатки", "додатків",
    "специфікація", "специфікації", "специфікацію",

    # Product / Subject matter terms
    "програмний комплекс", "програмного комплексу", "програмному комплексу", "програмним комплексом", "програмному комплексі", "програмні комплекси", "програмних комплексів",
    "програмна продукція", "програмної продукції", "програмну продукцію",
    "ітс",
}


class UkOrganizationRecognizer(PatternRecognizer):
    """
    Recognizer for Ukrainian Organizations, Companies, Legal Entities, FOPs, EDRPOU codes,
    and quoted company names with document-level entity propagation.
    """
    PATTERNS = [
        # Full Legal Entity with explicit prefix: ТОВ "Назва", ТзОВ «Назва», ПП 'Назва'
        Pattern(
            name="uk_org_full_quotes",
            regex=r"\b(?:ТОВ|ТзОВ|ПП|ПрАТ|ПАТ|АТ|ДП|ГО|КП|ОСББ|БФ)\s*[\"«'“][А-ЯІЇЄҐA-Z0-9\s\.\-–—]+[\"»'”]",
            score=0.95,
        ),
        # Long Organizational Form: Товариство з обмеженою відповідальністю "Назва"
        Pattern(
            name="uk_org_long_form",
            regex=r"\b(?:Товариство з обмеженою відповідальністю|Приватне акціонерне товариство|Публічне акціонерне товариство|Акціонерне товариство|Приватне підприємство|Громадська організація|Благодійний фонд|Державне підприємство)\s+[\"«'“][А-ЯІЇЄҐA-Z0-9\s\.\-–—]+[\"»'”]",
            score=0.98,
        ),
        # Standalone Quoted Name: «ВебСофт», «Альфа-Трейд», "ПриватБанк"
        Pattern(
            name="uk_org_quoted_standalone",
            regex=r"(?:[«\"'“][А-ЯІЇЄҐA-Z0-9][а-яіїєґa-zA-Z0-9\s\.\-–—]+[»\"'”])",
            score=0.88,
        ),
        # Sole Proprietor (ФОП): ФОП Коваленко О.С. or Фізична особа-підприємець Шевченко Т.Г.
        Pattern(
            name="uk_org_fop",
            regex=r"\b(?:ФОП|Фізична особа-підприємець)\s+[А-ЯІЇЄҐ][а-яіїєґ]+(?:\s+[А-ЯІЇЄҐ]\.\s?[А-ЯІЇЄҐ]\.|\s+[А-ЯІЇЄҐ][а-яіїєґ]+\s+[А-ЯІЇЄҐ][а-яіїєґ]+)?\b",
            score=0.95,
        ),
        # Abbreviation + Capitalized Name without quotes: ТОВ Автотрейд
        Pattern(
            name="uk_org_abbr_name",
            regex=r"\b(?:ТОВ|ТзОВ|ПП|ПрАТ|ПАТ|АТ|ДП|ГО|КП)\s+[А-ЯІЇЄҐ][а-яіїєґ0-9A-Z]+(?:\s+[А-ЯІЇЄҐ0-9A-Z][а-яіїєґ0-9A-Z]+)?\b",
            score=0.85,
        ),
    ]

    CONTEXT = [
        "єдрпоу", "код єдрпоу", "компанія", "підприємство", "товариство",
        "фірма", "організація", "банк", "уповноважений", "директор", "реквізити", "єгрпоу"
    ]

    def __init__(
        self,
        patterns: Optional[List[Pattern]] = None,
        context: Optional[List[str]] = None,
        supported_language: str = "uk",
    ):
        patterns = patterns if patterns else self.PATTERNS
        context = context if context else self.CONTEXT
        super().__init__(
            supported_entity="ORGANIZATION",
            patterns=patterns,
            context=context,
            supported_language=supported_language,
        )

    def validate_result(self, pattern_text: str) -> Optional[bool]:
        """
        If match is a pure 8-digit code, validate EDRPOU checksum algorithm.
        If match is a standard contract role or term, reject it.
        """
        clean_text = pattern_text.strip(" \"«'“»'”.,:;()[]{}").strip()
        if clean_text.lower() in EXCLUDED_CONTRACT_TERMS:
            return False

        if len(clean_text) == 8 and clean_text.isdigit():
            if validate_edrpou_checksum(clean_text):
                return True
            return False

        return None

    def analyze(
        self, text: str, entities: List[str], nlp_artifacts: Optional[NlpArtifacts] = None
    ) -> List[RecognizerResult]:
        """
        Analyze text for organizations, including document-level propagation of detected company names.
        """
        results = super().analyze(text, entities, nlp_artifacts)
        if not results:
            return []

        # Filter out any results that match excluded contract terms
        filtered_results = []
        for r in results:
            matched = text[r.start:r.end].strip(" \"«'“»'”.,:;()[]{}").strip().lower()
            if matched not in EXCLUDED_CONTRACT_TERMS:
                filtered_results.append(r)
        results = filtered_results

        # Extract core organization names from detected spans
        known_org_names = set()
        for r in results:
            span_text = text[r.start:r.end].strip()
            # Clean prefixes (both long forms and abbreviations) and quotation marks
            cleaned = re.sub(
                r"^(?:Товариство з обмеженою відповідальністю|Приватне акціонерне товариство|Публічне акціонерне товариство|Акціонерне товариство|Приватне підприємство|Громадська організація|Благодійний фонд|Державне підприємство|ТОВ|ТзОВ|ПП|ПрАТ|ПАТ|АТ|ДП|ГО|КП|ОСББ|БФ)\s*",
                "",
                span_text,
                flags=re.IGNORECASE
            )
            cleaned = cleaned.strip(" \"«'“»'”.,:;()[]{}").strip()
            if cleaned.lower() not in EXCLUDED_CONTRACT_TERMS and len(cleaned) >= 3 and not cleaned.isdigit():
                known_org_names.add(cleaned)

        # Propagate known organization names throughout the document
        additional_results = []
        existing_spans = [(r.start, r.end) for r in results]

        for name in known_org_names:
            escaped_name = re.escape(name)
            pattern = re.compile(rf"(?:[«\"'“])?{escaped_name}(?:[»\"'”])?")
            
            for m in pattern.finditer(text):
                start, end = m.span()
                overlap = any(not (end <= s or start >= e) for s, e in existing_spans)
                if not overlap:
                    res = RecognizerResult(
                        entity_type="ORGANIZATION",
                        start=start,
                        end=end,
                        score=0.92,
                        analysis_explanation=AnalysisExplanation(
                            recognizer=self.name,
                            original_score=0.92,
                            pattern_name="uk_org_propagated",
                        ),
                    )
                    additional_results.append(res)
                    existing_spans.append((start, end))

        return results + additional_results
