class AccountManager:
    def __init__(self, accounts, current_user_email, save_callback):
        """
        accounts: dict aller Accounts
        current_user_email: E-Mail des eingeloggten Benutzers
        save_callback: Funktion zum Speichern der Daten
        """
        self.accounts = accounts
        self.current_user_email = current_user_email
        self.save = save_callback

        user = self.accounts.get(self.current_user_email, {})
        if "lohn" not in user:
            user["lohn"] = []

    # ---------------------------------------------------------
    # Kontodaten anzeigen
    # ---------------------------------------------------------
    def anzeigen(self):
        user = self.accounts.get(self.current_user_email, {})

        print("\n\033[01mKontoinformationen\033[0m")
        print("---------------------------------------------")
        print(f"Vorname:  {user.get('vorname', '-')}")
        print(f"Nachname: {user.get('name', '-')}")
        print(f"E-Mail:   {user.get('email', '-')}")
        print(f"Lohn:   {user.get('lohn', '-')}")
        print("---------------------------------------------\n")

    # ---------------------------------------------------------
    # Vorname ändern
    # ---------------------------------------------------------
    def vorname_ändern(self):
        neuer_vorname = input("\n\033[34mNeuer Vorname: \033[0m").strip()

        if not neuer_vorname:
            print("\n\033[31mVorname darf nicht leer sein.\033[0m")
            return False

        self.accounts[self.current_user_email]["vorname"] = neuer_vorname
        self.save()
        print("\n\033[32mVorname erfolgreich geändert.\033[0m")
        return True

    # ---------------------------------------------------------
    # Nachname ändern
    # ---------------------------------------------------------
    def nachname_ändern(self):
        neuer_name = input("\n\033[34mNeuer Nachname: \033[0m").strip()

        if not neuer_name:
            print("\n\033[31mNachname darf nicht leer sein.\033[0m")
            return False

        self.accounts[self.current_user_email]["name"] = neuer_name
        self.save()
        print("\n\033[32mNachname erfolgreich geändert.\033[0m")
        return True

    # ---------------------------------------------------------
    # E-Mail ändern
    # ---------------------------------------------------------
    def email_ändern(self):
        neue_email = input("\n\033[01mNeue E-Mail: \033[0m").strip()

        if not neue_email:
            print("\n\033[31mE-Mail darf nicht leer sein.\033[0m")
            return False

        if neue_email in self.accounts:
            print("\n\033[31mDiese E-Mail existiert bereits!\033[0m")
            return False

        # Daten kopieren
        user_data = self.accounts[self.current_user_email]

        # E-Mail im Datensatz ändern
        user_data["email"] = neue_email

        # Alten Key löschen, neuen Key anlegen
        del self.accounts[self.current_user_email]
        self.accounts[neue_email] = user_data

        # System aktualisieren
        self.current_user_email = neue_email

        self.save()
        print("\n\033[32mE-Mail erfolgreich geändert.\033[0m")
        return True

    # ---------------------------------------------------------
    # Lohn einfügen
    # ---------------------------------------------------------
    def lohn_hinzufügen(self):
        print("\n\033[01mLohn hinzufügen\033[0m")

        # Datum
        datum = input("\033[34mDatum (DD.MM.YYYY oder '.' für heute): \033[0m").strip()
        if datum == ".":
            from datetime import datetime
            datum = datetime.now().strftime("%d.%m.%Y")

        # Betrag
        try:
            betrag = float(input("\033[34mBetrag in CHF: \033[0m"))

            if betrag <= 0:
                print("\n\033[31mDer Betrag muss positiv und größer als 0 sein.\033[0m")
                return False

        except ValueError:
            print("\n\033[31mUngültiger Betrag.\033[0m")
            return False

        # Speichern – Art ist immer LOHN
        eintrag = f"{datum} - Lohn - {betrag} CHF"
        self.accounts[self.current_user_email]["lohn"].append(eintrag)
        self.save()

        print(f"\n\033[32mLohn '{eintrag}' erfolgreich gespeichert.\033[0m")
        return True

    # ---------------------------------------------------------
    # Konto löschen
    # ---------------------------------------------------------
    def konto_löschen(self):
        print("\n\033[31mWARNUNG: Dein gesamtes Konto wird gelöscht!\033[0m")
        print("\033[31mAlle Kategorien, Limits und Finanzdaten werden entfernt.\n\033[0m")

        confirm1 = input("\033[34mBist du sicher? (Y/y zum Bestätigen): \033[0m")
        if confirm1.lower() != "y":
            print("\n\033[31mACHTUNG: Löschen abgebrochen.\033[0m")
            return False

        confirm2 = input("\033[34mBitte tippe 'LÖSCHEN' zur endgültigen Bestätigung: \033[0m")
        if confirm2 != "LÖSCHEN":
            print("\n\033[31mACHTUNG: Löschen abgebrochen.\033[0m")
            return False

        print("\n\033[33mKonto wird gelöscht...\033[0m")

        if self.current_user_email in self.accounts:
            del self.accounts[self.current_user_email]
            self.save()

        print("\033[32mKonto erfolgreich gelöscht.\033[0m")
        return True
