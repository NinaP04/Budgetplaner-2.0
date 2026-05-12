"""Auth service: thin adapter from the NiceGUI UI to models/.

Delegates hashing, validation, and persistence to the existing MVC
models so the CLI and the GUI share one source of truth and one JSON file.
"""

from typing import Optional

from models.auth_model import AuthModel
from models.data_storage import DataHandler


class AuthService:
    def __init__(self) -> None:
        self._dh = DataHandler()
        self._model = AuthModel()

    @property
    def accounts(self) -> dict:
        return self._dh.accounts

    def login_user(self, email: str, password: str):
        email = (email or '').strip().lower()
        if not email or not password:
            return False, 'Bitte E-Mail und Passwort eingeben.', None

        user = self.accounts.get(email)
        if not user or not self._model.verify_password(password, user.get('passwort')):
            return False, 'Ungültige E-Mail oder Passwort.', None

        return True, 'Login erfolgreich!', {
            'email': user['email'],
            'vorname': user.get('vorname', ''),
            'name': user.get('name', ''),
        }

    def register_user(self, vorname: str, name: str, email: str, password: str):
        vorname = (vorname or '').strip()
        name = (name or '').strip()
        email = (email or '').strip().lower()

        if not all([vorname, name, email, password]):
            return False, 'Alle Felder müssen ausgefüllt sein.'
        if email in self.accounts:
            return False, 'Diese E-Mail-Adresse ist bereits registriert.'

        ok, err = self._model.validate_password_rules(password)
        if not ok:
            return False, err

        user = self._model.default_user_data(email)
        user['vorname'] = vorname
        user['name'] = name
        self._model.set_password(user, password)

        self.accounts[email] = user
        self._dh.speichern()
        return True, 'Registrierung erfolgreich!'

    def request_password_reset(self, email: str):
        email = (email or '').strip().lower()
        if email not in self.accounts:
            return False, 'Diese E-Mail ist nicht registriert.', None
        code = self._model.generate_reset_code(email)
        return True, 'Reset-Code generiert.', code

    def confirm_password_reset(self, email: str, code: str, new_password: str):
        email = (email or '').strip().lower()
        user = self.accounts.get(email)
        if not user:
            return False, 'Diese E-Mail ist nicht registriert.'
        if not self._model.verify_reset_code(email, code):
            return False, 'Falscher Reset-Code.'
        ok, err = self._model.validate_password_rules(new_password)
        if not ok:
            return False, err
        self._model.set_password(user, new_password)
        self._dh.speichern()
        return True, 'Passwort erfolgreich geändert.'


_auth_service: Optional[AuthService] = None


def get_auth_service() -> AuthService:
    global _auth_service
    if _auth_service is None:
        _auth_service = AuthService()
    return _auth_service
