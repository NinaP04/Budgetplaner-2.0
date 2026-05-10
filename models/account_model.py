"""Domänenmodell für Profil- und Lohnverwaltung."""

from datetime import datetime
from typing import Optional, Tuple


class AccountModel:
    """Reine Modelllogik für Änderungen an Kontodaten."""

    @staticmethod
    def ensure_salary_list(user_data: dict) -> None:
        if "lohn" not in user_data:
            user_data["lohn"] = []

    @staticmethod
    def profile_data(user_data: dict) -> dict:
        return {
            "vorname": user_data.get("vorname", "-"),
            "name": user_data.get("name", "-"),
            "email": user_data.get("email", "-"),
            "lohn": user_data.get("lohn", []),
        }

    @staticmethod
    def change_firstname(user_data: dict, value: str) -> Tuple[bool, str]:
        value = value.strip()
        if not value:
            return False, "Vorname darf nicht leer sein."
        user_data["vorname"] = value
        return True, "Vorname erfolgreich geändert."

    @staticmethod
    def change_lastname(user_data: dict, value: str) -> Tuple[bool, str]:
        value = value.strip()
        if not value:
            return False, "Nachname darf nicht leer sein."
        user_data["name"] = value
        return True, "Nachname erfolgreich geändert."

    @staticmethod
    def change_email(accounts: dict, current_email: str, new_email: str) -> Tuple[bool, str, Optional[str]]:
        new_email = new_email.strip().lower()
        if not new_email:
            return False, "E-Mail darf nicht leer sein.", None
        if new_email in accounts:
            return False, "Diese E-Mail existiert bereits.", None

        user_data = accounts[current_email]
        user_data["email"] = new_email
        del accounts[current_email]
        accounts[new_email] = user_data
        return True, "E-Mail erfolgreich geändert.", new_email

    @staticmethod
    def add_salary(user_data: dict, date_str: str, amount_raw: str) -> Tuple[bool, str]:
        date_str = date_str.strip()
        if date_str == ".":
            date_str = datetime.now().strftime("%d.%m.%Y")

        try:
            amount = float(amount_raw)
        except ValueError:
            return False, "Ungültiger Betrag."

        if amount <= 0:
            return False, "Der Betrag muss positiv und grösser als 0 sein."

        entry = f"{date_str} - Lohn - {amount} CHF"
        user_data.setdefault("lohn", []).append(entry)
        return True, f"Lohn '{entry}' erfolgreich gespeichert."

    @staticmethod
    def delete_account(accounts: dict, email: str) -> None:
        if email in accounts:
            del accounts[email]
