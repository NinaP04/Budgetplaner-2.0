"""Statistik page — /statistik."""

from collections import defaultdict
from datetime import datetime

import plotly.graph_objects as go
from nicegui import ui

from gui.theme import apply_theme
from gui.components.sidebar import create_sidebar
from gui.components.header import create_header
from gui.services import get_budget_service, get_session_manager
from models.finance import BudgetData

_BLUE = "#0098DA"
_GREEN = "#10B981"
_RED = "#EF4444"
_GRAY = "#E2E8F0"
_TEXT = "#1A1A2E"


@ui.page("/statistik")
def statistik():
    apply_theme()
    ui.query("body").classes("bg-gray-50")

    session = get_session_manager()
    if not session.is_authenticated():
        ui.navigate.to("/login")
        return

    user = session.get_current_user() or {}
    email = user.get("email", "")

    create_sidebar(active_page="statistik")
    create_header(title="Statistik", subtitle="Finanzübersicht und Diagramme")

    service = get_budget_service()
    transactions = service.list_transactions(email)

    user_data = _load_user_data(email)
    monthly_stats = BudgetData(
        user_data.get("budget_kategorien", {}),
        user_data.get("budget_limits", {}),
    ).monats_summen_pro_kategorie()

    with ui.column().classes("w-full p-10 gap-8"):
        ui.label("Statistik").classes("text-3xl font-bold text-[#0098DA]")
        ui.label("Diagramme und Auswertungen Ihrer Finanzen").classes(
            "text-sm text-[#0098DA] opacity-65"
        )

        if not transactions:
            ui.label("Noch keine Daten vorhanden.").classes(
                "text-sm text-gray-500"
            )
            return

        # Row 1: Monthly spending
        with ui.card().classes(
            "w-full p-5 border border-gray-300 rounded"
        ):
            ui.label("Monatliche Ausgaben pro Kategorie").classes(
                "text-base font-semibold text-gray-800 mb-3"
            )
            if monthly_stats:
                ui.plotly(_monthly_bar_chart(monthly_stats)).classes("w-full")
            else:
                ui.label("Keine Daten.").classes("text-sm text-gray-500")

        # Row 2: Income vs Expenses over time
        with ui.card().classes(
            "w-full p-5 border border-gray-300 rounded"
        ):
            ui.label("Einnahmen vs. Ausgaben (monatlich)").classes(
                "text-base font-semibold text-gray-800 mb-3"
            )
            if transactions:
                ui.plotly(_income_vs_expense_chart(transactions)).classes("w-full")
            else:
                ui.label("Keine Transaktionen.").classes("text-sm text-gray-500")


# ---------------------------------------------------------------------------
# Chart builders
# ---------------------------------------------------------------------------

def _monthly_bar_chart(stats: dict) -> go.Figure:
    categories = list(stats.keys())
    prev_vals, curr_vals, curr_colors = [], [], []

    for cat in categories:
        data = stats[cat]
        values = data.get("werte", [])
        farben = data.get("farben", [])
        limit = data.get("limit")

        prev = values[-2] if len(values) >= 2 else 0.0
        curr = values[-1] if len(values) >= 1 else 0.0
        prev_vals.append(prev)
        curr_vals.append(curr)

        if limit is None:
            curr_colors.append(_BLUE)
        elif curr > limit:
            curr_colors.append(_RED)
        else:
            curr_colors.append(_GREEN)

    fig = go.Figure()
    fig.add_trace(go.Bar(
        name="Vormonat",
        x=categories,
        y=prev_vals,
        marker_color=_GRAY,
        text=[f"CHF {v:,.2f}" for v in prev_vals],
        textposition="outside",
    ))
    fig.add_trace(go.Bar(
        name="Aktueller Monat",
        x=categories,
        y=curr_vals,
        marker_color=curr_colors,
        text=[f"CHF {v:,.2f}" for v in curr_vals],
        textposition="outside",
    ))

    # Limit lines
    for i, cat in enumerate(categories):
        limit = stats[cat].get("limit")
        if limit is not None:
            fig.add_shape(
                type="line",
                x0=i - 0.4, x1=i + 0.4,
                y0=limit, y1=limit,
                line=dict(color=_RED, width=2, dash="dash"),
            )

    fig.update_layout(
        barmode="group",
        paper_bgcolor="white",
        plot_bgcolor="white",
        margin=dict(t=20, b=40, l=40, r=20),
        height=340,
        legend=dict(orientation="h", y=-0.2),
        yaxis=dict(title="CHF", gridcolor="#F0F4F8"),
        xaxis=dict(gridcolor="#F0F4F8"),
        font=dict(family="Inter, sans-serif", color=_TEXT),
    )
    return fig



def _income_vs_expense_chart(transactions: list[dict]) -> go.Figure:
    income_by_month: dict[str, float] = defaultdict(float)
    expense_by_month: dict[str, float] = defaultdict(float)

    for t in transactions:
        try:
            month = datetime.strptime(t["datum"], "%d.%m.%Y").strftime("%b %Y")
        except ValueError:
            continue
        if t["typ"] == "einnahme":
            income_by_month[month] += t["betrag"]
        else:
            expense_by_month[month] += t["betrag"]

    all_months = sorted(
        set(income_by_month) | set(expense_by_month),
        key=lambda m: datetime.strptime(m, "%b %Y"),
    )

    fig = go.Figure()
    fig.add_trace(go.Bar(
        name="Einnahmen",
        x=all_months,
        y=[income_by_month.get(m, 0) for m in all_months],
        marker_color=_GREEN,
        text=[f"CHF {income_by_month.get(m, 0):,.2f}" for m in all_months],
        textposition="outside",
    ))
    fig.add_trace(go.Bar(
        name="Ausgaben",
        x=all_months,
        y=[expense_by_month.get(m, 0) for m in all_months],
        marker_color=_RED,
        text=[f"CHF {expense_by_month.get(m, 0):,.2f}" for m in all_months],
        textposition="outside",
    ))
    fig.update_layout(
        barmode="group",
        paper_bgcolor="white",
        plot_bgcolor="white",
        margin=dict(t=20, b=40, l=40, r=20),
        height=320,
        legend=dict(orientation="h", y=-0.2),
        yaxis=dict(title="CHF", gridcolor="#F0F4F8"),
        xaxis=dict(gridcolor="#F0F4F8"),
        font=dict(family="Inter, sans-serif", color=_TEXT),
    )
    return fig


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _load_user_data(email: str) -> dict:
    from models.data_storage import DataHandler
    dh = DataHandler()
    return dh.accounts.get(email, {})
