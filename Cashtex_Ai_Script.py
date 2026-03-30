from flask import Flask, render_template, request, session, redirect, url_for
from werkzeug.security import generate_password_hash, check_password_hash
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import sqlite3
import os

app = Flask(__name__)
app.secret_key = "cashtex_geheim"

DB = "database.db"

ETFS = {
    "1": {"name": "MSCI World", "return": 8.0},
    "2": {"name": "S&P 500", "return": 8.5},
    "3": {"name": "Emerging Markets", "return": 7.2},
    "4": {"name": "Core DAX EUR", "return": 8.4},
    "5": {"name": "Global X Defense Tech", "return": 9.0},
    "6": {"name": "XTrackers AI & Big Data", "return": 10.0}
}

SPARLEVEL = {
    "wenig": 0.10,
    "mittel": 0.20,
    "hoch": 0.30,
    "sehr_hoch": 0.50
}


def get_db():
    conn = sqlite3.connect(DB, timeout=10)
    conn.row_factory = sqlite3.Row
    return conn


def init_database():
    conn = get_db()
    cur = conn.cursor()

    cur.execute("""
        CREATE TABLE IF NOT EXISTS Benutzer (
            BenutzerID INTEGER PRIMARY KEY AUTOINCREMENT,
            Vorname TEXT,
            Nachname TEXT,
            Benutzername TEXT UNIQUE,
            PasswortHash TEXT
        )
    """)

    # Für bestehende DB: ggf. fehlende Spalten ergänzen
    cur.execute("PRAGMA table_info(Benutzer)")
    existing_cols = [row[1] for row in cur.fetchall()]
    if "Benutzername" not in existing_cols:
        try:
            cur.execute("ALTER TABLE Benutzer ADD COLUMN Benutzername TEXT UNIQUE")
        except Exception:
            pass
    if "PasswortHash" not in existing_cols:
        try:
            cur.execute("ALTER TABLE Benutzer ADD COLUMN PasswortHash TEXT")
        except Exception:
            pass

    cur.execute("""
        CREATE TABLE IF NOT EXISTS Sparplaene (
            SparplanID INTEGER PRIMARY KEY AUTOINCREMENT,
            BenutzerID INTEGER NOT NULL,
            NetSalary REAL NOT NULL,
            Expenses REAL NOT NULL,
            SavingLevel TEXT NOT NULL,
            ETFID TEXT NOT NULL,
            Years INTEGER NOT NULL,
            InitialInvestment REAL NOT NULL,
            FOREIGN KEY (BenutzerID) REFERENCES Benutzer(BenutzerID)
        )
    """)

    conn.commit()
    conn.close()


def default_form_data():
    return {
        "net_salary": "",
        "monthly_expenses": "",
        "saving_level": "mittel",
        "etf_id": "1",
        "years": "10",
        "initial_investment": "0"
    }


def format_euro(value):
    return f"{value:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")


def get_top_unternehmen(etf_id):
    try:
        conn = get_db()
        cur = conn.cursor()

        cur.execute("""
            SELECT U.Bezeichnung
            FROM Unternehmen U
            JOIN ETF_Unternehmen EU ON U.WKN = EU.WKN
            WHERE EU.ETFID = ?
            LIMIT 5
        """, (etf_id,))

        data = [row[0] for row in cur.fetchall()]
        conn.close()
        return data
    except Exception:
        return []


def get_benutzer():
    try:
        conn = get_db()
        cur = conn.cursor()
        cur.execute("SELECT BenutzerID, Vorname, Nachname FROM Benutzer ORDER BY Vorname, Nachname")
        data = cur.fetchall()
        conn.close()
        return data
    except Exception:
        return []


def get_benutzer_by_username(username):
    try:
        conn = get_db()
        cur = conn.cursor()
        cur.execute("SELECT BenutzerID, Benutzername, PasswortHash FROM Benutzer WHERE Benutzername = ?", (username,))
        user = cur.fetchone()
        conn.close()
        return user
    except Exception:
        return None


