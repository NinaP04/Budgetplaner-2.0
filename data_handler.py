import json
import os


class DataHandler:
    """
    Verantwortlich für:
    - Laden aller Accounts
    - Speichern aller Accounts
    - Migration alter Datenformate
    - Bereitstellen von Standardkategorien
    """

    DATEN_DATEI = "budget_daten.json"

    STANDARD_KATEGORIEN = {
        "Lebensmittel": [
            "01.01.2025 - Nudeln - 2.50 CHF",
            "02.01.2025 - Milch - 1.80 CHF",
            "03.01.2025 - Gipfeli - 1.20 CHF",
            "04.01.2025 - Fisch (Lachs) - 12.90 CHF",
            "05.01.2025 - Brot - 3.50 CHF",
            "06.03.2025 - Käse - 4.80 CHF",
            "07.03.2025 - Eier - 5.20 CHF",
            "08.03.2025 - Äpfel - 3.60 CHF",
            "09.03.2025 - Tomaten - 2.90 CHF",
            "10.04.2025 - Reis - 3.10 CHF",
            "12.04.2025 - Bananen - 2.40 CHF",
            "15.04.2025 - Joghurt - 1.50 CHF",
            "18.04.2025 - Pouletfilet - 9.80 CHF",
            "22.04.2025 - Spinat - 3.20 CHF",
            "25.04.2025 - Mineralwasser - 1.00 CHF",
            "02.05.2025 - Schokolade - 2.90 CHF",
            "05.05.2025 - Orangensaft - 3.80 CHF",
            "09.05.2025 - Hackfleisch - 8.50 CHF",
            "14.05.2025 - Kartoffeln - 4.20 CHF",
            "20.05.2025 - Zwiebeln - 2.10 CHF",
            "28.05.2025 - Butter - 3.70 CHF"
        ],
        "Studium": [
            "01.01.2025 - Semestergebühr - 750 CHF",
            "10.01.2025 - Laptop-Rücklage - 50 CHF",
            "15.01.2025 - Bücher & Skripte - 380 CHF",
            "20.01.2025 - Lernmaterialien - 40 CHF",
            "01.02.2025 - Software-Lizenz - 30 CHF",
            "22.02.2025 - ÖV-Monatsabo - 65 CHF",
            "12.03.2025 - Kopier- und Druckkosten - 18 CHF",
            "20.03.2025 - Laptop-Rücklage - 50 CHF",
            "12.04.2025 - Mensa & Snacks - 22 CHF",
            "15.04.2025 - Kopier- und Druckkosten - 25 CHF",
            "20.05.2025 - Studierendenverein-Beitrag - 20 CHF"
        ],
        "Freizeit": [
            "05.01.2025 - Kinoabend - 20 CHF",
            "12.01.2025 - Bowling - 15 CHF",
            "18.01.2025 - Museumseintritt - 12 CHF",
            "01.02.2025 - Netflix Abo - 18 CHF",
            "05.02.2025 - Fitnessstudio - 50 CHF",
            "10.02.2025 - Ausflug Zürichsee - 25 CHF",
            "15.02.2025 - Buchhandlung - 22 CHF",
            "20.02.2025 - Café mit Freunden - 14 CHF",
            "25.02.2025 - Konzertticket - 60 CHF",
            "28.02.2025 - Eis essen - 6 CHF",
            "04.04.2025 - Theaterbesuch - 35 CHF",
            "08.04.2025 - Fahrradtour - 10 CHF",
            "12.04.2025 - Brettspielabend - 18 CHF",
            "16.04.2025 - Schwimmbad - 12 CHF",
            "20.04.2025 - Karaokeabend - 22 CHF",
            "02.05.2025 - Netflix Abo - 18 CHF",
            "06.05.2025 - Fitnessstudio - 50 CHF",
            "10.05.2025 - Ausflug Basel Altstadt - 28 CHF",
            "15.05.2025 - Café mit Freunden - 16 CHF",
            "19.05.2025 - Konzertticket - 65 CHF",
            "25.05.2025 - Eis essen - 7 CHF"
        ]
    }

    # ---------------------------------------------------------
    # Konstruktor
    # ---------------------------------------------------------
    def __init__(self):
        self.accounts = self._laden()

    # ---------------------------------------------------------
    # Private Methode: Laden
    # ---------------------------------------------------------
    def _laden(self):
        """Lädt Accounts aus Datei oder erstellt leere Struktur."""
        if not os.path.exists(self.DATEN_DATEI):
            return {}

        with open(self.DATEN_DATEI, "r", encoding="utf-8") as f:
            daten = json.load(f)

        # Migration alter Dateien
        if "accounts" not in daten:
            email = daten.get("benutzer_passwort", {}).get("email", "unknown@example.com")

            migrated = {
                email: {
                    "email": email,
                    "vorname": "",
                    "name": "",
                    "passwort": daten.get("benutzer_passwort", {}).get("passwort"),
                    "budget_kategorien": daten.get("budget_kategorien", {}),
                    "budget_limits": daten.get("budget_limits", {}),
                    "finanzziele": daten.get("finanzziele", {})
                }
            }

            self._speichern(migrated)
            return migrated

        return daten["accounts"]

    # ---------------------------------------------------------
    # Öffentliche Methode: Speichern
    # ---------------------------------------------------------
    def speichern(self):
        """Speichert alle Accounts."""
        self._speichern(self.accounts)

    # ---------------------------------------------------------
    # Private Methode: tatsächliches Schreiben in Datei
    # ---------------------------------------------------------
    def _speichern(self, accounts):
        daten = {"accounts": accounts}
        with open(self.DATEN_DATEI, "w", encoding="utf-8") as f:
            json.dump(daten, f, indent=4, ensure_ascii=False)

    # ---------------------------------------------------------
    # Hilfsmethode: Standardkategorien zurückgeben
    # ---------------------------------------------------------
    def get_standard_kategorien(self):
        return self.STANDARD_KATEGORIEN.copy()
