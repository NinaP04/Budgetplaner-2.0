import unittest

from models.account_model import AccountModel
from models.budget import BudgetCategory, BudgetEntry, BudgetManager
from utils.validators import validiere_datum


class TestBudgetAppUnits(unittest.TestCase):
    def test_validiere_datum_accepts_valid_date(self):
        self.assertTrue(validiere_datum("14.05.2026"))

    def test_validiere_datum_rejects_invalid_date(self):
        self.assertFalse(validiere_datum("31.02.2026"))

    def test_budget_entry_from_string_parses_fields(self):
        entry = BudgetEntry.from_string("14.05.2026 - Essen - 12.50 CHF")

        self.assertEqual(entry.datum, "14.05.2026")
        self.assertEqual(entry.art, "Essen")
        self.assertEqual(entry.betrag, 12.5)
        self.assertEqual(str(entry), "14.05.2026 - Essen - 12.50 CHF")

    def test_budget_category_total_and_limit_exceeded(self):
        category = BudgetCategory("Essen", limit=100)
        category.add_entry(BudgetEntry("14.05.2026", "Mittag", 40))
        category.add_entry(BudgetEntry("15.05.2026", "Abend", 30))

        self.assertEqual(category.total(), 70)
        self.assertFalse(category.limit_exceeded(20))
        self.assertTrue(category.limit_exceeded(40))

    def test_budget_manager_rejects_duplicate_category(self):
        manager = BudgetManager()
        manager.add_category("Miete")

        with self.assertRaises(ValueError):
            manager.add_category("Miete")

    def test_change_firstname_updates_user_data(self):
        user_data = {"vorname": "Anna", "name": "Muster"}

        success, message = AccountModel.change_firstname(user_data, "Laura")

        self.assertTrue(success)
        self.assertEqual(message, "Vorname erfolgreich geändert.")
        self.assertEqual(user_data["vorname"], "Laura")


if __name__ == "__main__":
    unittest.main()
