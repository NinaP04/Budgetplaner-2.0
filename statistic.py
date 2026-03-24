"""
Statistik-Modul für Budget-Tracker
Enthält Funktionen zur Datenaufbereitung und Visualisierung
"""

import matplotlib.pyplot as plt
import numpy as np
from datetime import datetime
from collections import defaultdict


# ---------------------------------------------------------
# 1) DATEN- UND BERECHNUNGSLOGIK
# ---------------------------------------------------------

class BudgetData:
    """Verwaltet Budgetdaten, Limits und Finanzziele."""

    def __init__(self, budget_kategorien, budget_limits):
        self.budget_kategorien = budget_kategorien
        self.budget_limits = budget_limits

    # -----------------------------
    # Monatsstatistik pro Kategorie
    # -----------------------------
    def monats_summen_pro_kategorie(self):
        ergebnis = {}

        for kategorie, eintraege in self.budget_kategorien.items():
            monats_summen = defaultdict(float)

            for e in eintraege:
                teile = e.split(" - ")
                if len(teile) != 3:
                    continue

                datum_str = teile[0].strip()
                betrag_str = teile[2].replace("CHF", "").strip()

                try:
                    datum = datetime.strptime(datum_str, "%d.%m.%Y")
                    monat = datum.strftime("%Y-%m")
                    betrag = float(betrag_str)
                    monats_summen[monat] += betrag
                except Exception:
                    continue

            monate = sorted(monats_summen.keys())
            werte = [monats_summen[m] for m in monate]

            limit = self.budget_limits.get(kategorie)
            farben = [
                "green" if (limit is not None and betrag <= limit)
                else "red" if (limit is not None and betrag > limit)
                else "blue"
                for betrag in werte
            ]

            ergebnis[kategorie] = {
                "monate": monate,
                "werte": werte,
                "farben": farben,
                "limit": limit
            }

        return ergebnis

# ---------------------------------------------------------
# 2) VISUALISIERUNG
# ---------------------------------------------------------

class BudgetPlotter:
    """Erzeugt Diagramme für Budgetstatistiken."""

    @staticmethod
    def plot_monats_summen(kategorien_daten):
        kategorien = list(kategorien_daten.keys())
        if not kategorien:
            print("\n\033[33mKeine Kategorien-Daten vorhanden.\033[0m")
            return

        prev_values = []
        curr_values = []
        farben = []

        for kategorie in kategorien:
            daten = kategorien_daten[kategorie]
            werte = daten.get("werte", [])

            curr = werte[-1] if len(werte) >= 1 else 0.0
            prev = werte[-2] if len(werte) >= 2 else 0.0

            prev_values.append(prev)
            curr_values.append(curr)

            limit = daten.get("limit")
            if limit is None:
                farben.append("blue")
            elif curr > limit:
                farben.append("red")
            else:
                farben.append("green")

        x = np.arange(len(kategorien))
        width = 0.35

        fig, ax = plt.subplots(figsize=(12, 6))

        ax.bar(x - width/2, prev_values, width,
               label='Vormonat', color='lightgray', edgecolor='black')
        bars_curr = ax.bar(x + width/2, curr_values, width,
                           color=farben, edgecolor='black')

        # Werte anzeigen
        for bar in bars_curr:
            h = bar.get_height()
            ax.annotate(f"{h:.2f}",
                        xy=(bar.get_x() + bar.get_width() / 2, h),
                        xytext=(0, 3),
                        textcoords="offset points",
                        ha="center")

        ax.set_title("Monatliche Summen pro Kategorie")
        ax.set_xticks(x)
        ax.set_xticklabels(kategorien)

        plt.tight_layout()
        print("\033[33mBitte Statistik schliessen um fortzufahren\033[0m")
        plt.show()

# ---------------------------------------------------------
# 3) MENÜSTEUERUNG
# ---------------------------------------------------------

class StatisticMenu:
    """Steuert das Statistik-Menü."""

    def __init__(self, data: BudgetData, timed_input):
        self.data = data
        self.timed_input = timed_input

    def start(self):
        while True:
            print("\n\033[01mStatistik-Menü\033[0m")
            print("1. Monatsstatistik")

            auswahl = self.timed_input("\n\033[34mWähle deine Statistik aus (0. Zurück): \033[0m")

            if auswahl == "0":
                return

            elif auswahl == "1":
                daten = self.data.monats_summen_pro_kategorie()
                BudgetPlotter.plot_monats_summen(daten)
                self.timed_input("\n\033[34mDrücke Enter, um zurückzukehren.\033[0m")

            else:
                print("\n\033[31mUngültige Eingabe.\033[0m")
