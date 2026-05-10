"""Phone-number metadata: country, region, carrier, timezones, validity.

Powered entirely by the `phonenumbers` library (offline data set).
"""

from __future__ import annotations

from typing import Any

import phonenumbers
from phonenumbers import PhoneNumberType, carrier, geocoder, timezone

_TYPE_NAMES = {value: name for name, value in vars(PhoneNumberType).items() if isinstance(value, int)}


def run(number: str, default_region: str | None = None) -> dict[str, Any]:
    number = (number or "").strip()
    if not number:
        return {"query": number, "error": "Provide a phone number (E.164 like +14155552671)."}

    try:
        parsed = phonenumbers.parse(number, default_region)
    except phonenumbers.NumberParseException as exc:
        return {"query": number, "error": f"Could not parse number: {exc}"}

    valid = phonenumbers.is_valid_number(parsed)
    return {
        "query": number,
        "is_valid": valid,
        "is_possible": phonenumbers.is_possible_number(parsed),
        "country_code": parsed.country_code,
        "national_number": parsed.national_number,
        "e164": phonenumbers.format_number(parsed, phonenumbers.PhoneNumberFormat.E164),
        "international": phonenumbers.format_number(
            parsed, phonenumbers.PhoneNumberFormat.INTERNATIONAL
        ),
        "national": phonenumbers.format_number(parsed, phonenumbers.PhoneNumberFormat.NATIONAL),
        "region": phonenumbers.region_code_for_number(parsed),
        "location": geocoder.description_for_number(parsed, "en"),
        "carrier": carrier.name_for_number(parsed, "en"),
        "timezones": list(timezone.time_zones_for_number(parsed)),
        "type": _TYPE_NAMES.get(phonenumbers.number_type(parsed), "UNKNOWN"),
    }
