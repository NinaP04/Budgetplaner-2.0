---

# FinFlow - Budgetplaner (Browser App)

---

![UI Showcase](docs/ui-images/ui_showcase.png)

---

This project is intended to:

- Practice the complete process from **application requirements analysis to implementation**
- Apply advanced **Python** concepts in a browser-based application (NiceGUI)
- Demonstrate **data validation**, a clean architecture (presentation / application logic / persistence), and **database access via ORM**
- Produce clean, well-structured, and documented code (incl. tests)
- Prepare students for **teamwork and professional documentation**
- Use this repository as a starting point by importing it into your own GitHub account  
- Work only within your own copy — do not push to the original template  
- Commit regularly to track your progress

---

# 🍕 TEMPLATE for documentation

---

## 📝 Application Requirements

---

### Problem :
Als Teilzeit-Student gibt es viele Dinge die man zu erledigen hat und zu welchen man einen Überblick behalten soll. Es kann schnell passieren, dass man etwas aus den Augen verliert.

---

### Scenario: 
Mit dem Budget-Planner im App-Format können Studiedierende ganz einfach und von überall einen Einblick in Ihre Finanzen erhalten. Mit diesen Informationen können Sie laufend Ihr Budget entsprechend der Situation anpassen.

-
-

---

## 📖 User Stories

### 1. Gesicherter Login
**Als User möchte ich, dass die Browser App Passwort geschützt ist (Passwort bei Erstnutzung: Test1234!).**

- **Inputs:** E-Mail, Passwort (max. 3 Versuche) 
- **Outputs:** Erfolgreicher Login, Fehlermeldung bei falschem Passwort

---

### 2. Passwort ändern
**Als User möchte ich jederzeit mein Passwort in der App ändern können.**

- **Inputs:** Aktuelles Passwort (falls vorhanden), neues Passwort, Passwort-Bestätigung
- **Outputs:** Passwort wird nach Regelprüfung gehasht gespeichert (bcrypt) und Erfolgsmeldung ausgegeben oder Fehlermeldung bei Regelverletzung

---

### 3. Auto-Logout bei Inaktivität
**Als User möchte ich automatisch ausgeloggt werden bei Inaktivität.**

- **Inputs:** Keine Eingabe innerhalb des Timeout-Timer
- **Outputs:** Automatischer Logout-Hinweis, Daten werden gespeichert, Anwendung wird beendet

---

### 4. Einnahmen erfassen und verwalten
**Als User möchte ich, meine Einnahmen erfassen und bearbeiten können.**

- **Inputs:** Kategorie wählen, Einnahme wählen, Datum (`DD.MM.YYYY` oder `.` für heute), Art und Betrag in CHF erfassen
- **Outputs:** Einnahme wird als positiver Betrag gespeichert; vorhandene Einträge können bearbeitet und gelöscht werden

---

### 5. Ausgaben erfassen und verwalten
**Als User möchte ich, meine Ausgaben erfassen und bearbeiten können.**

- **Inputs:** Kategorie wählen, Ausgabe wählen, Datum (`DD.MM.YYYY` oder `.` für heute), Art und Betrag in CHF erfassen
- **Outputs:** Ausgabe wird als negativer Betrag gespeichert; vorhandene Einträge können bearbeitet und gelöscht werden

---

### 6. Budget-Kategorien verwalten
**Als User möchte ich  mein Budget in mehrere (Limit von X) anpassbare Kategorien unterteilen können, um den Überblick zu behalten.**

- **Inputs:** 
- **Outputs:** 

---

### 7. Budgetlimit pro Kategorie festlegen
**Als User möchte ich ein Budgetlimit für jede Kategorie festlegen können.**

- **Inputs:** Kategorie auswählen, Aktion auswählen und Limitbetrag in CHF erfassen
- **Outputs:** Limit wird pro Kategorie gespeichert, angezeigt, aktualisiert oder entfernt; ungueltige Betraege werden abgewiesen (max. 2000 CHF)

---

### 8. Warnung bei Limitüberschreitung
**Als User möchte ich eine Warnung erhalten, wenn ich mein Budgetlimit überschritten habe.** 

- **Inputs:** 
- **Outputs:** 

---

### 9. Statistik anzeigen
**Als User möchte ich, die Daten vom aktuellen Monat mit denen der Vormonate vergleichen können.**

- **Inputs:** Statistik-Menü,  Monatsstatistik wählen
- **Outputs:** Balkendiagramm mit Vergleich Vormonat vs. aktueller Monat pro Kategorie inklusive Wertebeschriftung

---

## 🧩 Use Cases

> 🚧 Name actors and briefly describe each use case. Ideally, a UML use case diagram specifies use cases and relationships.

![UML Use Case Diagram](docs/architecture-diagrams/uml_use_case_diagram.png)

