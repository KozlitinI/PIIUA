# Recognizers package
from app.recognizers.uk_rntrc import UkRntrcRecognizer
from app.recognizers.uk_edrpou import UkEdrpouRecognizer
from app.recognizers.uk_mfo import UkMfoRecognizer
from app.recognizers.uk_passport import UkPassportRecognizer
from app.recognizers.uk_iban import UkIbanRecognizer
from app.recognizers.uk_phone import UkPhoneRecognizer
from app.recognizers.uk_case_number import UkCaseNumberRecognizer
from app.recognizers.uk_address import UkAddressRecognizer
from app.recognizers.uk_vehicle import UkVehicleRecognizer
from app.recognizers.uk_names import UkNameRecognizer
from app.recognizers.uk_organization import UkOrganizationRecognizer

__all__ = [
    "UkRntrcRecognizer",
    "UkEdrpouRecognizer",
    "UkMfoRecognizer",
    "UkPassportRecognizer",
    "UkIbanRecognizer",
    "UkPhoneRecognizer",
    "UkCaseNumberRecognizer",
    "UkAddressRecognizer",
    "UkVehicleRecognizer",
    "UkNameRecognizer",
    "UkOrganizationRecognizer",
]
