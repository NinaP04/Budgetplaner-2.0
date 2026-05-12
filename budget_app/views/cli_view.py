class CLIView:
    """Alle Ausgaben & Eingaben für Terminal-UI"""

    @staticmethod
    def zeige_login_menu():
        print("\n\033[01mLogin\033[0m")
        print("1. Login")
        print("2. Registrierung")
        return input("\033[34mWähle eine Option: \033[0m")

    @staticmethod
    def zeige_hauptmenu(vorname: str, name: str):
        vorname = vorname.strip() if vorname is not None else ""
        if vorname:
            print(f"\n\033[01mWillkommen {vorname}\033[0m")
        else:
            print("\n\033[01mWillkommen\033[0m")
        print("\n\033[01mKategorien Menü\033[0m")
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
        return input("\033[34mWähle eine Aktion: \033[0m")

    @staticmethod
    def zeige_kategorien(kategorien: dict):
        """Zeige Kategorien formatiert an"""
        for i, (name, einträge) in enumerate(kategorien.items(), 1):
            print(f"{i}. {name} - {len(einträge)} Einträge")

    @staticmethod
    def frage_benutzereingabe(prompt: str) -> str:
        return input(f"\033[34m{prompt}\033[0m")
