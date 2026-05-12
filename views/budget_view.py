"""CLI-Ansicht für Budgetkategorien und Einträge."""

import re
from datetime import datetime

from models.budget import BudgetEntry
from utils import validiere_datum


class BudgetView:
    """Zeigt Budgetmenüs an und wandelt Benutzereingaben in Domänenobjekte um."""

    def __init__(self, input_func=input):
        self._input = input_func

    @staticmethod
    def show_categories(names: list[str]) -> None:
        print("\n\033[1mAktuelle Budget-Kategorien:\033[0m")
        if not names:
            print("\033[33mKeine Kategorien vorhanden.\033[0m")
            return

        for idx, name in enumerate(names, start=1):
            print(f"{idx}. {name}")

    def prompt_category_name(self) -> str:
        return self._input("Name der Kategorie: ").strip()

    def choose_category(self, names: list[str], show_list: bool = True):
        if not names:
            print("\033[33mKeine Kategorien vorhanden.\033[0m")
            return None

        if show_list:
            print("\n\033[1mKategorien:\033[0m")
            for idx, name in enumerate(names, start=1):
                print(f"{idx}. {name}")

        try:
            selected = int(self._input("Nummer wählen: ").strip()) - 1
        except ValueError:
            print("\033[31mUngültige Auswahl.\033[0m")
            return None

        if 0 <= selected < len(names):
            return names[selected]

        print("\033[31mUngültige Auswahl.\033[0m")
        return None

    def show_category_edit_menu(self, name: str) -> str:
        print(f"\n\033[1mBearbeiten von '{name}':\033[0m")
        print("1. Namen ändern")
        print("2. Eintrag hinzufügen")
        print("3. Eintrag löschen")
        print("4. Kategorie löschen")
        print("0. Zurück")
        return self._input("Auswahl: ").strip()

    def prompt_entry_type(self) -> str:
        return self._input("1=Einnahme, 2=Ausgabe: ").strip()

    def prompt_entry_date(self) -> str:
        return self._input("Datum (DD.MM.YYYY oder . für heute): ").strip()

    def prompt_entry_art(self) -> str:
        return self._input("Art der Kosten: ").strip()

    def prompt_entry_amount(self) -> str:
        return self._input("Betrag in CHF: ").strip()

    def prompt_delete_entry_index(self) -> str:
        return self._input("Nummer löschen: ").strip()

    def confirm_delete_category(self) -> bool:
        return self._input("Wirklich löschen? (Y/N): ").strip().lower() == "y"

    @staticmethod
    def show_entries(entries: list[BudgetEntry]) -> None:
        for idx, entry in enumerate(entries, start=1):
            print(f"{idx}. {entry}")

    @staticmethod
    def show_success(message: str) -> None:
        print(f"\033[32m{message}\033[0m")

    @staticmethod
    def show_error(message: str) -> None:
        print(f"\033[31m{message}\033[0m")

    @staticmethod
    def validate_category_name(name: str) -> bool:
        return bool(re.match(r"^[A-Za-zÄÖÜäöüß ]+$", name))

    @staticmethod
    def validate_art(art: str) -> bool:
        return bool(re.match(r"^[A-Za-zÄÖÜäöüß ]+$", art))

    @staticmethod
    def build_entry(typ: str, date_str: str, art: str, amount_raw: str):
        if typ not in ("1", "2"):
            return None, "Ungültige Auswahl."

        if date_str == ".":
            date_str = datetime.now().strftime("%d.%m.%Y")

        if not validiere_datum(date_str):
            return None, "Ungültiges Datum."

        if not BudgetView.validate_art(art):
            return None, "Ungültige Kostenart."

        try:
            amount = float(amount_raw)
        except ValueError:
            return None, "Ungültiger Betrag."

        if typ == "2":
            amount = -amount

        return BudgetEntry(date_str, art, amount), ""