def load_sparplan_for_user(benutzer_id):
    try:
        conn = get_db()
        cur = conn.cursor()
        cur.execute("SELECT NetSalary, Expenses, SavingLevel, ETFID, Years, InitialInvestment FROM Sparplaene WHERE BenutzerID = ?", (benutzer_id,))
        plan = cur.fetchone()
        conn.close()
        return plan
    except Exception:
        return None


def save_sparplan_for_user(benutzer_id, form_data):
    conn = get_db()
    cur = conn.cursor()
    cur.execute("SELECT SparplanID FROM Sparplaene WHERE BenutzerID = ?", (benutzer_id,))
    existing_plan = cur.fetchone()

    if existing_plan:
        cur.execute("""
            UPDATE Sparplaene
            SET NetSalary = ?, Expenses = ?, SavingLevel = ?, ETFID = ?, Years = ?, InitialInvestment = ?
            WHERE BenutzerID = ?
        """, (
            form_data["net_salary"],
            form_data["monthly_expenses"],
            form_data["saving_level"],
            form_data["etf_id"],
            form_data["years"],
            form_data["initial_investment"],
            benutzer_id
        ))
    else:
        cur.execute("""
            INSERT INTO Sparplaene (BenutzerID, NetSalary, Expenses, SavingLevel, ETFID, Years, InitialInvestment)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (
            benutzer_id,
            form_data["net_salary"],
            form_data["monthly_expenses"],
            form_data["saving_level"],
            form_data["etf_id"],
            form_data["years"],
            form_data["initial_investment"]
        ))

    conn.commit()
    conn.close()


def save_chart(yearly_data):
    if not yearly_data:
        return

    jahre = [row["year"] for row in yearly_data]
    einzahlungen = [row["invested_value"] for row in yearly_data]
    kapitalwerte = [row["capital_value"] for row in yearly_data]

    fig, ax = plt.subplots(figsize=(10, 5), facecolor="#111827")
    ax.set_facecolor("#111827")

    ax.plot(
        jahre,
        einzahlungen,
        marker="o",
        linewidth=2.5,
        color="#94a3b8",
        label="Einzahlungen"
    )

    ax.plot(
        jahre,
        kapitalwerte,
        marker="o",
        linewidth=2.5,
        color="#38bdf8",
        label="Kapitalwert"
    )

    ax.set_title("Kapitalentwicklung", color="white", fontsize=16, pad=15)
    ax.set_xlabel("Jahre", color="white")
    ax.set_ylabel("Euro", color="white")

    ax.tick_params(axis="x", colors="white")
    ax.tick_params(axis="y", colors="white")

    for spine in ax.spines.values():
        spine.set_color("#334155")

    ax.grid(True, color="#334155", linestyle="--", linewidth=0.8, alpha=0.7)

    legend = ax.legend(facecolor="#1f2937", edgecolor="#334155", fontsize=10)
    for text in legend.get_texts():
        text.set_color("white")

    plt.tight_layout()

    os.makedirs("static", exist_ok=True)
    plt.savefig(
        "static/kapitalentwicklung.png",
        bbox_inches="tight",
        facecolor=fig.get_facecolor()
    )
    plt.close()


def calculate_data(form_data):
    yearly_data = []
    top_unternehmen = []
    frei_verfuegbar = ""
    monthly_rate = ""
    final_value = ""
    profit = ""
    error_message = ""

    try:
        net_salary = float(form_data["net_salary"])
        monthly_expenses = float(form_data["monthly_expenses"])
        years = int(form_data["years"])
        start_capital = float(form_data["initial_investment"])
        saving_level = form_data["saving_level"]
        etf_id = form_data["etf_id"]

        if saving_level not in SPARLEVEL:
            error_message = "Ungültiges Sparlevel."

        elif etf_id not in ETFS:
            error_message = "Ungültiger ETF."

        elif net_salary < 0 or monthly_expenses < 0 or start_capital < 0 or years < 0:
            error_message = "Bitte nur positive Werte eingeben."

        elif years <= 0:
            error_message = "Die Anzahl der Jahre muss größer als 0 sein."

        elif monthly_expenses > net_salary:
            error_message = "Die monatlichen Ausgaben dürfen nicht höher als das Nettoeinkommen sein."

        else:
            free_budget = net_salary - monthly_expenses
            sparrate = free_budget * SPARLEVEL[saving_level]

            etf = ETFS[etf_id]
            monthly_return = (etf["return"] / 100) / 12

            capital = start_capital
            invested = start_capital

            for year in range(1, years + 1):
                for _ in range(12):
                    capital += sparrate
                    invested += sparrate
                    capital *= (1 + monthly_return)

                yearly_data.append({
                    "year": year,
                    "invested_value": round(invested, 2),
                    "capital_value": round(capital, 2),
                    "invested": format_euro(invested),
                    "capital": format_euro(capital)
                })

            frei_verfuegbar = format_euro(free_budget)
            monthly_rate = format_euro(sparrate)
            final_value = format_euro(capital)
            profit = format_euro(capital - invested)
            top_unternehmen = get_top_unternehmen(etf_id)

            save_chart(yearly_data)

    except ValueError:
        error_message = "Bitte gültige Zahlen eingeben."

    return {
        "frei_verfuegbar_ergebnis": frei_verfuegbar,
        "monthly_rate": monthly_rate,
        "final_value": final_value,
        "profit": profit,
        "yearly_data": yearly_data,
        "top_unternehmen": top_unternehmen,
        "error_message": error_message
    }


def update_session_with_results(form_data, result):
    session["form_data"] = form_data
    session["frei_verfuegbar_ergebnis"] = result["frei_verfuegbar_ergebnis"]
    session["monthly_rate"] = result["monthly_rate"]
    session["final_value"] = result["final_value"]
    session["profit"] = result["profit"]
    session["yearly_data"] = result["yearly_data"]
    session["top_unternehmen"] = result["top_unternehmen"]
    session["error_message"] = result["error_message"]


@app.get("/")
def startseite():
    session.clear()
    return render_template("Startseite.html")


@app.route("/berechnen", methods=["GET", "POST"])
def berechnen():
    user_id = session.get("user_id")
    user_logged_in = bool(user_id)
    username = session.get("username", "")

    # Bei berechnen-POST wird auf GET weitergeleitet, deshalb dürfen Ergebnisse erhalten bleiben.
    # Beim ersten Betreten der Seite (z.B. /) kann stattdessen session.clear() in Startseite erfolgen.

    benutzer = get_benutzer()

    form_data = default_form_data()
    form_data.update(session.get("form_data", {}))

    frei_verfuegbar = session.get("frei_verfuegbar_ergebnis", "")
    monthly_rate = session.get("monthly_rate", "")
    final_value = session.get("final_value", "")
    profit = session.get("profit", "")
    yearly_data = session.get("yearly_data", [])
    top_unternehmen = session.get("top_unternehmen", [])
    error_message = session.get("error_message", "")
    success_message = session.pop("success_message", "")

    if request.method == "POST":
        action = request.form.get("action", "berechnen")

        if action == "laden":
            benutzer_id = request.form.get("benutzer_id", "").strip()

            if not benutzer_id:
                session["error_message"] = "Bitte einen Benutzer auswählen."
                return redirect(url_for("berechnen"))

            try:
                plan = load_sparplan_for_user(benutzer_id)

                if not plan:
                    session["error_message"] = "Für diesen Benutzer wurde noch kein Sparplan gespeichert."
                    return redirect(url_for("berechnen"))

                loaded_form_data = {
                    "net_salary": str(plan["NetSalary"]),
                    "monthly_expenses": str(plan["Expenses"]),
                    "saving_level": plan["SavingLevel"],
                    "etf_id": str(plan["ETFID"]),
                    "years": str(plan["Years"]),
                    "initial_investment": str(plan["InitialInvestment"])
                }

                result = calculate_data(loaded_form_data)
                update_session_with_results(loaded_form_data, result)

                if not result["error_message"]:
                    session["success_message"] = "Gespeicherter Sparplan wurde geladen."

                return redirect(url_for("berechnen"))

            except Exception:
                session["error_message"] = "Fehler beim Laden des gespeicherten Sparplans."
                return redirect(url_for("berechnen"))

        if action == "save_current":
            if not user_logged_in:
                session["error_message"] = "Bitte zuerst einloggen oder registrieren, um zu speichern."
                return redirect(url_for("berechnen"))

            form_data = {
                "net_salary": request.form.get("net_salary", "").strip(),
                "monthly_expenses": request.form.get("monthly_expenses", "").strip(),
                "saving_level": request.form.get("saving_level", "mittel"),
                "etf_id": request.form.get("etf_id", "1"),
                "years": request.form.get("years", "10").strip(),
                "initial_investment": request.form.get("initial_investment", "0").strip()
            }

            result = calculate_data(form_data)
            update_session_with_results(form_data, result)

            if result["error_message"]:
                return redirect(url_for("berechnen"))

            save_sparplan_for_user(user_id, form_data)
            session["success_message"] = "Ihre aktuellen Werte wurden gespeichert."
            return redirect(url_for("berechnen"))

        form_data = {
            "net_salary": request.form.get("net_salary", "").strip(),
            "monthly_expenses": request.form.get("monthly_expenses", "").strip(),
            "saving_level": request.form.get("saving_level", "mittel"),
            "etf_id": request.form.get("etf_id", "1"),
            "years": request.form.get("years", "10").strip(),
            "initial_investment": request.form.get("initial_investment", "0").strip()
        }

        result = calculate_data(form_data)
        update_session_with_results(form_data, result)

        return redirect(url_for("berechnen"))

    if yearly_data and not os.path.exists("static/kapitalentwicklung.png"):
        save_chart(yearly_data)

    return render_template(
        "CashTex_AI_main.html",
        form_data=form_data,
        frei_verfuegbar_ergebnis=frei_verfuegbar,
        monthly_rate=monthly_rate,
        final_value=final_value,
        profit=profit,
        yearly_data=yearly_data,
        top_unternehmen=top_unternehmen,
        error_message=error_message,
        success_message=success_message,
        etfs=ETFS,
        benutzer=benutzer,
        user_logged_in=user_logged_in,
        username=username
    )


@app.get("/speichern")
def speichern():
    if "form_data" not in session:
        session["error_message"] = "Bitte zuerst eine Berechnung durchführen."
        return redirect(url_for("berechnen"))

    if "user_id" in session:
        save_sparplan_for_user(session["user_id"], session["form_data"])
        session["success_message"] = "Aktuelle Werte gespeichert (eingeloggt)."
        return redirect(url_for("berechnen"))

    form_data = default_form_data()
    form_data.update(session.get("form_data", {}))

    return render_template("registrieren.html", form_data=form_data)


@app.route("/registrieren", methods=["POST"])
def registrieren():
    try:
        conn = get_db()
        cur = conn.cursor()

        benutzername = request.form.get("Benutzername", "").strip()
        password = request.form.get("Passwort", "")
        pass_confirm = request.form.get("PasswortBestaetigen", "")

        vorname = request.form.get("Vorname", "").strip()
        nachname = request.form.get("Nachname", "").strip()

        if not benutzername or not password or not pass_confirm:
            session["error_message"] = "Benutzername, Passwort und Passwortbestätigung sind erforderlich."
            return redirect(url_for("berechnen"))

        if password != pass_confirm:
            session["error_message"] = "Passwörter stimmen nicht überein."
            return redirect(url_for("berechnen"))

        # Sparplandaten sicher holen (Session = Hauptquelle)
        session_data = session.get("form_data", {})

        form_data = {
            "net_salary": request.form.get("net_salary") or session_data.get("net_salary"),
            "monthly_expenses": request.form.get("monthly_expenses") or session_data.get("monthly_expenses"),
            "saving_level": request.form.get("saving_level") or session_data.get("saving_level"),
            "etf_id": request.form.get("etf_id") or session_data.get("etf_id"),
            "years": request.form.get("years") or session_data.get("years"),
            "initial_investment": request.form.get("initial_investment") or session_data.get("initial_investment"),
        }

        if not all(form_data.values()):
            session["error_message"] = "Fehlende Sparplandaten. Bitte zuerst berechnen."
            return redirect(url_for("berechnen"))

        existing_user = get_benutzer_by_username(benutzername)

        if existing_user:
            if not existing_user["PasswortHash"] or not check_password_hash(existing_user["PasswortHash"], password):
                session["error_message"] = "Benutzername existiert bereits oder falsches Passwort."
                return redirect(url_for("berechnen"))
            benutzer_id = existing_user["BenutzerID"]
        else:
            hashed_pw = generate_password_hash(password)
            cur.execute("""
                INSERT INTO Benutzer (Vorname, Nachname, Benutzername, PasswortHash)
                VALUES (?, ?, ?, ?)
            """, (vorname, nachname, benutzername, hashed_pw))
            benutzer_id = cur.lastrowid

        cur.execute("SELECT SparplanID FROM Sparplaene WHERE BenutzerID = ?", (benutzer_id,))
        existing_plan = cur.fetchone()

        if existing_plan:
            cur.execute("""
                UPDATE Sparplaene
                SET NetSalary = ?, Expenses = ?, SavingLevel = ?, ETFID = ?, Years = ?, InitialInvestment = ?
                WHERE BenutzerID = ?
            """, (
                form_data["net_salary"],
                form_data["monthly_expenses"],
                form_data["saving_level"],
                form_data["etf_id"],
                form_data["years"],
                form_data["initial_investment"],
                benutzer_id
            ))
        else:
            cur.execute("""
                INSERT INTO Sparplaene
                (BenutzerID, NetSalary, Expenses, SavingLevel, ETFID, Years, InitialInvestment)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (
                benutzer_id,
                form_data["net_salary"],
                form_data["monthly_expenses"],
                form_data["saving_level"],
                form_data["etf_id"],
                form_data["years"],
                form_data["initial_investment"]
            ))

        session["user_id"] = benutzer_id
        session["username"] = benutzername
        session["form_data"] = form_data

        conn.commit()
        conn.close()

        session["success_message"] = "Sparplan erfolgreich gespeichert und Benutzer angemeldet."
        return redirect(url_for("berechnen"))

    except Exception as e:
        print("FEHLER:", e)
        session["error_message"] = f"Fehler beim Speichern: {e}"
        return redirect(url_for("berechnen"))

