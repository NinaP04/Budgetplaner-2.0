import base64
import os
import sys
import random
import string

try:
    import bcrypt
except ImportError:
    print("\n\033[31mFehler: bcrypt ist nicht installiert.\033[0m")
    print("\n033[31mInstalliere es mit: pip install bcrypt\033[0m")
    sys.exit(1)


class AuthManager:
    """
    Objektorientiertes Authentifizierungs-Modul für den Budget-Tracker.
    Verwaltet E-Mail, Login, Passwort-Reset und Passwortänderung.
    """

    def __init__(self, benutzer_daten: dict, save_callback):
        self.benutzer_daten = benutzer_daten
        self.save_callback = save_callback
        self._reset_codes = {}

    # ---------------- Passwort-Hashing und Verifizieren----------------

    @staticmethod
    def hash_passwort(passwort: str) -> str:
        salt = bcrypt.gensalt(rounds=12)
        hashed = bcrypt.hashpw(passwort.encode("utf-8"), salt)
        return base64.b64encode(hashed).decode("utf-8")

    @staticmethod
    def verifiziere_passwort(passwort: str, hashed_passwort: str) -> bool:
        try:
            hashed_bytes = base64.b64decode(hashed_passwort.encode("utf-8"))
            return bcrypt.checkpw(passwort.encode("utf-8"), hashed_bytes)
        except Exception:
            return False

    # ---------------- Login ----------------

    def login(self, accounts: dict) -> str | None:
        print("\n\033[34mBitte gebe deine Logindaten ein.\033[0m")

        email = input("\033[34mE-Mail: \033[0m").strip().lower()

        # Konto existiert nicht → Erstregistrierung
        if email not in accounts:
            print("\n\033[33mFür diese E-Mail existiert kein Konto.\033[0m")
            choice = input("\033[34mNeues Konto anlegen? (Y/N): \033[0m").strip().lower()

            if choice != "y":
                print("\n\033[34mOkay, bitte erneut versuchen.\033[0m")
                return None

            accounts[email] = {
                "email": email,
                "vorname": "",
                "name": "",
                "passwort": None,
                "budget_kategorien": {
                    "Haushalt": [
                        "01.01.2026 - Lebensmittel - 50 CHF",
                        "05.01.2026 - Reinigung - 20 CHF",
                        "10.01.2026 - Hygiene - 15 CHF"
                    ],
                    "Freizeit": [
                        "03.01.2026 - Kino - 18 CHF",
                        "07.01.2026 - Restaurant - 45 CHF",
                        "12.01.2026 - Bowling - 25 CHF"
                    ]
                },
                "budget_limits": {
                    "Haushalt": 500,
                    "Freizeit": 300
                },
                "lohn": []
            }

            self.benutzer_daten = accounts[email]
            print("\n\033[32mKonto erstellt! Bitte Passwort setzen.\033[0m")
            self.passwort_ändern(ohne_altes_passwort=True)
            self.save_callback()
            return email

        # Konto existiert → Login
        self.benutzer_daten = accounts[email]
        gespeichertes_pw = self.benutzer_daten.get("passwort")

        for _ in range(3):
            pw = input("\033[34mPasswort ('f' für Reset): \033[0m").strip()

            if pw.lower() == "f":
                if self.passwort_vergessen_flow():
                    print("\nBitte erneut einloggen.")
                return None

            if self.verifiziere_passwort(pw, gespeichertes_pw):
                print("\n\033[32mErfolgreich eingeloggt!\033[0m")
                return email

            print("\n\033[31mFalsches Passwort!\033[0m")

        print("\n\033[31mZu viele Fehlversuche.\033[0m")
        return None

    # ---------------- Erstregistrierung ----------------

    def _erstregistrierung(self, email: str):
        if not email:
            email = input("\033[34mBitte E-Mail eingeben: \033[0m").strip()

        self.benutzer_daten["email"] = email
        print("\n\033[32mE-Mail erfolgreich gespeichert.\033[0m")
        self.passwort_ändern(ohne_altes_passwort=True)

    # ---------------- Passwort vergessen ----------------

    def sende_reset_code(self, email: str) -> bool:
        gespeicherte_email = self.benutzer_daten.get("email")
        if email != gespeicherte_email:
            print("\n\033[33mDiese E-Mail ist nicht registriert.\033[0m")
            return False

        code = "".join(random.choices(string.digits, k=6))
        self._reset_codes[email] = code

        print(f"\n\033[12mDer Reset-Code wurde an \033[01m{email}\033[0m gesendet.")
        print(f"(Debug-Code: {code})")
        return True

    def passwort_vergessen_flow(self):
        print("\n\033[01mPasswort zurücksetzten\033[0m")
        email = input("\n\033[34mE-Mail eingeben: \033[0m").strip()

        if not self.sende_reset_code(email):
            return False

        code_input = input("\n\033[34mReset-Code eingeben: \033[0m").strip()

        if code_input != self._reset_codes.get(email):
            print("\n\033[31mFalscher Reset-Code!\033[0m")
            return False

        print("\n\033[32mReset-Code korrekt! Setzte ein neues Passwort: \033[0m")
        return self.passwort_ändern(ohne_altes_passwort=True)

    # ---------------- Passwort ändern ----------------

    def passwort_ändern(self, ohne_altes_passwort: bool = False) -> bool:
        hashed_passwort = self.benutzer_daten.get("passwort")

        if not ohne_altes_passwort and hashed_passwort:
            aktuelles = input("\n\033[34mAktuelles Passwort: \033[0m")
            if not self.verifiziere_passwort(aktuelles, hashed_passwort):
                print("\n\033[31mUngültiges Passwort!\033[0m")
                return False

        print("\n\033[01mPasswort neu festlegen: \033[0m")
        print("- Mindestens 8 Zeichen")
        print("- Groß- und Kleinbuchstaben")
        print("- Mindestens 1 Zahl")
        print("- Mindestens 1 Sonderzeichen (!,@,#,%,?,&,*)")

        while True:
            pw1 = input("\n\033[34mNeues Passwort: \033[0m")
            pw2 = input("\033[34mPasswort wiederholen: \033[0m")

            if pw1 != pw2:
                print("\n\033[31mPasswörter stimmen nicht überein!\033[0m")
                continue

            if not self._validiere_passwort(pw1):
                continue

            self.benutzer_daten["passwort"] = self.hash_passwort(pw1)
            self.save_callback()
            print("\n\033[32mPasswort erfolgreich geändert!\033[0m")
            return True

    @staticmethod
    def _validiere_passwort(passwort: str) -> bool:
        special = "!@#%?&*"

        if len(passwort) < 8:
            print("Mindestens 8 Zeichen.")
            return False
        if not any(c.isupper() for c in passwort):
            print("Mindestens 1 Großbuchstabe.")
            return False
        if not any(c.islower() for c in passwort):
            print("Mindestens 1 Kleinbuchstabe.")
            return False
        if not any(c.isdigit() for c in passwort):
            print("Mindestens 1 Zahl.")
            return False
        if not any(c in special for c in passwort):
            print("Mindestens 1 Sonderzeichen (!@#%?&*)")
            return False

        return True
