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
