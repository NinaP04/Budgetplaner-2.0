"""Dashboard page — /."""

from datetime import date as _date

from nicegui import ui

from gui.theme import apply_theme
from gui.components.sidebar import create_sidebar
from gui.components.header import create_header
from gui.services import get_budget_service, get_session_manager


@ui.page("/")
def dashboard():
    apply_theme()
    ui.query("body").classes("bg-gray-50")

    session = get_session_manager()
    if not session.is_authenticated():
        ui.navigate.to("/login")
        return

    user = session.get_current_user() or {}
    email = user.get("email", "")

    create_sidebar(active_page="dashboard")
    create_header(title="Dashboard", subtitle="Übersicht Ihrer Finanzen")

    with ui.column().classes("w-full p-10 gap-6"):
        ui.label("Willkommen zurück").classes("text-3xl font-bold text-[#0098DA]")
        ui.label("Hier ist eine Übersicht Ihrer aktuellen Finanzen").classes(
            "text-sm text-[#0098DA] opacity-65"
        )

        _body(email)


def _body(email: str):
    service = get_budget_service()
    transactions = service.list_transactions(email)

    income = sum(t["betrag"] for t in transactions if t["typ"] == "einnahme")
    expenses = sum(t["betrag"] for t in transactions if t["typ"] == "ausgabe")

    summary_row = ui.row().classes("w-full gap-4 flex-nowrap")
    with summary_row:
        _summary_card("trending_up", "Einnahmen", f"CHF {income:,.2f}", "#10B981")
        _summary_card("trending_down", "Ausgaben", f"CHF {expenses:,.2f}", "#EF4444")

    container = ui.column().classes("w-full gap-0")

    def refresh():
        container.clear()
        with container:
            _transactions_card(email, refresh)

    refresh()


def _transactions_card(email: str, refresh):
    service = get_budget_service()
    transactions = service.list_transactions(email)
    categories = [c["name"] for c in service.list_categories(email)]

    with ui.card().classes(
        "w-full p-5 border border-gray-300 rounded"
    ):
        with ui.row().classes("items-center justify-between w-full mb-4"):
            ui.label("Transaktionen").classes(
                "text-base font-semibold text-gray-800"
            )
            with ui.row().classes("gap-2"):
                ui.button(
                    "+ Einnahme",
                    on_click=lambda: _income_dialog(email, refresh),
                ).props("color=positive unelevated").classes("text-sm")
                ui.button(
                    "+ Ausgabe",
                    on_click=lambda: _expense_dialog(email, categories, refresh),
                ).props("color=negative unelevated").classes("text-sm")

        if not transactions:
            ui.label("Noch keine Transaktionen vorhanden.").classes(
                "text-sm text-gray-500"
            )
            return

        columns = [
            {"name": "datum", "label": "Datum", "field": "datum", "align": "left", "sortable": True},
            {"name": "art", "label": "Name", "field": "art", "align": "left"},
            {"name": "kategorie", "label": "Kategorie", "field": "kategorie", "align": "left"},
            {"name": "betrag", "label": "Betrag (CHF)", "field": "betrag_fmt", "align": "right"},
        ]
        rows = []
        for t in transactions:
            rows.append({
                "datum": t["datum"],
                "art": t["art"],
                "kategorie": t["kategorie"],
                "betrag_fmt": f"{t['betrag']:,.2f}",
                "_typ": t["typ"],
            })

        table = ui.table(columns=columns, rows=rows, row_key="datum").classes(
            "w-full"
        ).props("flat")

        table.add_slot("body-cell-betrag", """
            <q-td :props="props">
                <span :style="{color: props.row._typ === 'einnahme' ? '#10B981' : '#EF4444',
                               fontWeight: '600'}">
                    {{ props.row._typ === 'einnahme' ? '+' : '-' }} {{ props.value }}
                </span>
            </q-td>
        """)
        table.add_slot("body-cell-kategorie", """
            <q-td :props="props">
                <q-badge :color="props.row._typ === 'einnahme' ? 'positive' : 'negative'"
                         text-color="white" :label="props.value" />
            </q-td>
        """)


def _income_dialog(email: str, refresh):
    service = get_budget_service()

    with ui.dialog() as dialog, ui.card().classes("p-6 border border-gray-300 rounded w-96"):
        ui.label("Einnahme hinzufügen").classes(
            "text-base font-semibold text-gray-800 mb-2"
        )
        datum_input = ui.input(
            "Datum (DD.MM.YYYY)", value=_date.today().strftime("%d.%m.%Y")
        ).classes("w-full")
        betrag_input = ui.number("Betrag (CHF)", format="%.2f", min=0.01).classes(
            "w-full"
        )

        with ui.row().classes("justify-end gap-2 w-full mt-4"):
            ui.button("Abbrechen", on_click=dialog.close).props("flat")

            def do_add():
                ok, msg = service.add_income(
                    email, datum_input.value or "", betrag_input.value
                )
                ui.notify(msg, type="positive" if ok else "negative")
                if ok:
                    dialog.close()
                    refresh()

            ui.button("Speichern", on_click=do_add).props("color=positive")

    dialog.open()


def _expense_dialog(email: str, categories: list[str], refresh):
    service = get_budget_service()

    with ui.dialog() as dialog, ui.card().classes("p-6 border border-gray-300 rounded w-96"):
        ui.label("Ausgabe hinzufügen").classes(
            "text-base font-semibold text-gray-800 mb-2"
        )
        datum_input = ui.input(
            "Datum (DD.MM.YYYY)", value=_date.today().strftime("%d.%m.%Y")
        ).classes("w-full")

        if categories:
            cat_select = ui.select(categories, label="Kategorie", value=categories[0]).classes("w-full")
        else:
            ui.label("Keine Kategorien vorhanden. Bitte zuerst eine Kategorie anlegen.").classes(
                "text-xs text-[#EF4444]"
            )
            cat_select = None

        art_input = ui.input("Name (z. B. Miete, Einkauf)").classes("w-full")
        betrag_input = ui.number("Betrag (CHF)", format="%.2f", min=0.01).classes(
            "w-full"
        )

        with ui.row().classes("justify-end gap-2 w-full mt-4"):
            ui.button("Abbrechen", on_click=dialog.close).props("flat")

            def do_add():
                if not cat_select:
                    ui.notify("Bitte zuerst eine Kategorie anlegen.", type="negative")
                    return
                ok, msg = service.add_entry(
                    email,
                    cat_select.value,
                    datum_input.value or "",
                    art_input.value or "",
                    betrag_input.value,
                )
                ui.notify(msg, type="positive" if ok else "negative")
                if ok:
                    dialog.close()
                    refresh()

            ui.button("Speichern", on_click=do_add).props("color=negative")

    dialog.open()


def _summary_card(icon: str, label: str, value: str, accent: str):
    with ui.card().classes("flex-1 p-4 border border-gray-300 rounded"):
        with ui.row().classes("items-center gap-3 w-full"):
            ui.icon(icon, size="24px").style(f"color: {accent}")
            with ui.column().classes("gap-0"):
                ui.label(label).classes("text-xs text-gray-500")
                ui.label(value).classes("text-xl font-bold")
