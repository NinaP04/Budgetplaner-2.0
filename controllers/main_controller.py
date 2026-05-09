"""Hauptcontroller der Anwendung im MVC-Aufbau."""

from controllers.account_controller import AccountController
from controllers.auth_controller import AuthController
from controllers.budget_controller import BudgetController
from data_handler import DataHandler
from utils import InaktivitätsManager


class MainController:
	"""Orchestriert Auth-, Konto- und Budget-Controller."""

	def __init__(self, timeout_seconds: int = 1200):
		self.data_handler = DataHandler()
		self.accounts = self.data_handler.accounts

		self.current_user_email = None
		self.current_user_data = None

		inactivity = InaktivitätsManager(timeout_seconds, self.save_data)
		self._timed_input = inactivity.timed_input

		self.auth_controller = AuthController(self.accounts, self.save_data)
		self.account_controller = AccountController(
			self.accounts,
			self.save_data,
			timed_input=self._timed_input,
		)
		self.budget_controller = BudgetController(self._timed_input, self.save_data)

	def save_data(self) -> None:
		self.data_handler.speichern()

	def _show_main_menu(self) -> str:
		benutzer = self.current_user_data or {}

		print(
			f"\n\033[01mWillkommen {benutzer.get('vorname', '')} {benutzer.get('name', '')}\033[0m"
		)
		print("\n\033[01mKategorien Menue\033[0m")
		print("1. Kategorien anzeigen")
		print("2. Kategorie hinzufuegen")
		print("3. Kategorie bearbeiten")
		print("4. Budgetlimite setzen")
		print("5. Statistik anzeigen")
		print("6. Konto verwalten")
		print("7. Logout")
		return self._timed_input("\n\033[34mWaehle eine Aktion: \033[0m")

	def _main_menu_loop(self):
		while True:
			choice = self._show_main_menu()

			if self.budget_controller.handle_main_action(choice, self.current_user_data):
				continue

			if choice == "6":
				new_email, logout = self.account_controller.menu_loop(self.auth_controller)
				if logout:
					return "logout"

				if new_email and new_email != self.current_user_email:
					self.current_user_email = new_email
					self.current_user_data = self.accounts[new_email]
					self.account_controller.set_active_user(new_email)
					self.auth_controller.set_active_user(new_email)
				continue

			if choice == "7":
				print("\n\033[32mDu wurdest erfolgreich ausgeloggt.\033[0m")
				return "logout"

			print("\n\033[31mAchtung: Ungueltige Eingabe!\033[0m")

	def start(self):
		while True:
			email = self.auth_controller.login()
			if not email:
				continue

			self.current_user_email = email
			self.current_user_data = self.accounts[email]

			self.auth_controller.set_active_user(email)
			self.account_controller.set_active_user(email)
			self.budget_controller.load_from_user_data(self.current_user_data)

			result = self._main_menu_loop()
			if result == "logout":
				continue

			self.save_data()
