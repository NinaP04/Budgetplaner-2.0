"""Shared top header bar for authenticated pages."""

from nicegui import ui

from gui.services import get_session_manager


def create_header(title: str, subtitle: str):
    session = get_session_manager()
    user = session.get_current_user() or {}
    vorname = user.get("vorname", "")
    name = user.get("name", "")
    email = user.get("email", "")
    full_name = f"{vorname} {name}".strip() or "Benutzer"

    with ui.header(elevated=False).classes(
        "items-center justify-between px-8 bg-white h-[64px] border-b border-gray-200"
    ):
        with ui.column().classes("gap-0"):
            ui.label(title).classes("text-lg font-bold text-[#0098DA] leading-tight")
            ui.label(subtitle).classes(
                "text-xs text-[#0098DA] opacity-65 leading-tight"
            )

        with ui.row().classes("items-center gap-4"):
            with ui.column().classes("gap-0 items-end"):
                ui.label(full_name).classes(
                    "text-sm font-semibold text-[#1A1A2E] leading-tight"
                )
                ui.label(email).classes("text-xs text-[#6B7280] leading-tight")

            with ui.element("div").classes(
                "flex items-center justify-center rounded-full "
                "w-[38px] h-[38px] bg-[#0098DA]"
            ):
                ui.icon("person_outline", size="22px").classes("text-white")

            ui.element("div").classes("w-px h-8 bg-[#E2E8F0]")

            def _logout():
                session.logout()
                ui.navigate.to("/login")

            ui.button(icon="logout", on_click=_logout).props("flat round").classes(
                "text-[#6B7280]"
            ).tooltip("Abmelden")
