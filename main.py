from data_handler import DataHandler
from auth import AuthManager
from finance_control import BudgetLimitManager
from statistic import BudgetData, StatisticMenu
from utils import InaktivitätsManager
from account_manager import AccountManager
from category_manager import BudgetManager, BudgetUI, BudgetEntry


class BudgetSystem:
    """
    Zentrale Klasse, die alle Daten, das Menü und die Logik kapselt.
    Vollständig OOP-konform.
    """

    def __init__(self):

        self.data = DataHandler()
        self.accounts = self.data.accounts
        self.current_user_email = None

        self.benutzer_daten = None

        self.inaktivitäts_manager = InaktivitätsManager(1200, self.daten_speichern)
        self.timed_input = self.inaktivitäts_manager.timed_input

        self.auth = None
        self.account = None

        self.budget_manager = BudgetManager()
        self.budget_ui = BudgetUI(self.budget_manager, self.timed_input)

    # -------------------------------------------------------------
    def daten_speichern(self):
        self.data.speichern()

    # -------------------------------------------------------------
    def menü(self):
        while True:
            print(f"\n\033[01mWillkommen {self.benutzer_daten.get('vorname', '')} {self.benutzer_daten.get('name', '')}\033[0m")
            print("\n\033[01mKategorien Menü\033[0m")
            print("1. Kategorien anzeigen")
            print("2. Kategorie hinzufügen")
            print("3. Kategorie bearbeiten")
            print("4. Budgetlimite setzen")
            print("5. Statistik anzeigen")
            print("6. Konto verwalten")
            print("7. Logout")

            auswahl = self.timed_input("\n\033[34mWähle eine Aktion: \033[0m")

            match auswahl:
                case "1":
                    self.budget_ui.show_categories()

                case "2":
                    self.budget_ui.create_category()
                    self.benutzer_daten["budget_kategorien"] = self._export_categories()
                    self.daten_speichern()

                case "3":
                    self._edit_category_flow()

                case "4":
                    manager = BudgetLimitManager(
                        self._export_categories(),
                        self.benutzer_daten.get("budget_limits", {}),
                        self.timed_input,
                        self.daten_speichern
                    )
                    manager.start()

                case "5":
                    data = BudgetData(
                        self._export_categories(),
                        self.benutzer_daten.get("budget_limits", {})
                    )
                    menu = StatisticMenu(data, self.timed_input)
                    menu.start()

                case "6":
                    result = self.konto_menü()
                    if result == "logout":
                        return "logout"

                case "7":
                    print("\n\033[32mDu wurdest erfolgreich ausgeloggt.\n\033[0m")
                    return "logout"

                case _:
                    print("\n\033[31mAchtung: Ungültige Eingabe!\n")

    # -------------------------------------------------------------
    def _edit_category_flow(self):
        """Kategorie bearbeiten – jetzt korrekt per Nummernauswahl."""
        name = self.budget_ui.choose_category()
        if not name:
            return

        self.budget_ui.edit_category(name)

        self.benutzer_daten["budget_kategorien"] = self._export_categories()
        self.daten_speichern()

    # -------------------------------------------------------------
    def _export_categories(self):
        export = {}
        for name, cat in self.budget_manager.categories.items():
            export[name] = [str(e) for e in cat.entries]
        return export

    # -------------------------------------------------------------
    def konto_menü(self):
        while True:
            print("\n\033[01mKonto Menü\033[0m")
            print("1. Kontodaten anzeigen")
            print("2. Vorname ändern")
            print("3. Nachname ändern")
            print("4. E-Mail ändern")
            print("5. Passwort ändern")
            print("6. Lohn hinzufügen")
            print("7. Konto löschen")

            auswahl = self.timed_input("\n\033[34mWähle eine Aktion (0. Zurück): \033[0m")

            match auswahl:
                case "0":
                    return

                case "1":
                    self.account.anzeigen()

                case "2":
                    self.account.vorname_ändern()

                case "3":
                    self.account.nachname_ändern()

                case "4":
                    if self.account.email_ändern():
                        self.current_user_email = self.account.current_user_email
                        self.benutzer_daten = self.accounts[self.current_user_email]

                case "5":
                    self.auth.passwort_ändern()

                case "6":
                    self.account.lohn_hinzufügen()

                case "7":
                    if self.account.konto_löschen():
                        return "logout"

                case _:
                    print("\n\033[31mUngültige Eingabe. \033[0m")

    # -------------------------------------------------------------
    def start(self):
        while True:
            self.auth = AuthManager({}, self.daten_speichern)

            email = self.auth.login(self.accounts)
            if not email:
                continue

            self.current_user_email = email
            self.benutzer_daten = self.accounts[email]

            self.auth.benutzer_daten = self.benutzer_daten

            self._import_categories()

            self.account = AccountManager(self.accounts, email, self.daten_speichern)

            result = self.menü()

            if result == "logout":
                continue

            self.data.speichern()

    # -------------------------------------------------------------
    def _import_categories(self):
        self.budget_manager = BudgetManager()
        self.budget_ui = BudgetUI(self.budget_manager, self.timed_input)

        gespeicherte = self.benutzer_daten.get("budget_kategorien", {})

        for name, einträge in gespeicherte.items():
            self.budget_manager.add_category(name)
            for e in einträge:
                self.budget_manager.add_entry(name, BudgetEntry.from_string(e))


def main():
    system = BudgetSystem()
    system.start()


if __name__ == "__main__":
    main()
