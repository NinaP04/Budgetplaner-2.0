"""Account service: adapter for profile management in the NiceGUI UI."""

from typing import Optional

from models.account_model import AccountModel
from models.auth_model import AuthModel
from models.data_storage import DataHandler


class AccountService:
    def __init__(self) -> None:
        self._dh = DataHandler()
        self._model = AccountModel()
        self._auth = AuthModel()

    def get_profile(self, email: str) -> dict:
        user = self._dh.accounts.get(email, {})
        return self._model.profile_data(user)

    def update_profile(self, email: str, vorname: str, name: str):
        user = self._dh.accounts.get(email)
        if user is None:
            return False, "Benutzer nicht gefunden."

        ok, msg = self._model.change_firstname(user, vorname)
        if not ok:
            return False, msg

        ok, msg = self._model.change_lastname(user, name)
        if not ok:
            return False, msg

        self._dh.speichern()
        return True, "Profil aktualisiert."

    def change_password(self, email: str, current_password: str, new_password: str):
        user = self._dh.accounts.get(email)
        if user is None:
            return False, "Benutzer nicht gefunden."
        if not self._auth.verify_password(current_password, user.get("passwort")):
            return False, "Aktuelles Passwort ist falsch."
        ok, msg = self._auth.validate_password_rules(new_password)
        if not ok:
            return False, msg
        self._auth.set_password(user, new_password)
        self._dh.speichern()
        return True, "Passwort erfolgreich geändert."

    def change_email(self, current_email: str, new_email: str):
        ok, msg, updated_email = self._model.change_email(
            self._dh.accounts, current_email, new_email
        )
        if ok:
            self._dh.speichern()
        return ok, msg, updated_email


_account_service: Optional[AccountService] = None


def get_account_service() -> AccountService:
    global _account_service
    if _account_service is None:
        _account_service = AccountService()
    return _account_service
