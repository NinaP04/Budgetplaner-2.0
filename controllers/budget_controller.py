"""Controller fuer Budgetfunktionen im MVC-Aufbau."""

from typing import Callable

from category_manager import BudgetEntry, BudgetManager, BudgetUI
from finance_control import BudgetLimitManager
from statistic import BudgetData, StatisticMenu


class BudgetController:
    """Koordiniert Budget-Workflows zwischen Modellen und CLI-Ausgabe."""

    def __init__(self, timed_input: Callable[[str], str], save_callback):
        self._timed_input = timed_input
        self._save_callback = save_callback
        self._budget_manager = BudgetManager()
        self._budget_ui = BudgetUI(self._budget_manager, self._timed_input)

    def load_from_user_data(self, user_data: dict) -> None:
        """Importiert gespeicherte Kategorien in das interne Budget-Model."""
        self._budget_manager = BudgetManager()
        self._budget_ui = BudgetUI(self._budget_manager, self._timed_input)

        gespeicherte_kategorien = user_data.get("budget_kategorien", {})
        for name, eintraege in gespeicherte_kategorien.items():
            self._budget_manager.add_category(name)
            for eintrag in eintraege:
                self._budget_manager.add_entry(
                    name, BudgetEntry.from_string(eintrag))

    def _export_categories(self) -> dict:
        export = {}
        for name, category in self._budget_manager.categories.items():
            export[name] = [str(entry) for entry in category.entries]
        return export

    def _persist_categories(self, user_data: dict) -> None:
        user_data["budget_kategorien"] = self._export_categories()
        self._save_callback()

    def _edit_category_flow(self, user_data: dict) -> None:
        name = self._budget_ui.choose_category()
        if not name:
            return

        self._budget_ui.edit_category(name)
        self._persist_categories(user_data)

    def handle_main_action(self, action: str, user_data: dict) -> bool:
        """Verarbeitet Aktionen 1-5 des Hauptmenues.

        Returns:
                True, wenn die Aktion verarbeitet wurde, sonst False.
        """
        if action == "1":
            self._budget_ui.show_categories()
            return True

        if action == "2":
            self._budget_ui.create_category()
            self._persist_categories(user_data)
            return True

        if action == "3":
            self._edit_category_flow(user_data)
            return True

        if action == "4":
            budget_limits = user_data.get("budget_limits", {})
            manager = BudgetLimitManager(
                self._export_categories(),
                budget_limits,
                self._timed_input,
                self._save_callback,
            )
            user_data["budget_limits"] = manager.start()
            self._save_callback()
            return True

        if action == "5":
            data = BudgetData(self._export_categories(),
                              user_data.get("budget_limits", {}))
            menu = StatisticMenu(data, self._timed_input)
            menu.start()
            return True

        return False
