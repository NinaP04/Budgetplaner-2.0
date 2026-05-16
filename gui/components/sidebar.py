"""Shared left navigation drawer for authenticated pages."""

from nicegui import ui


def create_sidebar(active_page: str = "dashboard"):
    with ui.left_drawer(
        value=True,
        fixed=True,
        bordered=False,
        top_corner=True,
        bottom_corner=True,
    ).classes("p-0 w-[240px] border-none bg-[#0098DA]"):
        with ui.column().classes("w-full gap-0 pt-7 pb-4 px-6"):
            with ui.row().classes("items-center gap-2 no-wrap"):
                with ui.element("div").classes(
                    "flex items-center justify-center w-9 h-9 rounded-xl "
                    "bg-white/15 backdrop-blur-sm"
                ):
                    ui.icon("account_balance_wallet",
                            size="20px").classes("text-white")
                with ui.row().classes("items-baseline gap-0"):
                    ui.label("FinFlow").classes(
                        "text-2xl font-bold text-white tracking-tight leading-none"
                    )
                    ui.label(".").classes(
                        "text-2xl font-bold text-white/50 leading-none"
                    )
            ui.element("div").classes("w-full mt-5 h-px bg-white/15")

        with ui.column().classes("w-full gap-1 flex-grow px-3 pt-2"):
            _nav_item("home", "Dashboard", "/", active_page == "dashboard")
            _nav_item(
                "category", "Kategorie", "/kategorien", active_page == "kategorien"
            )
            _nav_item(
                "analytics", "Statistik", "/statistik", active_page == "statistik"
            )

        with ui.column().classes("w-full p-3"):
            ui.element("div").classes("w-full mb-2 h-px bg-white/15")
            _nav_item(
                "settings",
                "Einstellungen",
                "/einstellungen",
                active_page == "einstellungen",
            )


def _nav_item(icon: str, label: str, target: str, active: bool = False):
    active_cls = "bg-white/20" if active else "bg-transparent"
    weight = "font-semibold" if active else "font-normal"

    with (
        ui.row()
        .classes(
            f"w-full items-center gap-3 cursor-pointer rounded-lg "
            f"px-3.5 py-2.5 transition-colors duration-200 nav-item {active_cls}"
        )
        .on("click", lambda t=target: ui.navigate.to(t))
    ):
        ui.icon(icon, size="20px").classes("text-white")
        ui.label(label).classes(f"text-white text-sm {weight}")
