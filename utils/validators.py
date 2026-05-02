"""Validierungsfunktionen für Budgetdaten."""

from datetime import datetime

from utils.constants import MAX_BUDGET_LIMIT


class BudgetValidator:
    """Sammelt Validierungen für Daten und Beträge."""

    @staticmethod
    def validiere_datum(datum_str):
        try:
            datetime.strptime(datum_str, "%d.%m.%Y")
            return True
        except ValueError:
            return False

    @staticmethod
    def validiere_positiven_betrag(betrag, max_wert=None):
        if betrag < 0:
            print(
                "\n\033[31mFehler: Der Betrag darf nicht negativ sein!\033[0m")
            return False

        if max_wert is not None and betrag > max_wert:
            print(
                f"\n\033[31mFehler: Der Betrag darf maximal {max_wert:.2f} CHF betragen!\033[0m"
            )
            return False

        return True


def validiere_datum(datum_str):
    return BudgetValidator.validiere_datum(datum_str)


def validiere_positiven_betrag(betrag, max_wert=None):
    return BudgetValidator.validiere_positiven_betrag(betrag, max_wert)


__all__ = [
    "BudgetValidator",
    "MAX_BUDGET_LIMIT",
    "validiere_datum",
    "validiere_positiven_betrag",
]
