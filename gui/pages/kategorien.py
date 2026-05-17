"""Kategorien-Seite — /kategorien. Verwaltet Budgetkategorien und ihre Einträge."""

from datetime import date, datetime

from nicegui import ui

from gui.theme import apply_theme
from gui.components.sidebar import create_sidebar
from gui.components.header import create_header
from gui.services import get_budget_service, get_session_manager


# Monatsnamen auf Deutsch für die Dropdown-Anzeige
_MONTH_NAMES_DE = [
    "Januar", "Februar", "März", "April", "Mai", "Juni",
    "Juli", "August", "September", "Oktober", "November", "Dezember",
]


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
    create_header(title="Kategorien",
                  subtitle="Ihre Budgetkategorien verwalten")

    with ui.column().classes("w-full p-10 gap-6"):
        _categories_card(email)


def _categories_card(email: str):
    # Ausgewählter Monat als veränderlicher State (heute als Default)
    today = date.today()
    state = {"year": today.year, "month": today.month}

    with ui.row().classes("items-center justify-between w-full mt-2"):
        # Monatsauswahl links
        with ui.row().classes("items-center gap-3"):
            ui.label("Monat:").classes("text-sm text-gray-600 font-medium")
            month_select = ui.select(
                options=_month_options(email),
                value=_month_key(state["year"], state["month"]),
            ).props("outlined dense").classes("min-w-[180px]")

        # Neue Kategorie hinzufügen rechts
        ui.button(
            "+ Kategorie hinzufügen",
            on_click=lambda: _open_add_dialog(email, refresh),
        ).props("color=primary unelevated").classes("text-sm")

    container = ui.column().classes("w-full gap-4 mt-2")

    def refresh():
        # Dropdown-Optionen neu erzeugen (falls neue Einträge in anderen
        # Monaten dazugekommen sind), aktuelle Auswahl beibehalten
        opts = _month_options(email)
        current = _month_key(state["year"], state["month"])
        month_select.options = opts
        if current not in opts:
            # Falls der gewählte Monat keine Einträge mehr hat, auf aktuellen Monat zurück
            today_local = date.today()
            state["year"] = today_local.year
            state["month"] = today_local.month
            current = _month_key(state["year"], state["month"])
            if current not in opts and opts:
                current = next(iter(opts.keys()))
                y, m = _parse_month_key(current)
                state["year"] = y
                state["month"] = m
        month_select.value = current
        month_select.update()

        container.clear()
        with container:
            _render_categories(email, state["year"], state["month"], refresh)

    def on_month_change(e):
        if not e.value:
            return
        y, m = _parse_month_key(e.value)
        state["year"] = y
        state["month"] = m
        container.clear()
        with container:
            _render_categories(email, state["year"], state["month"], refresh)

    month_select.on_value_change(on_month_change)

    refresh()


# ---------------------------------------------------------------------------
# Monats-Hilfsfunktionen
# ---------------------------------------------------------------------------

def _month_key(year: int, month: int) -> str:
    return f"{year:04d}-{month:02d}"


def _parse_month_key(key: str) -> tuple[int, int]:
    y, m = key.split("-")
    return int(y), int(m)


def _format_month_label(year: int, month: int) -> str:
    return f"{_MONTH_NAMES_DE[month - 1]} {year}"


def _month_options(email: str) -> dict:
    """Erstellt die Dropdown-Optionen: alle Monate, in denen es Einträge gibt,
    plus immer den aktuellen Monat — absteigend sortiert (neueste zuerst)."""
    service = get_budget_service()
    categories = service.list_categories(email)

    months: set[tuple[int, int]] = set()
    today = date.today()
    months.add((today.year, today.month))  # aktuellen Monat immer anzeigen

    for cat in categories:
        for entry in cat["entries"]:
            try:
                d = datetime.strptime(entry["datum"], "%d.%m.%Y").date()
                months.add((d.year, d.month))
            except ValueError:
                continue

    # absteigend sortieren: neueste Monate zuerst
    sorted_months = sorted(months, reverse=True)
    return {_month_key(y, m): _format_month_label(y, m) for y, m in sorted_months}


def _filter_entries_by_month(entries: list[dict], year: int, month: int) -> list[dict]:
    """Behält nur Einträge im gewählten Monat (und behält den Original-Index!)."""
    result = []
    for e in entries:
        try:
            d = datetime.strptime(e["datum"], "%d.%m.%Y").date()
        except ValueError:
            continue
        if d.year == year and d.month == month:
            result.append(e)
    return result


# ---------------------------------------------------------------------------
# Rendering
# ---------------------------------------------------------------------------

