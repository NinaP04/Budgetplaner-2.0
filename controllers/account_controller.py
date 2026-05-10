"""Controller für die Kontoverwaltung im MVC-Aufbau."""

from typing import Callable, Optional, Tuple

from models.account_model import AccountModel
from views.account_view import AccountView


class AccountController:
    """Steuert das Kontomenü und delegiert Datenänderungen an das Modell."""

    def __init__(
            self,
            accounts: dict,
            save_callback,
            timed_input: Callable[[str], str] = input,
    ):
        self.accounts = accounts
        self._save_callback = save_callback
        self._view = AccountView(timed_input)
        self._model = AccountModel()
        self.current_user_email: Optional[str] = None

    def set_active_user(self, email: str) -> None:
        self.current_user_email = email
        self._model.ensure_salary_list(self.accounts[email])

    def _active_user(self) -> dict:
        if not self.current_user_email or self.current_user_email not in self.accounts:
            raise RuntimeError(
                "Kein aktiver Benutzer für AccountController gesetzt.")
        return self.accounts[self.current_user_email]

    def menu_loop(self, auth_controller) -> Tuple[Optional[str], bool]:
        """Führt das Kontomenü aus.

        Returns:
                tuple(new_email_or_none, logout)
        """
        user_data = self._active_user()

        while True:
            self._view.show_account_menu()
            choice = self._view.prompt_choice()

            if choice == "0":
                return self.current_user_email, False
            if choice == "1":
                self._view.show_profile(self._model.profile_data(user_data))
                continue
            if choice == "2":
                value = self._view.prompt_text("Neuer Vorname: ")
                ok, message = self._model.change_firstname(user_data, value)
                if ok:
                    self._save_callback()
                    self._view.show_success(message)
                else:
                    self._view.show_error(message)
                continue
            if choice == "3":
                value = self._view.prompt_text("Neuer Nachname: ")
                ok, message = self._model.change_lastname(user_data, value)
                if ok:
                    self._save_callback()
                    self._view.show_success(message)
                else:
                    self._view.show_error(message)
                continue
            if choice == "4":
                new_email = self._view.prompt_text("Neue E-Mail: ")
                ok, message, updated_email = self._model.change_email(
                    self.accounts,
                    self.current_user_email,
                    new_email,
                )
                if ok and updated_email:
                    self.current_user_email = updated_email
                    user_data = self.accounts[updated_email]
                    auth_controller.set_active_user(updated_email)
                    self._save_callback()
                    self._view.show_success(message)
                else:
                    self._view.show_error(message)
                continue
            if choice == "5":
                auth_controller.change_password()
                continue
            if choice == "6":
                date_str, amount_str = self._view.prompt_salary_data()
                ok, message = self._model.add_salary(
                    user_data, date_str, amount_str)
                if ok:
                    self._save_callback()
                    self._view.show_success(message)
                else:
                    self._view.show_error(message)
                continue
            if choice == "7":
                if self._view.confirm_account_delete():
                    self._model.delete_account(
                        self.accounts, self.current_user_email)
                    self._save_callback()
                    self._view.show_success("Konto erfolgreich geloescht.")
                    return None, True
                self._view.show_error("Loeschen abgebrochen.")
                continue

            self._view.show_error("Ungueltige Eingabe.")
