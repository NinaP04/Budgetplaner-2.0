"""CLI-Ansicht für Kontomenü und Eingabeaufforderungen."""


class AccountView:
    """Zeigt kontobezogene Menüs und Eingabeaufforderungen an."""

    def __init__(self, input_func=input):
        self._input = input_func

    @staticmethod
    def show_account_menu() -> None:
        print("\n\033[01mKonto Menue\033[0m")
        print("1. Kontodaten anzeigen")
        print("2. Vorname aendern")
        print("3. Nachname aendern")
        print("4. E-Mail aendern")
        print("5. Passwort aendern")
        print("6. Lohn hinzufuegen")
        print("7. Konto loeschen")

    def prompt_choice(self) -> str:
        return self._input("\n\033[34mWaehle eine Aktion (0. Zurueck): \033[0m")

    def prompt_text(self, label: str) -> str:
        return self._input(f"\033[34m{label}\033[0m").strip()

    def prompt_salary_data(self) -> tuple[str, str]:
        date_str = self._input(
            "\033[34mDatum (DD.MM.YYYY oder '.' fuer heute): \033[0m").strip()
        amount_str = self._input("\033[34mBetrag in CHF: \033[0m").strip()
        return date_str, amount_str

    def confirm_account_delete(self) -> bool:
        print("\n\033[31mWARNUNG: Dein gesamtes Konto wird geloescht!\033[0m")
        print(
            "\033[31mAlle Kategorien, Limits und Finanzdaten werden entfernt.\n\033[0m")
        first = self._input(
            "\033[34mBist du sicher? (Y/y zum Bestaetigen): \033[0m")
        if first.lower() != "y":
            return False
        second = self._input(
            "\033[34mBitte tippe 'LOESCHEN' zur endgueltigen Bestaetigung: \033[0m")
        return second == "LOESCHEN"

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
