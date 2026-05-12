"""Register page — /register."""

from nicegui import ui

from gui.theme import apply_theme
from gui.services import get_auth_service


@ui.page("/register")
def register():
    apply_theme()

    auth_service = get_auth_service()

    ui.add_head_html("""<style>
        .nicegui-content { padding: 0 !important; max-width: 100% !important; }
        .q-page { padding: 0 !important; }
    </style>""")

    vorname_input = None
    name_input = None
    email_input = None
    password_input = None
    password_confirm_input = None
    error_label = None

    validation_hints = {
        "length": None,
        "uppercase": None,
        "number": None,
        "special": None,
    }

    SPECIAL_CHARS = "!@#%?&*"

    def _set_hint(key: str, passed: bool):
        hint = validation_hints[key]
        hint["icon"].set_text("check_circle" if passed else "cancel")
        hint["icon"].classes(
            "text-green-500" if passed else "text-red-400",
            remove="text-green-500 text-red-400",
        )

    def validate_password_live(_e):
        password = password_input.value or ""
        _set_hint("length", len(password) >= 8)
        _set_hint("uppercase", any(c.isupper() for c in password))
        _set_hint("number", any(c.isdigit() for c in password))
        _set_hint("special", any(c in SPECIAL_CHARS for c in password))

    async def handle_register():
        vorname = vorname_input.value.strip()
        name = name_input.value.strip()
        email = email_input.value.strip()
        password = password_input.value
        password_confirm = password_confirm_input.value

        error_label.set_text("")
        error_label.set_visibility(False)

        if password != password_confirm:
            error_label.set_text("Die Passwörter stimmen nicht überein!")
            error_label.set_visibility(True)
            return

        success, message = auth_service.register_user(vorname, name, email, password)

        if success:
            ui.notify(message, type="positive")
            ui.navigate.to("/login")
        else:
            error_label.set_text(message)
            error_label.set_visibility(True)

    with ui.element("div").classes(
        "min-h-screen w-full flex justify-center items-center bg-gray-50"
    ):
        with ui.card().classes(
            "p-8 border border-gray-300 rounded min-w-[380px] max-w-[460px]"
        ):
            ui.label("FinFlow").classes("text-2xl font-bold text-[#0098DA] mb-1")
            ui.label("Konto erstellen").classes(
                "text-base font-semibold text-gray-700 mb-5"
            )

            error_label = ui.label("").classes("text-sm text-red-500 mb-3")
            error_label.set_visibility(False)

            vorname_input = (
                ui.input(placeholder="Vorname")
                .props("outlined dense")
                .classes("w-full mb-3")
            )
            name_input = (
                ui.input(placeholder="Nachname")
                .props("outlined dense")
                .classes("w-full mb-3")
            )
            email_input = (
                ui.input(placeholder="E-Mail")
                .props("outlined dense")
                .classes("w-full mb-3")
            )
            password_input = (
                ui.input(
                    placeholder="Passwort",
                    password=True,
                    password_toggle_button=True,
                )
                .props("outlined dense")
                .classes("w-full mb-1")
            )

            password_input.on("input", validate_password_live)

            password_confirm_input = (
                ui.input(
                    placeholder="Passwort bestätigen",
                    password=True,
                    password_toggle_button=True,
                )
                .props("outlined dense")
                .classes("w-full mb-5")
            )

            password_confirm_input.on("keydown.enter", handle_register)

            ui.button(
                "Registrieren",
                on_click=handle_register,
            ).props("unelevated color=primary no-caps").classes("w-full")

            with ui.row().classes("w-full justify-center items-center mt-4 gap-1"):
                ui.label("Bereits ein Konto?").classes("text-sm text-gray-500")
                ui.link("Anmelden", "/login").classes(
                    "text-sm font-semibold no-underline text-[#0098DA]"
                )
