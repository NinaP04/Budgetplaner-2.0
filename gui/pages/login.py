"""Login page — /login."""

from nicegui import ui

from gui.theme import apply_theme
from gui.services import get_auth_service, get_session_manager


@ui.page('/login')
def login():
    apply_theme()

    auth_service = get_auth_service()
    session_manager = get_session_manager()

    ui.add_head_html('''<style>
        .nicegui-content { padding: 0 !important; max-width: 100% !important; }
        .q-page { padding: 0 !important; }
    </style>''')

    email_input = None
    password_input = None
    error_label = None

    async def handle_login():
        email = email_input.value.strip()
        password = password_input.value

        error_label.set_text('')
        error_label.set_visibility(False)

        success, message, user_data = auth_service.login_user(email, password)

        if success:
            session_manager.login(user_data)
            ui.notify(message, type='positive')
            ui.navigate.to('/')
        else:
            error_label.set_text(message)
            error_label.set_visibility(True)

    with ui.element('div').classes('min-h-screen w-full flex justify-center items-center bg-gray-50'):
        with ui.card().classes('p-8 border border-gray-300 rounded min-w-[360px]'):
            ui.label('FinFlow').classes('text-2xl font-bold text-[#0098DA] mb-1')
            ui.label('Willkommen zurück').classes('text-base font-semibold text-gray-700 mb-5')

            error_label = ui.label('').classes('text-sm text-red-500 mb-3')
            error_label.set_visibility(False)

            ui.label('E-Mail').classes('text-sm font-medium text-gray-700 mb-1')
            email_input = ui.input(
                placeholder='ihre@email.ch'
            ).props('outlined dense').classes('w-full mb-4')

            ui.label('Passwort').classes('text-sm font-medium text-gray-700 mb-1')
            password_input = ui.input(
                placeholder='Passwort',
                password=True,
                password_toggle_button=True,
            ).props('outlined dense').classes('w-full mb-6')

            password_input.on('keydown.enter', handle_login)

            ui.button(
                'Anmelden',
                on_click=handle_login,
            ).props('unelevated color=primary no-caps').classes('w-full')

            with ui.row().classes('w-full justify-center items-center mt-4 gap-1'):
                ui.label('Noch kein Konto?').classes('text-sm text-gray-500')
                ui.link('Registrieren', '/register').classes('text-sm font-semibold no-underline text-[#0098DA]')
