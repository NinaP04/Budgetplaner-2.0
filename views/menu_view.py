"""CLI-Ansicht für Menüs und Standardausgaben."""

from views.formatter import Formatter


class MenuView:
    """Zeigt Navigationsaufforderungen für Anmeldung, Hauptmenü und Konten an."""

    def __init__(self, input_func=input):
        self._input = input_func

    @staticmethod
    def _clean_name_part(value) -> str:
        text = "" if value is None else str(value).strip()
        return "" if text == "0" else text

    def show_main_menu(self, firstname: str, lastname: str) -> str:
        fname = self._clean_name_part(firstname)
        if fname:
            print(Formatter.titel(f"Willkommen {fname}"))
        else:
            print(Formatter.titel("Willkommen"))
        print(Formatter.titel("Kategorien Menü"))
        print("1. Kategorien anzeigen")
        print("2. Kategorie hinzufügen")
        print("3. Kategorie bearbeiten")
        print("4. Budgetlimite setzen")
        print("5. Statistik anzeigen")
        print("6. Konto verwalten")
        print("7. Logout")
        return self._input(Formatter.eingabeaufforderung("Wähle eine Aktion: "))

    @staticmethod
    def show_error(text: str) -> None:
        print(Formatter.fehler(text))

    @staticmethod
    def show_success(text: str) -> None:
        print(Formatter.erfolg(text))
