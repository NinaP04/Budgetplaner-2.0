"""Einstellungen page — /einstellungen. Section cards for account settings."""

from nicegui import ui

from gui.theme import apply_theme
from gui.components.sidebar import create_sidebar
from gui.components.header import create_header
from gui.services import get_account_service, get_session_manager


@ui.page("/einstellungen")
def einstellungen():
    apply_theme()
    ui.query("body").classes("bg-gray-50")

    session = get_session_manager()
    if not session.is_authenticated():
        ui.navigate.to("/login")
        return

    create_sidebar(active_page="einstellungen")
    create_header(title="Einstellungen", subtitle="Ihre persönlichen Einstellungen")

    with ui.column().classes("w-full p-8 gap-4"):
        ui.label("Einstellungen").classes("text-2xl font-bold text-[#0098DA]")

        with ui.column().classes("w-full mt-4 gap-3"):
            _profil_section(session)
            _sicherheit_section(session)


def _profil_section(session):
    with ui.card().classes(
        "w-full p-5 border border-gray-300 rounded cursor-pointer"
    ).on("click", lambda: _open_profil_dialog(session)):
        with ui.row().classes("items-center gap-4 w-full"):
            ui.icon("person_outline", size="22px").classes("text-[#0098DA]")
            with ui.column().classes("gap-0 flex-grow"):
                ui.label("Profil").classes("text-sm font-semibold text-gray-800")
                ui.label("Name und E-Mail verwalten").classes("text-xs text-gray-500")
            ui.icon("chevron_right", size="20px").classes("text-gray-400")


def _open_profil_dialog(session):
    user = session.get_current_user() or {}
    email = user.get("email", "")

    account_service = get_account_service()
    profile = account_service.get_profile(email)

    with ui.dialog() as dialog, ui.card().classes("p-6 border border-gray-300 rounded w-[400px]"):
        ui.label("Profil bearbeiten").classes("text-base font-semibold text-gray-800 mb-4")

        vorname_input = ui.input("Vorname", value=profile.get("vorname", "")).classes("w-full")
        name_input = ui.input("Nachname", value=profile.get("name", "")).classes("w-full")

        ui.separator().classes("my-2")

        email_input = ui.input("E-Mail", value=profile.get("email", "")).classes("w-full")
        ui.label("E-Mail ändern erfordert eine erneute Sitzungsaktivierung.").classes(
            "text-xs text-gray-400 mt-1"
        )

        with ui.row().classes("justify-end gap-2 w-full mt-5"):
            ui.button("Abbrechen", on_click=dialog.close).props("flat")

            def do_save():
                current_email = email
                new_vorname = vorname_input.value or ""
                new_name = name_input.value or ""
                new_email = (email_input.value or "").strip().lower()

                if new_vorname != profile.get("vorname") or new_name != profile.get("name"):
                    ok, msg = account_service.update_profile(current_email, new_vorname, new_name)
                    if not ok:
                        ui.notify(msg, type="negative")
                        return

                active_email = current_email
                if new_email and new_email != current_email:
                    ok, msg, updated_email = account_service.change_email(current_email, new_email)
                    if not ok:
                        ui.notify(msg, type="negative")
                        return
                    active_email = updated_email

                fresh_user = account_service.get_profile(active_email)
                session.login({
                    "email": active_email,
                    "vorname": fresh_user.get("vorname", ""),
                    "name": fresh_user.get("name", ""),
                })

                ui.notify("Profil gespeichert.", type="positive")
                dialog.close()
                ui.navigate.to("/einstellungen")

            ui.button("Speichern", on_click=do_save).props("color=primary")

    dialog.open()


def _sicherheit_section(session):
    with ui.card().classes(
        "w-full p-5 border border-gray-300 rounded cursor-pointer"
    ).on("click", lambda: _open_passwort_dialog(session)):
        with ui.row().classes("items-center gap-4 w-full"):
            ui.icon("lock_outline", size="22px").classes("text-[#0098DA]")
            with ui.column().classes("gap-0 flex-grow"):
                ui.label("Sicherheit").classes("text-sm font-semibold text-gray-800")
                ui.label("Passwort ändern").classes("text-xs text-gray-500")
            ui.icon("chevron_right", size="20px").classes("text-gray-400")


def _open_passwort_dialog(session):
    user = session.get_current_user() or {}
    email = user.get("email", "")
    account_service = get_account_service()

    with ui.dialog() as dialog, ui.card().classes("p-6 border border-gray-300 rounded w-[400px]"):
        ui.label("Passwort ändern").classes("text-base font-semibold text-gray-800 mb-4")

        current_pw = ui.input(
            "Aktuelles Passwort", password=True, password_toggle_button=True
        ).classes("w-full")
        new_pw = ui.input(
            "Neues Passwort", password=True, password_toggle_button=True
        ).classes("w-full")
        confirm_pw = ui.input(
            "Neues Passwort bestätigen", password=True, password_toggle_button=True
        ).classes("w-full")

        ui.label("Min. 8 Zeichen, 1 Grossbuchstabe, 1 Zahl, 1 Sonderzeichen (!@#%?&*)").classes(
            "text-xs text-gray-400 mt-1"
        )

        with ui.row().classes("justify-end gap-2 w-full mt-5"):
            ui.button("Abbrechen", on_click=dialog.close).props("flat")

            def do_save():
                if new_pw.value != confirm_pw.value:
                    ui.notify("Passwörter stimmen nicht überein.", type="negative")
                    return
                ok, msg = account_service.change_password(
                    email, current_pw.value or "", new_pw.value or ""
                )
                ui.notify(msg, type="positive" if ok else "negative")
                if ok:
                    dialog.close()

            ui.button("Speichern", on_click=do_save).props("color=primary")

    dialog.open()
