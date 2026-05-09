"""Controller fuer Kontoverwaltung im MVC-Aufbau."""

from typing import Callable, Optional, Tuple

from account_manager import AccountManager


class AccountController:
    """Steuert Kontomenue und delegiert Datenaenderungen an das Model."""

    def __init__(
            self,
            accounts: dict,
            save_callback,
            timed_input: Callable[[str], str] = input,
    ):
        self.accounts = accounts
        self._save_callback = save_callback
        self._timed_input = timed_input
        self.current_user_email: Optional[str] = None
        self._account_manager: Optional[AccountManager] = None

    def set_active_user(self, email: str) -> None:
        self.current_user_email = email
        self._account_manager = AccountManager(
            self.accounts, email, self._save_callback)

    def _manager(self) -> AccountManager:
        if self._account_manager is None:
            raise RuntimeError(
                "Kein aktiver Benutzer fuer AccountController gesetzt.")
        return self._account_manager

    def menu_loop(self, auth_controller) -> Tuple[Optional[str], bool]:
        """Fuehrt das Konto-Menue aus.

        Returns:
                tuple(new_email_or_none, logout)
        """
        manager = self._manager()

        while True:
            print("\n\033[01mKonto Menue\033[0m")
            print("1. Kontodaten anzeigen")
            print("2. Vorname aendern")
            print("3. Nachname aendern")
            print("4. E-Mail aendern")
            print("5. Passwort aendern")
            print("6. Lohn hinzufuegen")
            print("7. Konto loeschen")

            choice = self._timed_input(
                "\n\033[34mWaehle eine Aktion (0. Zurueck): \033[0m")

            if choice == "0":
                return self.current_user_email, False
            if choice == "1":
                manager.anzeigen()
                continue
            if choice == "2":
                change_firstname = getattr(manager, "vorname_\u00e4ndern")
                change_firstname()
                continue
            if choice == "3":
                change_lastname = getattr(manager, "nachname_\u00e4ndern")
                change_lastname()
                continue
            if choice == "4":
                change_email = getattr(manager, "email_\u00e4ndern")
                if change_email():
                    self.current_user_email = manager.current_user_email
                    auth_controller.set_active_user(self.current_user_email)
                continue
            if choice == "5":
                auth_controller.change_password()
                continue
            if choice == "6":
                add_salary = getattr(manager, "lohn_hinzuf\u00fcgen")
                add_salary()
                continue
            if choice == "7":
                delete_account = getattr(manager, "konto_l\u00f6schen")
                if delete_account():
                    return None, True
                continue

            print("\n\033[31mUngueltige Eingabe.\033[0m")
