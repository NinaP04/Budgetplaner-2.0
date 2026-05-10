"""CLI + plotting view for budget statistics."""

import matplotlib.pyplot as plt
import numpy as np


class StatisticsView:
    """Renders statistics menu and charts."""

    def __init__(self, input_func=input):
        self._input = input_func

    def show_menu(self) -> str:
        print("\n\033[01mStatistik-Menue\033[0m")
        print("1. Monatsstatistik")
        return self._input("\n\033[34mWaehle deine Statistik aus (0. Zurueck): \033[0m").strip()

    def wait_for_enter(self) -> None:
        self._input("\n\033[34mDruecke Enter, um zurueckzukehren.\033[0m")

    @staticmethod
    def plot_monthly_sums(categories_data: dict) -> None:
        categories = list(categories_data.keys())
        if not categories:
            print("\n\033[33mKeine Kategorien-Daten vorhanden.\033[0m")
            return

        prev_values = []
        curr_values = []
        colors = []

        for category in categories:
            data = categories_data[category]
            values = data.get("werte", [])

            curr = values[-1] if len(values) >= 1 else 0.0
            prev = values[-2] if len(values) >= 2 else 0.0

            prev_values.append(prev)
            curr_values.append(curr)

            limit = data.get("limit")
            if limit is None:
                colors.append("blue")
            elif curr > limit:
                colors.append("red")
            else:
                colors.append("green")

        x = np.arange(len(categories))
        width = 0.35

        fig, ax = plt.subplots(figsize=(12, 6))
        ax.bar(
            x - width / 2,
            prev_values,
            width,
            label="Vormonat",
            color="lightgray",
            edgecolor="black",
        )
        bars_curr = ax.bar(
            x + width / 2,
            curr_values,
            width,
            color=colors,
            edgecolor="black",
        )

        for bar in bars_curr:
            height = bar.get_height()
            ax.annotate(
                f"{height:.2f}",
                xy=(bar.get_x() + bar.get_width() / 2, height),
                xytext=(0, 3),
                textcoords="offset points",
                ha="center",
            )

        ax.set_title("Monatliche Summen pro Kategorie")
        ax.set_xticks(x)
        ax.set_xticklabels(categories)

        plt.tight_layout()
        print("\033[33mBitte Statistik schliessen um fortzufahren\033[0m")
        plt.show()
