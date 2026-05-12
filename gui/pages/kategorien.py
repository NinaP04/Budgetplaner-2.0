"""Kategorien page — /kategorien. Manage budget categories and their entries."""

from nicegui import ui

from gui.theme import apply_theme
from gui.components.sidebar import create_sidebar
from gui.components.header import create_header
from gui.services import get_budget_service, get_session_manager


@ui.page("/kategorien")
def kategorien():
    apply_theme()
    ui.query("body").classes("bg-gray-50")

    session = get_session_manager()
    if not session.is_authenticated():
        ui.navigate.to("/login")
        return

    user = session.get_current_user() or {}
    email = user.get("email", "")

    create_sidebar(active_page="kategorien")
    create_header(title="Kategorien", subtitle="Ihre Budgetkategorien verwalten")

    with ui.column().classes("w-full p-10 gap-6"):
        _categories_card(email)


def _categories_card(email: str):
    with ui.row().classes("items-center justify-between w-full mt-2"):
        ui.button(
            "+ Kategorie hinzufügen",
            on_click=lambda: _open_add_dialog(email, refresh),
        ).props("color=primary unelevated").classes("text-sm")

    container = ui.column().classes("w-full gap-4 mt-2")

    def refresh():
        container.clear()
        with container:
            _render_categories(email, refresh)

    refresh()


def _render_categories(email: str, refresh):
    service = get_budget_service()
    categories = service.list_categories(email)

    if not categories:
        ui.label("Noch keine Kategorien vorhanden.").classes("text-sm text-gray-500")
        return

    for cat in categories:
        _render_category_card(email, cat, refresh)


def _render_category_card(email: str, cat: dict, refresh):
    limit = cat["limit"]
    spent = cat["spent"]
    over = limit is not None and spent > limit
    spent_color = "#EF4444" if over else "#1A1A2E"
    limit_text = f"CHF {limit:.2f}" if limit is not None else "—"

    with ui.card().classes(
        "w-full p-5 border border-gray-300 rounded"
    ):
        with ui.row().classes("items-center justify-between w-full"):
            ui.label(cat["name"]).classes("text-lg font-semibold text-[#0098DA]")
            with ui.row().classes("gap-1"):
                ui.button(
                    "+ Erfassen",
                    on_click=lambda e, n=cat["name"]: _open_entry_dialog(
                        email, n, refresh
                    ),
                ).props("flat color=primary dense").classes("text-xs")
                ui.button(
                    icon="delete",
                    on_click=lambda e, n=cat["name"]: _confirm_delete(
                        email, n, refresh
                    ),
                ).props("flat dense round color=negative")

        with ui.row().classes("items-center gap-6 mt-1 mb-3"):
            with ui.column().classes("gap-0"):
                ui.label("Limit").classes("text-xs text-gray-500")
                with ui.row().classes("items-center gap-1"):
                    ui.label(limit_text).classes("text-sm font-medium text-gray-800")
                    ui.button(
                        icon="edit",
                        on_click=lambda e, n=cat["name"], cur=limit: _open_limit_dialog(
                            email, n, cur, refresh
                        ),
                    ).props("flat dense round size=xs color=grey")
            with ui.column().classes("gap-0"):
                ui.label("Ausgaben").classes("text-xs text-gray-500")
                ui.label(f"CHF {spent:.2f}").classes("text-sm font-semibold").style(
                    f"color: {spent_color}"
                )

        _render_entries(cat["entries"])


def _render_entries(entries: list[dict]):
    if not entries:
        ui.label("Noch keine Einträge.").classes("text-xs text-gray-500")
        return

    columns = [
        {"name": "datum", "label": "Datum", "field": "datum", "align": "left"},
        {"name": "art", "label": "Name", "field": "art", "align": "left"},
        {
            "name": "betrag",
            "label": "Betrag (CHF)",
            "field": "betrag",
            "align": "right",
        },
    ]
    rows = [
        {"datum": e["datum"], "art": e["art"], "betrag": f"{e['betrag']:.2f}"}
        for e in entries
    ]
    ui.table(columns=columns, rows=rows, row_key="datum").classes("w-full").props(
        "flat dense"
    )


