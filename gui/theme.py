"""FinFlow theme: colors, fonts, and global CSS for the NiceGUI UI."""

from nicegui import ui

PRIMARY = '#0098DA'
PRIMARY_DARK = '#0077B6'
PRIMARY_LIGHT = '#33ADDE'
ACCENT = '#00B4D8'

WHITE = '#FFFFFF'
TEXT_DARK = '#1A1A2E'
TEXT_GRAY = '#6B7280'
TEXT_LIGHT = '#94A3B8'

SUCCESS = '#10B981'
ERROR = '#EF4444'

GLOBAL_CSS = """
@import url('https://fonts.googleapis.com/icon?family=Material+Icons');
@import url('https://fonts.googleapis.com/icon?family=Material+Icons+Outlined');

.nav-item:hover { background: rgba(255, 255, 255, 0.15) !important; }
"""


def apply_theme():
    ui.add_head_html(f'<style>{GLOBAL_CSS}</style>')
    ui.colors(primary=PRIMARY, secondary=PRIMARY_DARK, accent=ACCENT)
