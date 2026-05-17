"""Statistik-Seite — /statistik."""

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
_GRAY = "#94A3B8"      # Dunkleres Grau, damit die "Vormonat"-Balken gut lesbar sind
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

        # Erste Zeile: Monatliche Ausgaben pro Kategorie
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

        # Zweite Zeile: Einnahmen vs. Ausgaben im Zeitverlauf
        with ui.card().classes(
            "w-full p-5 border border-gray-300 rounded"
        ):
            ui.label("Einnahmen vs. Ausgaben (monatlich)").classes(
                "text-base font-semibold text-gray-800 mb-3"
            )
            if transactions:
                ui.plotly(_income_vs_expense_chart(
                    transactions)).classes("w-full")
            else:
                ui.label("Keine Transaktionen.").classes(
                    "text-sm text-gray-500")


# ---------------------------------------------------------------------------
# Hilfsfunktion: CHF-Formatierung
# ---------------------------------------------------------------------------

def _format_chf(value: float) -> str:
    """Formatiert eine Zahl als 'CHF 1'234.50' (Schweizer Stil)."""
    return f"CHF {value:,.2f}".replace(",", "'")


# ---------------------------------------------------------------------------
# Diagramm-Erstellung
# ---------------------------------------------------------------------------

def _monthly_bar_chart(stats: dict) -> go.Figure:
    categories = list(stats.keys())
    prev_vals, curr_vals, curr_colors = [], [], []

    for cat in categories:
        data = stats[cat]
        values = data.get("werte", [])
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

    # Balkenbreite begrenzen, damit Balken bei wenigen Kategorien nicht riesig werden
    bar_width = min(0.35, 0.7 / max(len(categories), 1))

    fig = go.Figure()
    fig.add_trace(go.Bar(
        name="Vormonat",
        x=categories,
        y=prev_vals,
        marker_color=_GRAY,
        text=[_format_chf(v) for v in prev_vals],
        textposition="outside",
        textfont=dict(size=13, color=_TEXT, family="Inter, sans-serif"),
        cliponaxis=False,
        width=bar_width,
    ))
    fig.add_trace(go.Bar(
        name="Aktueller Monat",
        x=categories,
        y=curr_vals,
        marker_color=curr_colors,
        text=[_format_chf(v) for v in curr_vals],
        textposition="outside",
        textfont=dict(size=13, color=_TEXT, family="Inter, sans-serif"),
        cliponaxis=False,
        width=bar_width,
    ))

    # Limit-Linien (nur über dem Balken der jeweiligen Kategorie)
    for i, cat in enumerate(categories):
        limit = stats[cat].get("limit")
        if limit is not None:
            fig.add_shape(
                type="line",
                x0=i - 0.4, x1=i + 0.4,
                y0=limit, y1=limit,
                line=dict(color=_RED, width=2, dash="dash"),
            )
            # Beschriftung, damit klar ist was die rote gestrichelte Linie bedeutet
            fig.add_annotation(
                x=i + 0.4, y=limit,
                xanchor="left", yanchor="middle",
                text=f"Limit: {_format_chf(limit)}",
                showarrow=False,
                font=dict(size=11, color=_RED, family="Inter, sans-serif"),
                xshift=4,
            )

    # 25% Platz über dem höchsten Balken, damit die Beschriftungen nicht abgeschnitten werden
    max_value = max([*prev_vals, *curr_vals, 0])
    y_max = max_value * 1.25 if max_value > 0 else 100

    fig.update_layout(
        barmode="group",
        paper_bgcolor="white",
        plot_bgcolor="white",
        margin=dict(t=30, b=60, l=60, r=120),
        height=400,
        legend=dict(
            orientation="h",
            y=-0.18,
            font=dict(size=13, color=_TEXT, family="Inter, sans-serif"),
        ),
        yaxis=dict(
            title=dict(text="CHF", font=dict(size=13, color=_TEXT)),
            gridcolor="#E2E8F0",
            tickfont=dict(size=12, color=_TEXT),
            range=[0, y_max],
            fixedrange=True,  # Y-Achsen-Zoom deaktivieren
        ),
        xaxis=dict(
            gridcolor="#E2E8F0",
            tickfont=dict(size=13, color=_TEXT, family="Inter, sans-serif"),
            fixedrange=True,  # X-Achsen-Zoom deaktivieren
        ),
        font=dict(family="Inter, sans-serif", color=_TEXT, size=13),
        bargap=0.3,
        bargroupgap=0.15,
        dragmode=False,  # Pan/Zoom mit der Maus deaktivieren
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

    income_vals = [income_by_month.get(m, 0) for m in all_months]
    expense_vals = [expense_by_month.get(m, 0) for m in all_months]

    bar_width = min(0.35, 0.7 / max(len(all_months), 1))

    fig = go.Figure()
    fig.add_trace(go.Bar(
        name="Einnahmen",
        x=all_months,
        y=income_vals,
        marker_color=_GREEN,
        text=[_format_chf(v) for v in income_vals],
        textposition="outside",
        textfont=dict(size=13, color=_TEXT, family="Inter, sans-serif"),
        cliponaxis=False,
        width=bar_width,
    ))
    fig.add_trace(go.Bar(
        name="Ausgaben",
        x=all_months,
        y=expense_vals,
        marker_color=_RED,
        text=[_format_chf(v) for v in expense_vals],
        textposition="outside",
        textfont=dict(size=13, color=_TEXT, family="Inter, sans-serif"),
        cliponaxis=False,
        width=bar_width,
    ))

    max_value = max([*income_vals, *expense_vals, 0])
    y_max = max_value * 1.25 if max_value > 0 else 100

    fig.update_layout(
        barmode="group",
        paper_bgcolor="white",
        plot_bgcolor="white",
        margin=dict(t=30, b=60, l=60, r=40),
        height=380,
        legend=dict(
            orientation="h",
            y=-0.18,
            font=dict(size=13, color=_TEXT, family="Inter, sans-serif"),
        ),
        yaxis=dict(
            title=dict(text="CHF", font=dict(size=13, color=_TEXT)),
            gridcolor="#E2E8F0",
            tickfont=dict(size=12, color=_TEXT),
            range=[0, y_max],
            fixedrange=True,
        ),
        xaxis=dict(
            gridcolor="#E2E8F0",
            tickfont=dict(size=13, color=_TEXT, family="Inter, sans-serif"),
            fixedrange=True,
        ),
        font=dict(family="Inter, sans-serif", color=_TEXT, size=13),
        bargap=0.3,
        bargroupgap=0.15,
        dragmode=False,
    )
    return fig


# ---------------------------------------------------------------------------
# Daten laden
# ---------------------------------------------------------------------------

def _load_user_data(email: str) -> dict:
    from models.data_storage import DataHandler
    dh = DataHandler()
    return dh.accounts.get(email, {})
