"""Controller fuer Authentifizierung im MVC-Aufbau."""

from typing import Optional

from auth import AuthManager


class AuthController:
    """Koordiniert Login- und Passwort-Aktionen zwischen View und Model."""

    def __init__(self, accounts: dict, save_callback):
        self.accounts = accounts
        self._auth_manager = AuthManager({}, save_callback)

    def login(self) -> Optional[str]:
        """Führt den Login-Flow aus und liefert die aktive E-Mail."""
        return self._auth_manager.login(self.accounts)

    def set_active_user(self, email: str) -> None:
        """Bindet den eingeloggten Benutzer an das Auth-Model."""
        self._auth_manager.benutzer_daten = self.accounts[email]

    def change_password(self) -> bool:
        """Leitet Passwortaenderung an das Auth-Model weiter."""
        change_password = getattr(self._auth_manager, "passwort_\u00e4ndern")
        return change_password()

    @property
    def manager(self) -> AuthManager:
        return self._auth_manager