def _render_categories(email: str, year: int, month: int, refresh):
    service = get_budget_service()
    categories = service.list_categories(email)

    if not categories:
        ui.label("Noch keine Kategorien vorhanden.").classes(
            "text-sm text-gray-500")
        return

    for cat in categories:
        _render_category_card(email, cat, year, month, refresh)


def _render_category_card(email: str, cat: dict, year: int, month: int, refresh):
    # Auf den gewählten Monat einschränken
    month_entries = _filter_entries_by_month(cat["entries"], year, month)
    month_spent = sum(e["betrag"] for e in month_entries)

    limit = cat["limit"]
    over = limit is not None and month_spent > limit
    spent_color = "#EF4444" if over else "#1A1A2E"
    limit_text = f"CHF {limit:.2f}" if limit is not None else "—"

    with ui.card().classes(
        "w-full p-5 border border-gray-300 rounded"
    ):
        with ui.row().classes("items-center justify-between w-full"):
            ui.label(cat["name"]).classes(
                "text-lg font-semibold text-[#0098DA]")
            with ui.row().classes("gap-1"):
                ui.button(
                    "+ Eintrag erfassen",
                    on_click=lambda e, n=cat["name"]: _open_entry_dialog(
                        email, n, year, month, refresh
                    ),
                ).props("flat color=primary dense").classes("text-xs")
                ui.button(
                    icon="delete",
                    on_click=lambda e, n=cat["name"]: _confirm_delete_category(
                        email, n, refresh
                    ),
                ).props("flat dense round color=negative")

        with ui.row().classes("items-center gap-6 mt-1 mb-3"):
            with ui.column().classes("gap-0"):
                ui.label("Monatslimit").classes("text-xs text-gray-500")
                with ui.row().classes("items-center gap-1"):
                    ui.label(limit_text).classes(
                        "text-sm font-medium text-gray-800")
                    ui.button(
                        icon="edit",
                        on_click=lambda e, n=cat["name"], cur=limit: _open_limit_dialog(
                            email, n, cur, refresh
                        ),
                    ).props("flat dense round size=xs color=grey")
            with ui.column().classes("gap-0"):
                ui.label(f"Ausgaben ({_format_month_label(year, month)})").classes(
                    "text-xs text-gray-500"
                )
                ui.label(f"CHF {month_spent:.2f}").classes(
                    "text-sm font-semibold"
                ).style(f"color: {spent_color}")

        _render_entries(email, cat["name"], month_entries, refresh)


def _render_entries(email: str, category: str, entries: list[dict], refresh):
    if not entries:
        ui.label("Keine Einträge in diesem Monat.").classes(
            "text-xs text-gray-500")
        return

    # Einträge nach Datum absteigend sortieren (neueste oben)
    sorted_entries = sorted(
        entries,
        key=lambda e: datetime.strptime(e["datum"], "%d.%m.%Y"),
        reverse=True,
    )

    # Kopfzeile
    with ui.row().classes(
        "w-full items-center px-3 py-2 border-b border-gray-200"
    ):
        ui.label("Datum").classes("text-xs font-semibold text-gray-600 w-28")
        ui.label("Name").classes(
            "text-xs font-semibold text-gray-600 flex-grow")
        ui.label("Betrag (CHF)").classes(
            "text-xs font-semibold text-gray-600 w-32 text-right"
        )
        ui.label("").classes("w-20")  # Platz für Buttons

    # Datenzeilen
    for entry in sorted_entries:
        with ui.row().classes(
            "w-full items-center px-3 py-2 border-b border-gray-100 hover:bg-gray-50"
        ):
            ui.label(entry["datum"]).classes("text-sm text-gray-700 w-28")
            ui.label(entry["art"]).classes("text-sm text-gray-800 flex-grow")
            ui.label(f"{entry['betrag']:.2f}").classes(
                "text-sm text-gray-800 w-32 text-right"
            )
            with ui.row().classes("w-20 gap-0 justify-end"):
                ui.button(
                    icon="edit",
                    on_click=lambda e, ent=entry: _open_edit_entry_dialog(
                        email, category, ent, refresh
                    ),
                ).props("flat dense round size=sm color=primary")
                ui.button(
                    icon="delete",
                    on_click=lambda e, ent=entry: _confirm_delete_entry(
                        email, category, ent, refresh
                    ),
                ).props("flat dense round size=sm color=negative")


# ---------------------------------------------------------------------------
# Dialoge: Kategorie
# ---------------------------------------------------------------------------

def _confirm_delete_category(email: str, name: str, refresh):
    service = get_budget_service()

    with ui.dialog() as dialog, ui.card().classes(
        "p-6 border border-gray-300 rounded"
    ):
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


