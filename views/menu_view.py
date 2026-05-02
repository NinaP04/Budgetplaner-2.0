"""Menü-Darstellung für die CLI.

Die View kümmert sich nur um Ausgaben und Eingaben. Die eigentliche Logik
bleibt im Controller bzw. in den Modellklassen.
"""

from views.formatter import Formatter


class MenuView:
	"""Zentrale CLI-Menüs für Login, Hauptmenü und Kontomenü."""

	@staticmethod
	def zeige_login_menu() -> str:
		print(Formatter.titel("Login"))
		print("1. Login")
		print("2. Registrierung")
		return input(Formatter.eingabeaufforderung("Wähle eine Option: "))

	@staticmethod
	def zeige_hauptmenu(vorname: str, name: str) -> str:
		print(Formatter.titel(f"Willkommen {vorname} {name}"))
		print(Formatter.titel("Kategorien Menü"))
		print("1. Kategorien anzeigen")
		print("2. Kategorie hinzufügen")
		print("3. Kategorie löschen")
		print("4. Kategorie bearbeiten")
		print("5. Eintrag hinzufügen")
		print("6. Einträge anzeigen")
		print("7. Eintrag löschen")
		print("8. Eintrag bearbeiten")
		print("9. Account Einstellungen")
		print("0. Logout")
		return input(Formatter.eingabeaufforderung("Wähle eine Aktion: "))

	@staticmethod
	def zeige_konto_menu() -> str:
		print(Formatter.titel("Konto Menü"))
		print("1. Kontodaten anzeigen")
		print("2. Vorname ändern")
		print("3. Nachname ändern")
		print("4. E-Mail ändern")
		print("5. Passwort ändern")
		print("6. Lohn hinzufügen")
		print("7. Konto löschen")
		return input(Formatter.eingabeaufforderung("Wähle eine Aktion (0. Zurück): "))

	@staticmethod
	def zeige_kategorien(kategorien: dict) -> None:
		print(Formatter.titel("Kategorien"))
		if not kategorien:
			print("Keine Kategorien vorhanden.")
			return

		for index, (name, einträge) in enumerate(kategorien.items(), start=1):
			print(f"{index}. {name} - {len(einträge)} Einträge")

	@staticmethod
	def frage_benutzereingabe(prompt: str) -> str:
		return input(Formatter.eingabeaufforderung(prompt))

	@staticmethod
	def zeige_erfolg(text: str) -> None:
		print(Formatter.erfolg(text))

	@staticmethod
	def zeige_fehler(text: str) -> None:
		print(Formatter.fehler(text))
