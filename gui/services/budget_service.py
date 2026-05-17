"""Budget-Service: Adapter von der NiceGUI-Oberfläche zu den Budget-Modellen.

Liest und schreibt dieselbe JSON-Datei wie die CLI, sodass beide Ansichten
eine gemeinsame Datenquelle nutzen.
"""

import re
from datetime import datetime
from typing import Optional

from models.budget import BudgetEntry
from models.data_storage import DataHandler
from utils import MAX_BUDGET_LIMIT, validiere_datum


_NAME_RE = re.compile(r"^[A-Za-zÄÖÜäöüß ]+$")
MAX_KATEGORIEN = 7


class BudgetService:
    def __init__(self) -> None:
        self._dh = DataHandler()

    def _user(self, email: str) -> Optional[dict]:
        return self._dh.accounts.get(email)

    def list_categories(self, email: str) -> list[dict]:
        user = self._user(email)
        if not user:
            return []
        kategorien = user.get('budget_kategorien', {}) or {}
        limits = user.get('budget_limits', {}) or {}

        result: list[dict] = []
        for name, eintraege in kategorien.items():
            parsed = []
            # Index wird mitgegeben, damit das UI den richtigen Eintrag
            # zum Bearbeiten/Löschen referenzieren kann.
            for idx, s in enumerate(eintraege):
                try:
                    e = BudgetEntry.from_string(s)
                    parsed.append({
                        'index': idx,
                        'datum': e.datum,
                        'art': e.art,
                        'betrag': e.betrag,
                    })
                except ValueError:
                    continue
            spent = sum(p['betrag'] for p in parsed)
            result.append({
                'name': name,
                'limit': limits.get(name),
                'spent': spent,
                'entries': parsed,
            })
        return result

    def add_category(self, email: str, name: str, limit: Optional[float] = None):
        name = (name or '').strip()
        if not _NAME_RE.match(name):
            return False, 'Ungültiger Name — nur Buchstaben und Leerzeichen erlaubt.'

        user = self._user(email)
        if user is None:
            return False, 'Benutzer nicht gefunden.'

        kategorien = user.setdefault('budget_kategorien', {})
        if name in kategorien:
            return False, 'Kategorie existiert bereits.'
        if len(kategorien) >= MAX_KATEGORIEN:
            return False, f'Maximal {MAX_KATEGORIEN} Kategorien erlaubt.'

        kategorien[name] = []

        if limit is not None:
            ok, err = self._apply_limit(user, name, limit)
            if not ok:
                del kategorien[name]
                return False, err

        self._dh.speichern()
        return True, 'Kategorie hinzugefügt.'

    def add_income(self, email: str, datum: str, betrag: float):
        user = self._user(email)
        if user is None:
            return False, 'Benutzer nicht gefunden.'
        datum = (datum or '').strip()
        if not validiere_datum(datum):
            return False, 'Ungültiges Datum (Format: DD.MM.YYYY).'
        try:
            value = float(betrag)
        except (TypeError, ValueError):
            return False, 'Ungültiger Betrag.'
        if value <= 0:
            return False, 'Betrag muss grösser als 0 sein.'
        entry = f"{datum} - Lohn - {value} CHF"
        user.setdefault('lohn', []).append(entry)
        self._dh.speichern()
        return True, 'Einnahme gespeichert.'

    def list_transactions(self, email: str) -> list[dict]:
        user = self._user(email)
        if not user:
            return []
        transactions: list[dict] = []
        for entry_str in user.get('lohn', []):
            parts = entry_str.split(' - ')
            if len(parts) == 3:
                transactions.append({
                    'datum': parts[0].strip(),
                    'art': parts[1].strip(),
                    'kategorie': 'Einnahme',
                    'betrag': float(parts[2].replace('CHF', '').strip()),
                    'typ': 'einnahme',
                })
        for cat_name, entries in (user.get('budget_kategorien') or {}).items():
            for entry_str in entries:
                parts = entry_str.split(' - ')
                if len(parts) == 3:
                    transactions.append({
                        'datum': parts[0].strip(),
                        'art': parts[1].strip(),
                        'kategorie': cat_name,
                        'betrag': float(parts[2].replace('CHF', '').strip()),
                        'typ': 'ausgabe',
                    })
        transactions.sort(
            key=lambda t: datetime.strptime(t['datum'], '%d.%m.%Y'),
            reverse=True,
        )
        return transactions

    def add_entry(self, email: str, category: str, datum: str, art: str, betrag: float):
        user = self._user(email)
        if user is None:
            return False, 'Benutzer nicht gefunden.'
        kategorien = user.get('budget_kategorien', {})
        if category not in kategorien:
            return False, 'Kategorie nicht gefunden.'
        datum = (datum or '').strip()
        if not validiere_datum(datum):
            return False, 'Ungültiges Datum (Format: DD.MM.YYYY).'
        art = (art or '').strip()
        if not art:
            return False, 'Name darf nicht leer sein.'
        try:
            value = float(betrag)
        except (TypeError, ValueError):
            return False, 'Ungültiger Betrag.'
        if value <= 0:
            return False, 'Betrag muss grösser als 0 sein.'
        entry = BudgetEntry(datum, art, value)
        kategorien[category].append(str(entry))
        self._dh.speichern()
        return True, 'Eintrag hinzugefügt.'

    # ---------------------------------------------------------
    # NEU: Eintrag löschen
    # ---------------------------------------------------------
    def delete_entry(self, email: str, category: str, index: int):
        user = self._user(email)
        if user is None:
            return False, 'Benutzer nicht gefunden.'
        kategorien = user.get('budget_kategorien', {})
        if category not in kategorien:
            return False, 'Kategorie nicht gefunden.'
        entries = kategorien[category]
        if index < 0 or index >= len(entries):
            return False, 'Eintrag nicht gefunden.'
        del entries[index]
        self._dh.speichern()
        return True, 'Eintrag gelöscht.'

    # ---------------------------------------------------------
    # NEU: Eintrag bearbeiten
    # ---------------------------------------------------------
    def update_entry(
        self,
        email: str,
        category: str,
        index: int,
        datum: str,
        art: str,
        betrag: float,
    ):
        user = self._user(email)
        if user is None:
            return False, 'Benutzer nicht gefunden.'
        kategorien = user.get('budget_kategorien', {})
        if category not in kategorien:
            return False, 'Kategorie nicht gefunden.'
        entries = kategorien[category]
        if index < 0 or index >= len(entries):
            return False, 'Eintrag nicht gefunden.'

        datum = (datum or '').strip()
        if not validiere_datum(datum):
            return False, 'Ungültiges Datum (Format: DD.MM.YYYY).'
        art = (art or '').strip()
        if not art:
            return False, 'Name darf nicht leer sein.'
        try:
            value = float(betrag)
        except (TypeError, ValueError):
            return False, 'Ungültiger Betrag.'
        if value <= 0:
            return False, 'Betrag muss grösser als 0 sein.'

        entries[index] = str(BudgetEntry(datum, art, value))
        self._dh.speichern()
        return True, 'Eintrag aktualisiert.'

    def delete_category(self, email: str, name: str):
        user = self._user(email)
        if user is None:
            return False, 'Benutzer nicht gefunden.'

        kategorien = user.get('budget_kategorien', {})
        if name not in kategorien:
            return False, 'Kategorie nicht gefunden.'

        del kategorien[name]
        limits = user.get('budget_limits', {})
        limits.pop(name, None)

        self._dh.speichern()
        return True, 'Kategorie gelöscht.'

    def set_limit(self, email: str, name: str, amount: float):
        user = self._user(email)
        if user is None:
            return False, 'Benutzer nicht gefunden.'
        if name not in user.get('budget_kategorien', {}):
            return False, 'Kategorie nicht gefunden.'

        ok, err = self._apply_limit(user, name, amount)
        if not ok:
            return False, err

        self._dh.speichern()
        return True, 'Limit gesetzt.'

    @staticmethod
    def _apply_limit(user: dict, name: str, amount: float):
        try:
            value = float(amount)
        except (TypeError, ValueError):
            return False, 'Ungültiger Betrag.'
        if value <= 0:
            return False, 'Limit muss grösser als 0 sein.'
        if value > MAX_BUDGET_LIMIT:
            return False, f'Limit darf max. {MAX_BUDGET_LIMIT:.2f} CHF betragen.'

        user.setdefault('budget_limits', {})[name] = value
        return True, ''


_budget_service: Optional[BudgetService] = None


def get_budget_service() -> BudgetService:
    global _budget_service
    if _budget_service is None:
        _budget_service = BudgetService()
    return _budget_service
