"""Anwendungseinstieg fuer den Budgetplaner im MVC-Aufbau."""

from controllers.main_controller import MainController


def main() -> None:
    controller = MainController()
    controller.start()


if __name__ == "__main__":
    main()
