"""
Hilfsfunktionen-Modul für Budget-Tracker
Enthält Validierungs- und Utility-Klassen
"""

import threading
import os
from datetime import datetime


class BudgetValidator:
    """
    Verantwortlich für Validierungen rund um Budgetdaten
    (Datum, Beträge, Limits).
    """

    MAX_BUDGET_LIMIT = 2000.0

    @staticmethod
    def validiere_datum(datum_str):
        """
        Validiert ob ein Datum im Format DD.MM.YYYY gültig ist.

        Args:
            datum_str (str): Datum als String im Format DD.MM.YYYY

        Returns:
            bool: True wenn Datum gültig ist, sonst False
        """
        try:
            datetime.strptime(datum_str, "%d.%m.%Y")
            return True
        except ValueError:
            return False

    @staticmethod
    def validiere_positiven_betrag(betrag, max_wert=None):
        """
        Validiert ob ein Betrag positiv (>=0) und optional unter einem Maximum liegt.

        Args:
            betrag (float): Zu validierender Betrag
            max_wert (float, optional): Maximaler erlaubter Wert

        Returns:
            bool: True wenn Betrag gültig ist, sonst False
        """
        if betrag < 0:
            print("\n\033[31mFehler: Der Betrag darf nicht negativ sein!\033[0m")
            return False

        if max_wert is not None and betrag > max_wert:
            print(
                f"\n\033[31mFehler: Der Betrag darf maximal "
                f"{max_wert:.2f} CHF betragen!\033[0m"
            )
            return False

        return True


class InaktivitätsManager:
    """
    Verantwortlich für das Erstellen eines input()-Wrappers,
    der bei Inaktivität automatisch ausloggt.
    """

    def __init__(self, timeout, daten_speichern_func):
        """
        Args:
            timeout (int): Sekunden bis zum automatischen Logout
            daten_speichern_func (callable): Funktion zum Speichern der Daten
        """
        self.timeout = timeout
        self.daten_speichern_func = daten_speichern_func

    def _logout(self):
        print("\n\n\033[31mDu wurdest wegen Inaktivität ausgeloggt! \033[0m")
        self.daten_speichern_func()
        os._exit(0)

    def timed_input(self, prompt):
        """
        Input-Funktion mit automatischem Logout bei Inaktivität.

        Args:
            prompt (str): Eingabeaufforderung

        Returns:
            str: Nutzereingabe
        """
        timer = threading.Timer(self.timeout, self._logout)
        timer.start()

        try:
            eingabe = input(prompt)
            timer.cancel()
            return eingabe

        except (KeyboardInterrupt, EOFError):
            timer.cancel()
            print("\n\nEingabe abgebrochen (Ctrl+C/EOF).")
            self.daten_speichern_func()
            raise SystemExit(0)

        except Exception as e:
            timer.cancel()
            print(f"\n\nUnerwarteter Fehler bei der Eingabe: {e}")
            self.daten_speichern_func()
            raise SystemExit(1)


# ---------------------------------------------------------
# Kompatibilitätsfunktionen für andere Module
# ---------------------------------------------------------

MAX_BUDGET_LIMIT = BudgetValidator.MAX_BUDGET_LIMIT


def validiere_datum(datum_str):
    return BudgetValidator.validiere_datum(datum_str)


def validiere_positiven_betrag(betrag, max_wert=None):
    return BudgetValidator.validiere_positiven_betrag(betrag, max_wert)