@app.route("/login", methods=["GET", "POST"])
def login():
    error_message = session.pop("error_message", "")

    if request.method == "POST":
        username = request.form.get("Benutzername", "").strip()
        password = request.form.get("Passwort", "")

        if not username or not password:
            return render_template("anmelden.html", error_message="Bitte Benutzername und Passwort eingeben.")

        user = get_benutzer_by_username(username)

        if not user or not user["PasswortHash"] or not check_password_hash(user["PasswortHash"], password):
            return render_template("anmelden.html", error_message="Benutzername oder Passwort ist falsch.")

        session["user_id"] = user["BenutzerID"]
        session["username"] = username

        plan = load_sparplan_for_user(user["BenutzerID"])
        if plan:
            loaded_form_data = {
                "net_salary": str(plan["NetSalary"]),
                "monthly_expenses": str(plan["Expenses"]),
                "saving_level": plan["SavingLevel"],
                "etf_id": str(plan["ETFID"]),
                "years": str(plan["Years"]),
                "initial_investment": str(plan["InitialInvestment"])
            }
            result = calculate_data(loaded_form_data)
            update_session_with_results(loaded_form_data, result)
            session["success_message"] = "Eingeloggt und gespeicherter Sparplan geladen."
        else:
            session.pop("form_data", None)
            session.pop("yearly_data", None)
            session["success_message"] = "Eingeloggt. Noch keine gespeicherten Werte vorhanden."

        return redirect(url_for("berechnen"))

    return render_template("anmelden.html", error_message=error_message)



@app.get("/logout")
def logout():
    session.pop("user_id", None)
    session.pop("username", None)
    session.pop("form_data", None)
    session.pop("frei_verfuegbar_ergebnis", None)
    session.pop("monthly_rate", None)
    session.pop("final_value", None)
    session.pop("profit", None)
    session.pop("yearly_data", None)
    session.pop("top_unternehmen", None)
    session["success_message"] = "Sie wurden ausgeloggt."
    return redirect(url_for("berechnen"))


@app.get("/kapitalentwicklung")
def kapitalentwicklung():
    yearly_data = session.get("yearly_data", [])
    return render_template("CashTex_Kapitalentwicklung.html", yearly_data=yearly_data)


init_database()

if __name__ == "__main__":
    app.run(debug=True)