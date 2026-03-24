import re
from datetime import datetime
from utils import validiere_datum


# ---------------------------------------------------------
# BudgetEntry – Ein einzelner Eintrag
# ---------------------------------------------------------

class BudgetEntry:
    """
    Repräsentiert einen Budgeteintrag im Format:
    'DD.MM.YYYY - Art - Betrag CHF'
    """

    _PATTERN = re.compile(
        r"^(?P<datum>\d{2}\.\d{2}\.\d{4}) - (?P<art>.+?) - (?P<betrag>-?\d+(?:\.\d+)?) CHF$"
    )

    def __init__(self, datum, art, betrag):
        self.datum = datum
        self.art = art
        self.betrag = float(betrag)

    @classmethod
    def from_string(cls, eintrag_str):
        eintrag_str = eintrag_str.strip()
        match = cls._PATTERN.match(eintrag_str)

        if not match:
            raise ValueError(f"Ungültiges Eintragsformat: '{eintrag_str}'")

        datum = match.group("datum")
        art = match.group("art").strip()
        betrag = float(match.group("betrag"))

        if not validiere_datum(datum):
            raise ValueError(f"Ungültiges Datum: '{datum}'")

        return cls(datum, art, betrag)

    def __str__(self):
        return f"{self.datum} - {self.art} - {self.betrag:.2f} CHF"


# ---------------------------------------------------------
# BudgetCategory – Eine Kategorie mit Einträgen
# ---------------------------------------------------------

class BudgetCategory:
    def __init__(self, name, limit=None):
        self.name = name
        self.entries = []
        self.limit = limit

    def add_entry(self, entry: BudgetEntry):
        self.entries.append(entry)

    def delete_entry(self, index):
        return self.entries.pop(index)

    def total(self):
        return sum(e.betrag for e in self.entries)

    def limit_exceeded(self, new_amount):
        if self.limit is None:
            return False
        return (self.total() + new_amount) > self.limit


# ---------------------------------------------------------
# BudgetManager – Verwaltung aller Kategorien
# ---------------------------------------------------------

class BudgetManager:
    MAX_KATEGORIEN = 7

    def __init__(self):
        self.categories = {}

    def list_categories(self):
        return list(self.categories.values())

    def add_category(self, name):
        if len(self.categories) >= self.MAX_KATEGORIEN:
            raise ValueError("Maximal 7 Kategorien erlaubt.")
        if name in self.categories:
            raise ValueError("Kategorie existiert bereits.")
        self.categories[name] = BudgetCategory(name)

    def rename_category(self, old, new):
        if new in self.categories:
            raise ValueError("Neuer Name existiert bereits.")
        self.categories[new] = self.categories.pop(old)
        self.categories[new].name = new

    def delete_category(self, name):
        del self.categories[name]

    def add_entry(self, cat_name, entry):
        cat = self.categories[cat_name]
        if cat.limit_exceeded(entry.betrag):
            print("\033[31mAchtung: Budgetlimit überschritten!\033[0m")
        cat.add_entry(entry)


# ---------------------------------------------------------
# BudgetUI – Benutzeroberfläche für Kategorien
# ---------------------------------------------------------

class BudgetUI:
    def __init__(self, manager: BudgetManager, timed_input):
        self.manager = manager
        self.timed_input = timed_input

    # ---------------------------------------------------------
    # Hilfsmethoden
    # ---------------------------------------------------------

    def _input_category_name(self):
        while True:
            name = self.timed_input("Name der Kategorie: ").strip()
            if re.match(r'^[A-Za-zÄÖÜäöüß ]+$', name):
                return name
            print("\033[31mUngültiger Name – nur Buchstaben und Leerzeichen erlaubt.\033[0m")

    def _input_entry(self):
        typ = self.timed_input("1=Einnahme, 2=Ausgabe: ").strip()
        if typ not in ("1", "2"):
            print("\033[31mUngültige Auswahl.\033[0m")
            return None

        datum = self.timed_input("Datum (DD.MM.YYYY oder . für heute): ").strip()
        if datum == ".":
            datum = datetime.now().strftime("%d.%m.%Y")
        if not validiere_datum(datum):
            print("\033[31mUngültiges Datum.\033[0m")
            return None

        art = self.timed_input("Art der Kosten: ").strip()
        if not re.match(r'^[A-Za-zÄÖÜäöüß ]+$', art):
            print("\033[31mUngültige Kostenart.\033[0m")
            return None

        try:
            betrag = float(self.timed_input("Betrag in CHF: "))
        except ValueError:
            print("\033[31mUngültiger Betrag.\033[0m")
            return None

        if typ == "2":
            betrag = -betrag

        return BudgetEntry(datum, art, betrag)

    def choose_category(self):
        cats = list(self.manager.categories.keys())

        if not cats:
            print("\033[33mKeine Kategorien vorhanden.\033[0m")
            return None

        print("\n\033[1mKategorien:\033[0m")
        for i, name in enumerate(cats, start=1):
            print(f"{i}. {name}")

        try:
            idx = int(self.timed_input("Nummer wählen: ")) - 1
            if 0 <= idx < len(cats):
                return cats[idx]
        except:
            pass

        print("\033[31mUngültige Auswahl.\033[0m")
        return None

    # ---------------------------------------------------------
    # UI‑Funktionen
    # ---------------------------------------------------------

    def show_categories(self):
        print("\n\033[1mAktuelle Budget-Kategorien:\033[0m")
        for i, cat in enumerate(self.manager.list_categories(), start=1):
            print(f"{i}. {cat.name}")

    def create_category(self):
        try:
            name = self._input_category_name()
            self.manager.add_category(name)
            print(f"\033[32mKategorie '{name}' wurde hinzugefügt.\033[0m")
        except ValueError as e:
            print(f"\033[31m{e}\033[0m")

    def edit_category(self, name):
        """Bearbeitet eine Kategorie, die bereits existiert."""
        if name not in self.manager.categories:
            print("\033[31mKategorie existiert nicht.\033[0m")
            return

        cat = self.manager.categories[name]

        while True:
            print(f"\n\033[1mBearbeiten von '{name}':\033[0m")
            print("1. Namen ändern")
            print("2. Eintrag hinzufügen")
            print("3. Eintrag löschen")
            print("4. Kategorie löschen")
            print("0. Zurück")

            choice = self.timed_input("Auswahl: ").strip()

            if choice == "0":
                return

            if choice == "1":
                new_name = self._input_category_name()
                self.manager.rename_category(name, new_name)
                print("\033[32mKategorie umbenannt.\033[0m")
                return

            elif choice == "2":
                entry = self._input_entry()
                if entry:
                    self.manager.add_entry(name, entry)
                    print("\033[32mEintrag hinzugefügt.\033[0m")

            elif choice == "3":
                if not cat.entries:
                    print("\033[33mKeine Einträge vorhanden.\033[0m")
                    continue

                for i, e in enumerate(cat.entries, start=1):
                    print(f"{i}. {e}")

                try:
                    idx = int(self.timed_input("Nummer löschen: ")) - 1
                    gelöscht = cat.delete_entry(idx)
                    print(f"\033[32mEintrag '{gelöscht}' gelöscht.\033[0m")
                except Exception:
                    print("\033[31mUngültige Auswahl.\033[0m")

            elif choice == "4":
                confirm = self.timed_input("Wirklich löschen? (Y/N): ").lower()
                if confirm == "y":
                    self.manager.delete_category(name)
