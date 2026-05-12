"""Hilfsfunktionen für die Darstellung in der CLI.

Diese Datei hält reine Formatierungslogik zusammen, damit die View-Klassen
nicht mit ANSI-Codes und wiederholten Überschriften überladen werden.
"""


class Formatter:
	"""Kleine Sammlung statischer Formatierungshilfen für Terminalausgaben."""

	RESET = "\033[0m"
	BOLD = "\033[01m"
	BLUE = "\033[34m"
	GREEN = "\033[32m"
	RED = "\033[31m"

	@staticmethod
	def fett(text: str) -> str:
		return f"{Formatter.BOLD}{text}{Formatter.RESET}"

	@staticmethod
	def blau(text: str) -> str:
		return f"{Formatter.BLUE}{text}{Formatter.RESET}"

	@staticmethod
	def gruen(text: str) -> str:
		return f"{Formatter.GREEN}{text}{Formatter.RESET}"

	@staticmethod
	def rot(text: str) -> str:
		return f"{Formatter.RED}{text}{Formatter.RESET}"

	@staticmethod
	def titel(text: str) -> str:
		return f"\n{Formatter.fett(text)}"

	@staticmethod
	def trennlinie(zeichen: str = "-", länge: int = 45) -> str:
		return zeichen * länge

	@staticmethod
	def eingabeaufforderung(text: str) -> str:
		return f"{Formatter.BLUE}{text}{Formatter.RESET}"

	@staticmethod
	def erfolg(text: str) -> str:
		return Formatter.gruen(text)

	@staticmethod
	def fehler(text: str) -> str:
		return Formatter.rot(text)
