from typing import Optional, Dict, Any, List


class User:
    """Domänenmodell für Benutzer (MVC-kompatibel).

    Felder stimmen mit dem bestehenden Datenschema überein, damit
    bestehende Codepfade weiterhin `dict`-basierte Accounts nutzen können.
    """

    def __init__(
        self,
        email: str,
        vorname: str = "",
        name: str = "",
        passwort: Optional[str] = None,
        budget_kategorien: Optional[Dict[str, List[str]]] = None,
        budget_limits: Optional[Dict[str, float]] = None,
        finanzziele: Optional[Dict[str, Any]] = None,
        lohn: Optional[List[str]] = None,
    ) -> None:
        self.email = email
        self.vorname = vorname
        self.name = name
        self.passwort = passwort
        self.budget_kategorien = budget_kategorien or {}
        self.budget_limits = budget_limits or {}
        self.finanzziele = finanzziele or {}
        self.lohn = lohn or []

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "User":
        return cls(
            email=data.get("email", ""),
            vorname=data.get("vorname", ""),
            name=data.get("name", ""),
            passwort=data.get("passwort"),
            budget_kategorien=data.get("budget_kategorien", {}),
            budget_limits=data.get("budget_limits", {}),
            finanzziele=data.get("finanzziele", {}),
            lohn=data.get("lohn", []),
        )

    def to_dict(self) -> Dict[str, Any]:
        return {
            "email": self.email,
            "vorname": self.vorname,
            "name": self.name,
            "passwort": self.passwort,
            "budget_kategorien": self.budget_kategorien,
            "budget_limits": self.budget_limits,
            "finanzziele": self.finanzziele,
            "lohn": self.lohn,
        }

    # Hilfs-APIs für die Controller-Logik
    def add_lohn(self, datum: str, betrag: float) -> str:
        eintrag = f"{datum} - Lohn - {betrag} CHF"
        self.lohn.append(eintrag)
        return eintrag

    def add_category(self, name: str) -> None:
        if name in self.budget_kategorien:
            raise ValueError("Kategorie existiert bereits.")
        self.budget_kategorien[name] = []

    def add_entry_to_category(self, category: str, entry_str: str) -> None:
        if category not in self.budget_kategorien:
            raise KeyError("Kategorie existiert nicht.")
        self.budget_kategorien[category].append(entry_str)
