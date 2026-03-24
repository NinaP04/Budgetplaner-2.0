"""
Finanzkontroll-Modul für Budget-Tracker
Objektorientierte Verwaltung von Budgetlimits
"""

from utils import validiere_positiven_betrag, MAX_BUDGET_LIMIT


class BudgetLimitManager:
    """OOP-Klasse zur Verwaltung von Budgetlimits."""

    def __init__(self, budget_kategorien, budget_limits, timed_input, daten_speichern_func):
        self.budget_kategorien = budget_kategorien
        self.budget_limits = budget_limits
        self.timed_input = timed_input
        self.speichern = daten_speichern_func

    # -------------------------------------------------------------
    def start(self):
        """Startet die Budgetlimit-Verwaltung mit Kategorieauswahl."""
        kategorien_liste = list(self.budget_kategorien.keys())

        print("\n\033[1mBudgetlimite pro Kategorie\033[0m")
        for i, kategorie in enumerate(kategorien_liste, start=1):
            print(f"{i}. {kategorie}")
        print("")

        try:
            index = int(self.timed_input(
                "\033[34mWähle eine Kategorie für die Bearbeitung der Budgetlimite "
                "(0 = Hauptmenü):\033[0m"
            ))

            if index == 0:
                return self.budget_limits

            index -= 1

            if not (0 <= index < len(kategorien_liste)):
                print("\n\033[31mUngültige Auswahl.\033[0m")
                return self.budget_limits

        except ValueError:
            print("\n\033[31mBitte eine gültige Zahl eingeben.\033[0m")
            return self.budget_limits

        gewählte_kategorie = kategorien_liste[index]
        self._budgetlimit_menu(gewählte_kategorie)

        return self.budget_limits

    # -------------------------------------------------------------
    def _budgetlimit_menu(self, kategorie):
        """Menü zur Verwaltung der Budgetlimite für eine Kategorie."""

        while True:
            print(f"\n\033[1mBudgetlimite für '{kategorie}'\033[0m")
            print("1. Anzeigen")
            print("2. Setzen")
            print("3. Ändern")
            print("4. Entfernen")

            auswahl = self.timed_input(
                "\n\033[34mWähle eine Option (0 = Zurück, 1–4): \033[0m")

            if auswahl == "0":
                break

            if auswahl == "1":
                self._anzeigen(kategorie)

            elif auswahl == "2":
                self._setzen(kategorie)

            elif auswahl == "3":
                self._ändern(kategorie)

            elif auswahl == "4":
                self._entfernen(kategorie)

    # -------------------------------------------------------------
    def _anzeigen(self, kategorie):
        limit = self.budget_limits.get(kategorie)
        if limit is not None:
            print(f"\n\033[1mAktuelles Budgetlimit: \033[0m{limit:.2f} CHF\033[0m")
        else:
            print("\n\033[33mKein Budgetlimit gesetzt.\033[0m")

    # -------------------------------------------------------------
    def _setzen(self, kategorie):
        try:
            limit = float(self.timed_input(
                f"\n\033[34mNeues Budgetlimit in CHF (max. {MAX_BUDGET_LIMIT:.2f} CHF):\033[0m"
            ))
            if validiere_positiven_betrag(limit, MAX_BUDGET_LIMIT):
                self.budget_limits[kategorie] = limit
                self.speichern()
                print(f"\n\033[32mBudgetlimite erfolgreich gesetzt: {limit:.2f} CHF\033[0m")

        except ValueError:
            print("\n\033[31mUngültiger Betrag.\033[0m")

    # -------------------------------------------------------------
    def _ändern(self, kategorie):
        if kategorie not in self.budget_limits:
            print("\n\033[33mKein Limit vorhanden.\033[0m")
            return

        try:
            neues_limit = float(self.timed_input(
                f"\n\033[34mNeues Limit in CHF (max. {MAX_BUDGET_LIMIT:.2f} CHF):\033[0m"
            ))
            if validiere_positiven_betrag(neues_limit, MAX_BUDGET_LIMIT):
                self.budget_limits[kategorie] = neues_limit
                self.speichern()
                print(f"\n\033[32mLimit geändert auf {neues_limit:.2f} CHF\033[0m")
        except ValueError:
            print("\n\033[31mUngültiger Betrag.\033[0m")

    # -------------------------------------------------------------
    def _entfernen(self, kategorie):
        if kategorie in self.budget_limits:
            del self.budget_limits[kategorie]
            self.speichern()
            print(f"\n\033[32mLimit entfernt.\033[0m")
        else:
            print("\n\033[33mKein Limit vorhanden.\033[0m")
