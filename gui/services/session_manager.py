"""Session management for the NiceGUI UI.

Wraps NiceGUI's per-user storage to track the authenticated user and
enforce a 20-minute inactivity timeout. Parallel to (not replacing)
the CLI's InaktivitätsManager.
"""

from datetime import datetime
from typing import Optional

from nicegui import app, ui


class SessionManager:
    INACTIVITY_TIMEOUT = 1200  # 20 minutes

    def login(self, user_data: dict) -> None:
        app.storage.user['current_user'] = user_data
        app.storage.user['last_activity'] = datetime.now().isoformat()
        app.storage.user['is_authenticated'] = True

    def logout(self) -> None:
        app.storage.user.clear()

    def is_authenticated(self) -> bool:
        if not app.storage.user.get('is_authenticated'):
            return False

        last = app.storage.user.get('last_activity')
        if last:
            elapsed = (datetime.now() - datetime.fromisoformat(last)).total_seconds()
            if elapsed > self.INACTIVITY_TIMEOUT:
                self.logout()
                return False
        return True

    def get_current_user(self):
        return app.storage.user.get('current_user') if self.is_authenticated() else None

    def update_activity(self) -> None:
        app.storage.user['last_activity'] = datetime.now().isoformat()

    def require_auth(self, target_page: str = '/') -> bool:
        if not self.is_authenticated():
            ui.navigate.to(f'/login?redirect={target_page}')
            return False
        self.update_activity()
        return True


_session_manager: Optional[SessionManager] = None


def get_session_manager() -> SessionManager:
    global _session_manager
    if _session_manager is None:
        _session_manager = SessionManager()
    return _session_manager
