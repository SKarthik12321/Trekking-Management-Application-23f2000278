import re


def normalize_phone_number(value):
    """Return a 10-digit Indian phone number, or None when the value is invalid."""
    if value is None:
        return ''

    phone = str(value).strip()
    if not phone:
        return ''
    if not re.fullmatch(r'[0-9+().\-\s]+', phone):
        return None

    digits = re.sub(r'\D', '', phone)
    if len(digits) == 12 and digits.startswith('91'):
        digits = digits[2:]

    return digits if len(digits) == 10 else None
