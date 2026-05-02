"""Hilfen für zeitgesteuerte Eingaben und automatischen Logout."""

import os
import threading


class InaktivitätsManager:
    """Erstellt einen timed input, der bei Inaktivität ausloggt."""

    def __init__(self, timeout, daten_speichern_func):
        self.timeout = timeout
        self.daten_speichern_func = daten_speichern_func

    def _logout(self):
        print("\n\n\033[31mDu wurdest wegen Inaktivität ausgeloggt! \033[0m")
        self.daten_speichern_func()
        os._exit(0)

    def timed_input(self, prompt):
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


__all__ = ["InaktivitätsManager"]
