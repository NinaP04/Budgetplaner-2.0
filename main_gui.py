"""NiceGUI entry point. Runs alongside main.py (the CLI)."""

from nicegui import ui

import gui.pages.login         # noqa: F401  →  /login
import gui.pages.register      # noqa: F401  →  /register
import gui.pages.dashboard     # noqa: F401  →  /
import gui.pages.kategorien    # noqa: F401  →  /kategorien
import gui.pages.statistik     # noqa: F401  →  /statistik
import gui.pages.einstellungen  # noqa: F401  →  /einstellungen


if __name__ in {'__main__', '__mp_main__'}:
    ui.run(
        title='FinFlow — Persönlicher Budgetplaner',
        port=8080,
        reload=False,
        storage_secret='change-me-in-production',
    )
