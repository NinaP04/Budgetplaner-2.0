"""CLI-View für Menüs und Standardausgaben."""

from views.formatter import Formatter


class MenuView:
    """Renders login, main and account navigation prompts."""

    def __init__(self, input_func=input):
        self._input = input_func

    def show_main_menu(self, firstname: str, lastname: str) -> str:
        print(Formatter.titel(f"Willkommen {firstname} {lastname}"))
        print(Formatter.titel("Kategorien Menue"))
        print("1. Kategorien anzeigen")
        print("2. Kategorie hinzufuegen")
        print("3. Kategorie bearbeiten")
        print("4. Budgetlimite setzen")
        print("5. Statistik anzeigen")
        print("6. Konto verwalten")
        print("7. Logout")
        return self._input(Formatter.eingabeaufforderung("Waehle eine Aktion: "))

    @staticmethod
    def show_error(text: str) -> None:
        print(Formatter.fehler(text))

    @staticmethod
    def show_success(text: str) -> None:
        print(Formatter.erfolg(text))