def _open_add_dialog(email: str, refresh):
    service = get_budget_service()

    with ui.dialog() as dialog, ui.card().classes(
        "p-6 border border-gray-300 rounded w-96"
    ):
        ui.label("Neue Kategorie").classes(
            "text-base font-semibold text-gray-800 mb-2"
        )
        name_input = ui.input("Name").classes("w-full")
        limit_input = ui.number("Monatslimit in CHF (optional)", format="%.2f").classes(
            "w-full"
        )

        with ui.row().classes("justify-end gap-2 w-full mt-4"):
            ui.button("Abbrechen", on_click=dialog.close).props("flat")

            def do_add():
                limit_val = limit_input.value
                limit = float(limit_val) if limit_val not in (
                    None, "") else None
                ok, msg = service.add_category(
                    email, name_input.value or "", limit)
                ui.notify(msg, type="positive" if ok else "negative")
                if ok:
                    dialog.close()
                    refresh()

            ui.button("Hinzufügen", on_click=do_add).props("color=primary")

    dialog.open()


def _open_limit_dialog(email: str, category: str, current_limit, refresh):
    service = get_budget_service()

    with ui.dialog() as dialog, ui.card().classes(
        "p-6 border border-gray-300 rounded w-80"
    ):
        ui.label(f"Monatslimit bearbeiten — {category}").classes(
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


# ---------------------------------------------------------------------------
# Dialoge: Eintrag
# ---------------------------------------------------------------------------

def _open_entry_dialog(email: str, category: str, year: int, month: int, refresh):
    """Neuen Eintrag erfassen. Default-Datum ist im gerade gewählten Monat."""
    service = get_budget_service()

    # Default-Datum: heute, falls heute im gewählten Monat ist, sonst der 1. des Monats
    today = date.today()
    if today.year == year and today.month == month:
        default_date = today.strftime("%d.%m.%Y")
    else:
        default_date = date(year, month, 1).strftime("%d.%m.%Y")

    with ui.dialog() as dialog, ui.card().classes(
        "p-6 border border-gray-300 rounded w-96"
    ):
        ui.label(f"Eintrag erfassen — {category}").classes(
            "text-base font-semibold text-gray-800 mb-2"
        )
        datum_input = ui.input(
            "Datum (DD.MM.YYYY)",
            value=default_date,
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


def _open_edit_entry_dialog(email: str, category: str, entry: dict, refresh):
    """Bestehenden Eintrag bearbeiten — Felder mit Originalwerten vorausgefüllt."""
    service = get_budget_service()

    with ui.dialog() as dialog, ui.card().classes(
        "p-6 border border-gray-300 rounded w-96"
    ):
        ui.label(f"Eintrag bearbeiten — {category}").classes(
            "text-base font-semibold text-gray-800 mb-2"
        )
        datum_input = ui.input(
            "Datum (DD.MM.YYYY)",
            value=entry["datum"],
        ).classes("w-full")
        art_input = ui.input(
            "Name",
            value=entry["art"],
        ).classes("w-full")
        betrag_input = ui.number(
            "Betrag (CHF)",
            format="%.2f",
            min=0.01,
            value=entry["betrag"],
        ).classes("w-full")

        with ui.row().classes("justify-end gap-2 w-full mt-4"):
            ui.button("Abbrechen", on_click=dialog.close).props("flat")

            def do_save():
                ok, msg = service.update_entry(
                    email,
                    category,
                    entry["index"],
                    datum_input.value or "",
                    art_input.value or "",
                    betrag_input.value,
                )
                ui.notify(msg, type="positive" if ok else "negative")
                if ok:
                    dialog.close()
                    refresh()

            ui.button("Speichern", on_click=do_save).props("color=primary")

    dialog.open()


def _confirm_delete_entry(email: str, category: str, entry: dict, refresh):
    """Bestätigungsdialog vor dem Löschen eines Eintrags."""
    service = get_budget_service()

    with ui.dialog() as dialog, ui.card().classes(
        "p-6 border border-gray-300 rounded"
    ):
        ui.label("Eintrag löschen?").classes(
            "text-base font-semibold text-gray-800"
        )
        ui.label(
            f"{entry['datum']} — {entry['art']} — CHF {entry['betrag']:.2f}"
        ).classes("text-sm text-[#6B7280] mb-4")
        with ui.row().classes("justify-end gap-2 w-full"):
            ui.button("Abbrechen", on_click=dialog.close).props("flat")

            def do_delete():
                ok, msg = service.delete_entry(email, category, entry["index"])
                ui.notify(msg, type="positive" if ok else "negative")
                dialog.close()
                if ok:
                    refresh()

            ui.button("Löschen", on_click=do_delete).props("color=negative")

    dialog.open()
