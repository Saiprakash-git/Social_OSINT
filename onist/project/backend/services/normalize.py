from __future__ import annotations
from typing import Optional
import phonenumbers
from email_validator import validate_email, EmailNotValidError

# Email

def normalize_email(email: Optional[str]) -> Optional[str]:
    if not email: return None
    try:
        v = validate_email(email, check_deliverability=False)
        return v.email.lower()
    except EmailNotValidError:
        return None

# Phone to E.164

def normalize_phone(phone: Optional[str], default_region: str = "IN") -> Optional[str]:
    if not phone: return None
    try:
        num = phonenumbers.parse(phone, default_region)
        if not phonenumbers.is_possible_number(num) or not phonenumbers.is_valid_number(num):
            return None
        return phonenumbers.format_number(num, phonenumbers.PhoneNumberFormat.E164)
    except Exception:
        return None

# Name/username simple cleanup

def clean(s: Optional[str]) -> Optional[str]:
    if not s: return None
    return " ".join(str(s).strip().split())