from collections import defaultdict
from datetime import datetime

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