def _confirm_delete(email: str, name: str, refresh):
    service = get_budget_service()

    with ui.dialog() as dialog, ui.card().classes("p-6 border border-gray-300 rounded"):
        ui.label(f"Kategorie '{name}' löschen?").classes(
            "text-base font-semibold text-gray-800"
        )
        ui.label("Alle Einträge und das Limit werden entfernt.").classes(
            "text-sm text-[#6B7280] mb-4"
        )
        with ui.row().classes("justify-end gap-2 w-full"):
            ui.button("Abbrechen", on_click=dialog.close).props("flat")

            def do_delete():
                ok, msg = service.delete_category(email, name)
                ui.notify(msg, type="positive" if ok else "negative")
                dialog.close()
                if ok:
                    refresh()

            ui.button("Löschen", on_click=do_delete).props("color=negative")

    dialog.open()


def _open_entry_dialog(email: str, category: str, refresh):
    from datetime import date as _date

    service = get_budget_service()

    with ui.dialog() as dialog, ui.card().classes("p-6 border border-gray-300 rounded w-96"):
        ui.label(f"Ausgabe hinzufügen — {category}").classes(
            "text-base font-semibold text-gray-800 mb-2"
        )
        datum_input = ui.input(
            "Datum (DD.MM.YYYY)",
            value=_date.today().strftime("%d.%m.%Y"),
        ).classes("w-full")
        art_input = ui.input("Name (z. B. Miete, Einkauf)").classes("w-full")
        betrag_input = ui.number("Betrag (CHF)", format="%.2f", min=0.01).classes(
            "w-full"
        )

        with ui.row().classes("justify-end gap-2 w-full mt-4"):
            ui.button("Abbrechen", on_click=dialog.close).props("flat")

            def do_add():
                ok, msg = service.add_entry(
                    email,
                    category,
                    datum_input.value or "",
                    art_input.value or "",
                    betrag_input.value,
                )
                ui.notify(msg, type="positive" if ok else "negative")
                if ok:
                    dialog.close()
                    refresh()

            ui.button("Hinzufügen", on_click=do_add).props("color=primary")

    dialog.open()


def _open_add_dialog(email: str, refresh):
    service = get_budget_service()

    with ui.dialog() as dialog, ui.card().classes("p-6 border border-gray-300 rounded w-96"):
        ui.label("Neue Kategorie").classes(
            "text-base font-semibold text-gray-800 mb-2"
        )
        name_input = ui.input("Name").classes("w-full")
        limit_input = ui.number("Limit in CHF (optional)", format="%.2f").classes(
            "w-full"
        )

        with ui.row().classes("justify-end gap-2 w-full mt-4"):
            ui.button("Abbrechen", on_click=dialog.close).props("flat")

            def do_add():
                limit_val = limit_input.value
                limit = float(limit_val) if limit_val not in (None, "") else None
                ok, msg = service.add_category(email, name_input.value or "", limit)
                ui.notify(msg, type="positive" if ok else "negative")
                if ok:
                    dialog.close()
                    refresh()

            ui.button("Hinzufügen", on_click=do_add).props("color=primary")

    dialog.open()


def _open_limit_dialog(email: str, category: str, current_limit, refresh):
    service = get_budget_service()

    with ui.dialog() as dialog, ui.card().classes("p-6 border border-gray-300 rounded w-80"):
        ui.label(f"Limit bearbeiten — {category}").classes(
            "text-base font-semibold text-gray-800 mb-2"
        )
        limit_input = ui.number(
            "Limit in CHF",
            format="%.2f",
            value=current_limit,
        ).classes("w-full")

        with ui.row().classes("justify-end gap-2 w-full mt-4"):
            ui.button("Abbrechen", on_click=dialog.close).props("flat")

            def do_save():
                val = limit_input.value
                if val in (None, ""):
                    ui.notify("Bitte einen Betrag eingeben.", type="warning")
                    return
                ok, msg = service.set_limit(email, category, float(val))
                ui.notify(msg, type="positive" if ok else "negative")
                if ok:
                    dialog.close()
                    refresh()

            ui.button("Speichern", on_click=do_save).props("color=primary")

    dialog.open()
