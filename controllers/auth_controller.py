"""Controller für Authentifizierung im MVC-Aufbau."""

from typing import Optional

from models.auth_model import AuthModel
from views.auth_view import AuthView


class AuthController:
    """Koordiniert Login- und Passwort-Aktionen zwischen View und Model."""

    def __init__(self, accounts: dict, save_callback, input_func=input):
        self.accounts = accounts
        self._save_callback = save_callback
        self._model = AuthModel()
        self._view = AuthView(input_func)
        self._active_email: Optional[str] = None

    def set_active_user(self, email: str) -> None:
        self._active_email = email

    def _active_user(self) -> Optional[dict]:
        if not self._active_email:
            return None
        return self.accounts.get(self._active_email)

    def login(self) -> Optional[str]:
        self._view.show_message("Bitte gib deine Logindaten ein.", "34")
        email = self._view.prompt_email()

        if email not in self.accounts:
            self._view.show_message(
                "Fuer diese E-Mail existiert kein Konto.", "33")
            if not self._view.ask_create_account():
                self._view.show_message("Okay, bitte erneut versuchen.", "34")
                return None

            self.accounts[email] = self._model.default_user_data(email)
            self._active_email = email
            self._view.show_message(
                "Konto erstellt. Bitte Passwort setzen.", "32")
            self.change_password(force_without_old=True)
            self._save_callback()
            return email

        for _ in range(3):
            password = self._view.prompt_password(allow_reset=True)

            if password.lower() == "f":
                if self.password_reset_flow(email):
                    self._view.show_message("Bitte erneut einloggen.", "34")
                return None

            if self._model.verify_password(
                password, self.accounts[email].get("passwort")
            ):
                self._active_email = email
                self._view.show_message("Erfolgreich eingeloggt.", "32")
                return email

            self._view.show_message("Falsches Passwort.", "31")

        self._view.show_message("Zu viele Fehlversuche.", "31")
        return None

    def password_reset_flow(self, email: str) -> bool:
        self._view.show_message("Passwort zuruecksetzen", "01")
        entered_email = self._view.prompt_email()
        if entered_email != email:
            self._view.show_message(
                "Diese E-Mail ist nicht registriert.", "33")
            return False

        code = self._model.generate_reset_code(email)
        self._view.show_message(
            f"Reset-Code gesendet an {email}. (Debug-Code: {code})", "34")

        if not self._model.verify_reset_code(email, self._view.prompt_reset_code()):
            self._view.show_message("Falscher Reset-Code.", "31")
            return False

        self._active_email = email
        return self.change_password(force_without_old=True)

    def change_password(self, force_without_old: bool = False) -> bool:
        user_data = self._active_user()
        if not user_data:
            self._view.show_message("Kein aktiver Benutzer gesetzt.", "31")
            return False

        if not force_without_old and user_data.get("passwort"):
            current = self._view.prompt_password(allow_reset=False)
            if not self._model.verify_password(current, user_data.get("passwort")):
                self._view.show_message("Ungueltiges Passwort.", "31")
                return False

        self._view.show_password_rules()

        while True:
            pw1, pw2 = self._view.prompt_new_password()

            if pw1 != pw2:
                self._view.show_message(
                    "Passwoerter stimmen nicht ueberein.", "31")
                continue

            valid, error = self._model.validate_password_rules(pw1)
            if not valid:
                self._view.show_message(error, "31")
                continue

            self._model.set_password(user_data, pw1)
            self._save_callback()
            self._view.show_message("Passwort erfolgreich geaendert.", "32")
            return True
