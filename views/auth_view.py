"""CLI view for authentication interactions."""


class AuthView:
    """Renders auth prompts and feedback in the terminal."""

    def __init__(self, input_func=input):
        self._input = input_func

    def prompt_email(self) -> str:
        return self._input("\033[34mE-Mail: \033[0m").strip().lower()

    def prompt_password(self, allow_reset: bool = False) -> str:
        label = "Passwort ('f' fuer Reset): " if allow_reset else "Passwort: "
        return self._input(f"\033[34m{label}\033[0m").strip()

    def prompt_new_password(self) -> tuple[str, str]:
        pw1 = self._input("\n\033[34mNeues Passwort: \033[0m")
        pw2 = self._input("\033[34mPasswort wiederholen: \033[0m")
        return pw1, pw2

    def prompt_reset_code(self) -> str:
        return self._input("\n\033[34mReset-Code eingeben: \033[0m").strip()

    def ask_create_account(self) -> bool:
        choice = self._input(
            "\033[34mNeues Konto anlegen? (Y/N): \033[0m").strip().lower()
        return choice == "y"

    @staticmethod
    def show_message(message: str, color: str = "34") -> None:
        print(f"\n\033[{color}m{message}\033[0m")

    @staticmethod
    def show_password_rules() -> None:
        print("\n\033[01mPasswort neu festlegen:\033[0m")
        print("- Mindestens 8 Zeichen")
        print("- Gross- und Kleinbuchstaben")
        print("- Mindestens 1 Zahl")
        print("- Mindestens 1 Sonderzeichen (!,@,#,%,?,&,*)")