### Main Use Cases
- Hauptmenü anzeigen (Bedienung aller Funktionen)
- Budget-Kategorien verwalten (Kategorien und Einträge anzeigen, erstellen, bearbeiten und löschen)
- Finanzkontrolle pro Kategorie (Budgetlimit und Sparziel setzen, anzeigen, ändern, entfernen)
- Passwort ändern (Benutzerpasswort aktualisieren, Sicherheitsregeln prüfen)
- Daten speichern und Programm beenden (Eingaben werden dauerhaft gesichert und das Programm wird sauber beendet)
- Ausgabe von Statistik (Visualisierung) als PGN-Datei (finanzziele_diagramm.png & monats_summen_diagramm.png

**Actors**
- Benutzer (plant sein Budget)
- System/Timer (führt Auto-Logout bei Inaktivität aus)
- Datenspeicher/Dateisystem (sichert Benutzerdaten)
---

### Wireframes / Mockups

> 🚧 Add screenshots of the wireframe mockups you chose to implement.

![Wireframe – Home](docs/ui-images/wireframe_home.png)
![Wireframe – Checkout](docs/ui-images/wireframe_checkout.png)

---

## 🏛️ Architecture

> 🚧 Document the architecture components, relationships, and key design decisions.

### Software Architecture

> 🚧 Insert your UML class diagram(s). Split into multiple diagrams if needed.

![UML Class Diagram](docs/architecture-diagrams/uml_class_architecture.png)

**Layers / components:**
- UI (NiceGUI pages/components, browser as thin client)
- Application logic (controllers + domain/services)
- Persistence (SQLite + ORM entities + repositories/queries)

**Design decisions (examples):**
- Organize code using **MVC**:
   - **Model:** domain + ORM entities (e.g. `models.py`)
   - **View:** NiceGUI UI components/pages
   - **Controller:** event handlers and coordination logic between UI, services, and persistence
- Separate UI (`app/main.py`) from domain logic (e.g. `pricing.py`) and persistence (e.g. `models.py`, `db.py`)
- Use and interaction of modules to minimize dependencies, by minimizing cohesion and maximizing coupling
- Keep business rules testable without starting the UI

**Design patterns used**
- Model–View–Controller: Wir haben uns für das MVC-Pattern entschieden, weil dieses die Anwendung klar zwischen Datenlogik, Benutzereingabe & -ausgabe und Ablaufsteuerung trennt. Die Business Logik bleibt somit testbar und das UI ist jederzeit austauschbar.


---

### 🗄️ Database and ORM

> 🚧 Describe the database and your ORM entities. Ideally, a diagram documents the database and it is described together with the ORM entities.

![ER Diagram](docs/architecture-diagrams/er_diagram.png)

**ORM and Entities (example):** In the database, order are stored in ... that are mapped an `Order` entity. The `Order` ↔ `OrderItem` relationship ... ensures that an `Order` has at least one `OrderItem` and an `OrderItem` always relates to an `Order`.

### Entities
- `X`
- `Y`
- `Z`

### Relationships
- One `Order` → many `OrderItem`
- Each `OrderItem` references one `Pizza`

---


## ✅ Project Requirements

---

> 🚧 Requirements act as a contract: implement and demonstrate each point below.

Each app must meet the following criteria in order to be accepted (see also the official project guidelines PDF on Moodle):

1. Using NiceGUI for building an interactive web app
2. Data validation in the app
3. Using an ORM for database management

---

### 1. Browser-based App (NiceGUI)

> 🚧 In this section, document how your project fulfills each criterion.

Der Benutzer interagiert via Browser mit der Anwendung. Der Benutzer kann: 

- Hauptmenü / Dashboard anzeigen
- Einnahmen und Ausgaben erfassen
- Bereits erfasste Einnahmen und Ausgaben bearbeiten oder löschen
- Budget-Kategorien erstellen und verwalten (maximal 5 Kategorien)
- Pro Kategorie Budgetlimits setzen und anpassen
- Warnungen bei Überschreitung von Budgetlimits erhalten
- Statistiken anzeigen und Monatswerte vergleichen
- Passwort ändern und bei Inaktivität automatisch ausgelogt werden

**Architecture note (per SS26 guidelines):** the browser is a thin client; UI state + business logic live on the server-side NiceGUI app.

---

### 2. Data Validation

The application validates all user input to ensure data integrity and a smooth user experience.
These checks prevent crashes and guide the user to provide correct input, matching the validation requirements described in the project guidelines.

---

### 3. Database Management

All relevant data is managed via an ORM (e.g. SQLModel or SQLAlchemy). For the pizza example this includes users, pizzas, and orders. 
Alle relevanten Daten werden via ORM () gemanaged. Für FinFlow beeihaltet das Benutzer, ...

---

## ⚙️ Implementation

---

### Technology

- Python 3.x
- Environment: GitHub Codespaces
- External libraries (e.g. NiceGUI, SQLAlchemy, Pydantic)

---

### 📚 Libraries Used

- **nicegui** – UI framework  
- **sqlmodel** – ORM  
- **sqlalchemy** – database toolkit  
- **reportlab** – PDF generation  
- **python-dotenv** – configuration  
- **pytest** – testing  
- **pytest-cov** – coverage  

- **bcrypt** - Password-Hashing
- **matplotlib** - Diagramm generation
- **numpy**** - help function for statistic
---

### 📂 Repository Structure

```text
budgetplaner/
├── models/                 # M - Model (Daten & Business-Logik)
│   ├── __init__.py
│   ├── user.py
│   ├── auth_model.py
│   ├── account_model.py
│   ├── budget.py
│   ├── finance.py
│   └── data_storage.py
│
├── views/                 # V - View (Benutzeroberfläche)
│   ├── __init__.py
│   ├── cli_view.py
│   ├── auth_view.py
│   ├── account_view.py
│   ├── budget_view.py
│   ├── statistics_view.py
│   ├── menu_view.py
│   └── formatter.py
│
├── controllers/           # C - Controller (Logik-Orchestrierung)
│   ├── __init__.py
│   ├── auth_controller.py
│   ├── budget_controller.py
│   ├── account_controller.py
│   └── main_controller.py
│
├── utils/
│   ├── __init__.py
│   ├── validators.py
│   └── constants.py
│
├── main.py               # Entry-Point
└── budget_daten.json
```

---

### How to Run

> 🚧 Adjust to your project.

### 1. Project Setup
- Python 3.13 (or the course version) is required
- Create and activate a virtual environment:
   - **macOS/Linux:**
      ```bash
      python3 -m venv .venv
      source .venv/bin/activate
      ```
   - **Windows:**
      ```bash
      python -m venv .venv
      .venv\Scripts\Activate
      ```
- Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

### 2. Configuration
- E.g., setup of parameters or environment variables

### 3. Launch
- Start the NiceGUI app (example):
   ```bash
   python app/main.py
   ```
- Open the URL printed in the console.

### 4. Usage (document as steps)

FinFlow nutzen (Hauptfunktionen)
1. Anmeldung und Sicherheit
   - App starten und mit dem bestehenden Passwort anmelden (Erstpasswort: `Test1234!`).
   - Bei Bedarf das Passwort in der App ändern.
   - Bei längerer Inaktivität erfolgt ein automatischer Logout.
2. Einnahmen und Ausgaben verwalten:
   - Neue Einnahmen und Ausgaben mit Betrag und Bezeichnung erfassen.
   - Vorhandene Einträge bearbeiten oder löschen.
3. Budget-Kategorien verwalten:
   - Bis zu 5 Kategorien anlegen, um Finanzen strukturiert zu trennen.
   - Pro Kategorie ein Budgetlimit setzen und bei Bedarf anpassen.
4. Budgetkontrolle und Warnungen:
   - Ausgaben je Kategorie mit dem gesetzten Limit vergleichen.
   - Bei Überschreitung eines Limits wird eine Warnung ausgegeben.
5. Statistik und Monatsvergleich:
   - FinanzÜbersichten und Statistiken aufrufen.
   - Aktuelle Monatswerte mit Vormonaten vergleichen.
6. Daten sichern und beenden:
   - Änderungen werden dauerhaft gespeichert.
   - App über die Beenden-Funktion sauber schliessen.

> 🚧 Add UI screenshots of the main screens (or a short video link):

![UI – Menu](docs/ui-images/ui_menu.png)
![UI – Checkout](docs/ui-images/ui_checkout.png)

---

## 🧪 Testing

> 🚧 Explain what you test and how to run tests.

**Types (examples):**
- Unit tests: pricing/discount rules, validators
- Integration tests: ORM mappings + queries against a test SQLite DB

**Run:**
```bash
pytest
```

> 🚧 If you provide separate commands, document them here (e.g. `pytest -m integration`).

---

## 👥 Team & Contributions

---


| Name      | Contribution |
|-----------|--------------|
| Gowsi | NiceGUI UI + documentation |
| Paola | Database & ORM + documentation |
| Nina | Business logic + documentation |

---

## Planung / Zeitplan

---


| Was      | Datum |  ZUständige Person | Bemerkungen | 
|-----------|--------------|--------------|--------------|
| Code fertig stellen  | 09.03.2026 | Paola | Finanzziel raus & recheriere DB-Sache 1W | 
| GUI-Mockup erstellen | 09.03.2026 | Gowsi & Nina | |
| Business Logik  | 27.03.2026  | Nina | |
| Gui fertig stellen  | 27.03.2026 | Gowsi | |
| Code & GUI an Rainer schicken für Feedback 1 | 28.03.2026 | Paola | |
| 1 Coaching | 07.04.2026 | alle | verbesserte GUI & Code präsentieren & Feedback 2 einholen|
| Verbesserung Feedback 2 | 28.04.2026 | | |
| Präsentation aufsetzen & Planen | 12.05.2026 | Nina | |
| 2 Coaching | 12.05.2026 | alle | REadme zeigen und Feedback einholen |
| Umsetzen von noch offenen Anliegen | 22.05.2026 | alle | |
| Finale Abgabe | 24.05.2026 | Nina | Präsi als PDF & GitHub-Link |
| Präsentation | 02.06.2026 |  alle | * |

---

## 🤝 Contributing

---

- Use this repository as a starting point by importing it into your own GitHub account
- Work only within your own copy — do not push to the original template
- Commit regularly to track your progress

---

## 📝 License

---

This project is provided for **educational use only** as part of the Advanced Programming module.

[MIT License](LICENSE)
