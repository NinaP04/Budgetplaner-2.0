"""Domänenmodell für Passwort- und Login-Abläufe."""

import base64
import random
import string
from typing import Dict, Optional, Tuple

import bcrypt


class AuthModel:
    """Reine Modelllogik für Authentifizierung und Passwortverwaltung."""

    def __init__(self) -> None:
        self._reset_codes: Dict[str, str] = {}

    @staticmethod
    def hash_password(password: str) -> str:
        salt = bcrypt.gensalt(rounds=12)
        hashed = bcrypt.hashpw(password.encode("utf-8"), salt)
        return base64.b64encode(hashed).decode("utf-8")

    @staticmethod
    def verify_password(password: str, hashed_password: Optional[str]) -> bool:
        if not hashed_password:
            return False

        try:
            hashed_bytes = base64.b64decode(hashed_password.encode("utf-8"))
            return bcrypt.checkpw(password.encode("utf-8"), hashed_bytes)
        except Exception:
            return False

    @staticmethod
    def validate_password_rules(password: str) -> Tuple[bool, str]:
        special = "!@#%?&*"

        if len(password) < 8:
            return False, "Mindestens 8 Zeichen."
        if not any(c.isupper() for c in password):
            return False, "Mindestens 1 Grossbuchstabe."
        if not any(c.islower() for c in password):
            return False, "Mindestens 1 Kleinbuchstabe."
        if not any(c.isdigit() for c in password):
            return False, "Mindestens 1 Zahl."
        if not any(c in special for c in password):
            return False, "Mindestens 1 Sonderzeichen (!@#%?&*)."

        return True, ""

    def set_password(self, user_data: dict, password: str) -> None:
        user_data["passwort"] = self.hash_password(password)

    @staticmethod
    def default_user_data(email: str) -> dict:
        return {
            "email": email,
            "vorname": "",
            "name": "",
            "passwort": None,
            "budget_kategorien": {
                "Haushalt": [],
                "Freizeit": [],
            },
            "budget_limits": {
                "Haushalt": 500,
                "Freizeit": 300,
            },
            "lohn": [],
        }

    def generate_reset_code(self, email: str) -> str:
        code = "".join(random.choices(string.digits, k=6))
        self._reset_codes[email] = code
        return code

    def verify_reset_code(self, email: str, code: str) -> bool:
        return self._reset_codes.get(email) == code
