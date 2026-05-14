import json
import tempfile
import unittest
from unittest.mock import Mock

from controllers.budget_controller import BudgetController
from models.account_model import AccountModel
from models.auth_model import AuthModel
from models.data_storage import DataHandler


class TestBudgetAppIntegration(unittest.TestCase):
    def setUp(self):
        DataHandler._instance = None

    def tearDown(self):
        DataHandler._instance = None

    def test_budgetcontroller_import_and_export_categories_roundtrip(self):
        save_callback = Mock()
        controller = BudgetController(lambda prompt="": "0", save_callback)

        user_data = {
            "budget_kategorien": {
                "Haushalt": [
                    "04.05.2026 - Krankenkasse - 365.80 CHF",
                    "30.04.2026 - Wingo Abo - 29.95 CHF",
                ],
                "Freizeit": [
                    "13.05.2026 - Kino Besuch - 30.00 CHF",
                    "03.05.2026 - Brunch Date - 17.35 CHF",
                ],
            },
            "budget_limits": {"Haushalt": 500, "Freizeit": 300},
        }

        controller.load_from_user_data(user_data)

        self.assertEqual(
            controller._export_categories(),
            user_data["budget_kategorien"],
        )

    def test_budgetcontroller_add_category_updates_user_data_and_saves(self):
        save_callback = Mock()
        controller = BudgetController(lambda prompt="": "0", save_callback)
        controller._view.prompt_category_name = Mock(return_value="Gesundheit")
        controller._view.validate_category_name = Mock(return_value=True)
        controller._view.show_error = Mock()
        controller._view.show_success = Mock()

        user_data = {"budget_kategorien": {}, "budget_limits": {}}

        handled = controller.handle_main_action("2", user_data)

        self.assertTrue(handled)
        self.assertIn("Gesundheit", user_data["budget_kategorien"])
        self.assertEqual(user_data["budget_kategorien"]["Gesundheit"], [])
        save_callback.assert_called_once()

    def test_accountmodel_change_email_updates_accounts_and_keeps_profile_data(self):
        accounts = {
            "alt@example.com": {
                "email": "alt@example.com",
                "vorname": "Sarah",
                "name": "Spargut",
                "lohn": ["27.04.2026 - Lohn - 3500.0 CHF"],
            }
        }

        ok, message, updated_email = AccountModel.change_email(
            accounts,
            "alt@example.com",
            "neu@example.com",
        )

        self.assertTrue(ok)
        self.assertEqual(message, "E-Mail erfolgreich geändert.")
        self.assertEqual(updated_email, "neu@example.com")
        self.assertNotIn("alt@example.com", accounts)
        self.assertIn("neu@example.com", accounts)
        self.assertEqual(accounts["neu@example.com"]
                         ["email"], "neu@example.com")
        self.assertEqual(
            AccountModel.profile_data(accounts["neu@example.com"])["email"],
            "neu@example.com",
        )

    def test_authmodel_password_roundtrip_and_reset_code_validation(self):
        auth_model = AuthModel()
        user_data = AuthModel.default_user_data("sarah@example.com")

        auth_model.set_password(user_data, "Test1234!")

        self.assertTrue(
            auth_model.verify_password("Test1234!", user_data["passwort"])
        )

        reset_code = auth_model.generate_reset_code("sarah@example.com")
        self.assertTrue(
            auth_model.verify_reset_code("sarah@example.com", reset_code)
        )
        self.assertFalse(
            auth_model.verify_reset_code("sarah@example.com", "000000")
        )


if __name__ == "__main__":
    unittest.main()
