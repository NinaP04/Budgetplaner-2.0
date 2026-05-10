"""CLI-Ansicht für Kontomenü und Eingabeaufforderungen."""


class AccountView:
    """Zeigt kontobezogene Menüs und Eingabeaufforderungen an."""

    def __init__(self, input_func=input):
        self._input = input_func

    @staticmethod
    def show_account_menu() -> None:
        print("\n\033[01mKonto Menü\033[0m")
        print("1. Kontodaten anzeigen")
        print("2. Vorname ändern")
        print("3. Nachname ändern")
        print("4. E-Mail ändern")
        print("5. Passwort ändern")
        print("6. Lohn hinzufügen")
        print("7. Konto löschen")

    def prompt_choice(self) -> str:
        return self._input("\n\033[34mWähle eine Aktion (0. Zurück): \033[0m")

    def prompt_text(self, label: str) -> str:
        return self._input(f"\033[34m{label}\033[0m").strip()

    def prompt_salary_data(self) -> tuple[str, str]:
        date_str = self._input(
            "\033[34mDatum (DD.MM.YYYY oder '.' für heute): \033[0m").strip()
        amount_str = self._input("\033[34mBetrag in CHF: \033[0m").strip()
        return date_str, amount_str

    def confirm_account_delete(self) -> bool:
        print("\n\033[31mWARNUNG: Dein gesamtes Konto wird gelöscht!\033[0m")
        print(
            "\033[31mAlle Kategorien, Limits und Finanzdaten werden entfernt.\n\033[0m")
        first = self._input(
            "\033[34mBist du sicher? (Y/y zum Bestätigen): \033[0m")
        if first.lower() != "y":
            return False
        second = self._input(
            "\033[34mBitte tippe 'LÖSCHEN' zur endgültigen Bestätigung: \033[0m")
        return second == "LÖSCHEN"

    @staticmethod
    def show_profile(data: dict) -> None:
        print("\n\033[01mKontoinformationen\033[0m")
        print("---------------------------------------------")
        print(f"Vorname:  {data.get('vorname', '-')}")
        print(f"Nachname: {data.get('name', '-')}")
        print(f"E-Mail:   {data.get('email', '-')}")
        print(f"Lohn:     {data.get('lohn', '-')}")
        print("---------------------------------------------\n")

    @staticmethod
    def show_success(message: str) -> None:
        print(f"\n\033[32m{message}\033[0m")

    @staticmethod
    def show_error(message: str) -> None:
        print(f"\n\033[31m{message}\033[0m")
