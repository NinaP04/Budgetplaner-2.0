"""Controller für Budgetfunktionen im MVC-Aufbau."""

from typing import Callable

from models.budget import BudgetEntry, BudgetManager
from models.finance import BudgetData
from utils import MAX_BUDGET_LIMIT, validiere_positiven_betrag
from views.budget_view import BudgetView
from views.statistics_view import StatisticsView


class BudgetController:
    """Koordiniert Budget-Workflows zwischen Modellen und CLI-Ausgabe."""

    def __init__(self, timed_input: Callable[[str], str], save_callback):
        self._timed_input = timed_input
        self._save_callback = save_callback
        self._budget_manager = BudgetManager()
        self._view = BudgetView(self._timed_input)
        self._stats_view = StatisticsView(self._timed_input)

    def load_from_user_data(self, user_data: dict) -> None:
        """Importiert gespeicherte Kategorien in das interne Budget-Modell."""
        self._budget_manager = BudgetManager()

        gespeicherte_kategorien = user_data.get("budget_kategorien", {})
        for name, einträge in gespeicherte_kategorien.items():
            self._budget_manager.add_category(name)
            for eintrag in einträge:
                self._budget_manager.add_entry(
                    name, BudgetEntry.from_string(eintrag))

    def _choose_category(self):
        names = list(self._budget_manager.categories.keys())
        return self._view.choose_category(names)

    def _export_categories(self) -> dict:
        export = {}
        for name, category in self._budget_manager.categories.items():
            export[name] = [str(entry) for entry in category.entries]
        return export

    def _persist_categories(self, user_data: dict) -> None:
        user_data["budget_kategorien"] = self._export_categories()
        self._save_callback()

    def _edit_category_flow(self, user_data: dict) -> None:
        name = self._choose_category()
        if not name:
            return

        while True:
            choice = self._view.show_category_edit_menu(name)
            category = self._budget_manager.categories.get(name)

            if choice == "0":
                return

            if choice == "1":
                new_name = self._view.prompt_category_name()
                if not self._view.validate_category_name(new_name):
                    self._view.show_error(
                        "Ungültiger Name - nur Buchstaben und Leerzeichen erlaubt.")
                    continue
                try:
                    self._budget_manager.rename_category(name, new_name)
                    name = new_name
                    self._persist_categories(user_data)
                    self._view.show_success("Kategorie umbenannt.")
                except ValueError as error:
                    self._view.show_error(str(error))
                continue

            if choice == "2":
                typ = self._view.prompt_entry_type()
                date_str = self._view.prompt_entry_date()
                art = self._view.prompt_entry_art()
                amount = self._view.prompt_entry_amount()
                entry, error = self._view.build_entry(
                    typ, date_str, art, amount)
                if not entry:
                    self._view.show_error(error)
                    continue

                if category and category.limit_exceeded(entry.betrag):
                    self._view.show_error(
                        "Achtung: Budgetlimit ueberschritten!")

                self._budget_manager.add_entry(name, entry)
                self._persist_categories(user_data)
                self._view.show_success("Eintrag hinzugefuegt.")
                continue

            if choice == "3":
                if not category or not category.entries:
                    self._view.show_error("Keine Einträge vorhanden.")
                    continue

                self._view.show_entries(category.entries)
                try:
                    index = int(self._view.prompt_delete_entry_index()) - 1
                    deleted = category.delete_entry(index)
                    self._persist_categories(user_data)
                    self._view.show_success(f"Eintrag '{deleted}' gelöscht.")
                except Exception:
                    self._view.show_error("Ungültige Auswahl.")
                continue

            if choice == "4":
                if self._view.confirm_delete_category():
                    self._budget_manager.delete_category(name)
                    self._persist_categories(user_data)
                    self._view.show_success("Kategorie gelöscht.")
                    return
                continue

            self._view.show_error("Ungültige Auswahl.")

    def _manage_budget_limits(self, user_data: dict) -> None:
        category_name = self._choose_category()
        if not category_name:
            return

        while True:
            print(f"\n\033[1mBudgetlimite für '{category_name}'\033[0m")
            print("1. Anzeigen")
            print("2. Setzen")
            print("3. Ändern")
            print("4. Entfernen")
            choice = self._timed_input(
                "\n\033[34mWähle eine Option (0 = Zurück, 1-4): \033[0m")

            limits = user_data.setdefault("budget_limits", {})

            if choice == "0":
                return

            if choice == "1":
                limit = limits.get(category_name)
                if limit is None:
                    self._view.show_error("Kein Budgetlimit gesetzt.")
                else:
                    self._view.show_success(
                        f"Aktuelles Budgetlimit: {limit:.2f} CHF")
                continue

            if choice in ("2", "3"):
                try:
                    amount = float(
                        self._timed_input(
                            f"\n\033[34mNeues Budgetlimit in CHF (max. {MAX_BUDGET_LIMIT:.2f} CHF):\033[0m"
                        )
                    )
                except ValueError:
                    self._view.show_error("Ungültiger Betrag.")
                    continue

                if not validiere_positiven_betrag(amount, MAX_BUDGET_LIMIT):
                    continue

                limits[category_name] = amount
                self._save_callback()
                self._view.show_success(
                    f"Budgetlimite gesetzt: {amount:.2f} CHF")
                continue

            if choice == "4":
                if category_name in limits:
                    del limits[category_name]
                    self._save_callback()
                    self._view.show_success("Limit entfernt.")
                else:
                    self._view.show_error("Kein Limit vorhanden.")
                continue

            self._view.show_error("Ungültige Eingabe.")

    def _show_statistics(self, user_data: dict) -> None:
        while True:
            choice = self._stats_view.show_menu()
            if choice == "0":
                return
            if choice == "1":
                data = BudgetData(self._export_categories(),
                                  user_data.get("budget_limits", {}))
                self._stats_view.plot_monthly_sums(
                    data.monats_summen_pro_kategorie())
                self._stats_view.wait_for_enter()
                continue
            self._view.show_error("Ungültige Eingabe.")

    def handle_main_action(self, action: str, user_data: dict) -> bool:
        """Verarbeitet die Aktionen 1 bis 5 des Hauptmenüs.

        Returns:
                True, wenn die Aktion verarbeitet wurde, sonst False.
        """
        if action == "1":
            names = list(self._budget_manager.categories.keys())
            self._view.show_categories(names)
            if not names:
                return True

            category_name = self._view.choose_category(names, show_list=False)
            if not category_name:
                return True

            category = self._budget_manager.categories.get(category_name)
            if not category or not category.entries:
                self._view.show_error("Keine Einträge vorhanden.")
                return True

            print()
            self._view.show_success(f"Einträge in '{category_name}':")
            self._view.show_entries(category.entries)
            return True

        if action == "2":
            name = self._view.prompt_category_name()
            if not self._view.validate_category_name(name):
                self._view.show_error(
                    "Ungültiger Name - nur Buchstaben und Leerzeichen erlaubt.")
                return True

            try:
                self._budget_manager.add_category(name)
            except ValueError as error:
                self._view.show_error(str(error))
                return True

            self._persist_categories(user_data)
            self._view.show_success(f"Kategorie '{name}' wurde hinzugefügt.")
            return True

        if action == "3":
            self._edit_category_flow(user_data)
            return True

        if action == "4":
            self._manage_budget_limits(user_data)
            return True

        if action == "5":
            self._show_statistics(user_data)
            return True

        return False
