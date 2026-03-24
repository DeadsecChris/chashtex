from flask import Flask, render_template, request, redirect
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import sqlite3
import os

app = Flask(__name__)
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

def format_euro(value):
    return f"{value:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")

def get_db():
    return sqlite3.connect(DB)

def get_top_unternehmen(etf_id):
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

# -------------------------
# STARTSEITE
# -------------------------
@app.route("/")
def home():
    conn = get_db()
    cur = conn.cursor()

    cur.execute("SELECT BenutzerID, Vorname, Nachname FROM Benutzer")
    benutzer = cur.fetchall()

    return render_template("index.html", form_data={}, benutzer=benutzer)

# -------------------------
# BERECHNEN + LOGIN
# -------------------------
@app.route("/berechnen", methods=["GET", "POST"])
def berechnen():

    conn = get_db()
    cur = conn.cursor()

    # Benutzer laden
    cur.execute("SELECT BenutzerID, Vorname, Nachname FROM Benutzer")
    benutzer = cur.fetchall()

    # Standardwerte
    form_data = {
        "net_salary": "",
        "monthly_expenses": "",
        "saving_level": "mittel",
        "etf_id": "1",
        "years": "10",
        "initial_investment": "0"
    }

    # 👉 WICHTIG: GET = nur Seite anzeigen
    if request.method == "GET":
        return render_template("CashTex_AI_main.html", form_data=form_data, benutzer=benutzer)

    # 👉 AB HIER: POST (Berechnung oder Login)
    form_data = request.form.to_dict()

    # -------------------------
    # LOGIN LADEN
    # -------------------------
    if "benutzer_id" in request.form and request.form["benutzer_id"] != "":
        benutzer_id = request.form["benutzer_id"]

        cur.execute("""
        SELECT NetSalary, Expenses, SavingLevel, ETFID, Years, InitialInvestment
        FROM Sparplaene
        WHERE BenutzerID = ?
        """, (benutzer_id,))

        data = cur.fetchone()

        if data:
            form_data = {
                "net_salary": data[0],
                "monthly_expenses": data[1],
                "saving_level": data[2],
                "etf_id": str(data[3]),
                "years": str(data[4]),
                "initial_investment": data[5]
            }

        return render_template("CashTex_AI_main.html", form_data=form_data, benutzer=benutzer)

    # -------------------------
    # BERECHNUNG
    # -------------------------
    form_data = request.form.to_dict()

    net_salary = float(form_data["net_salary"])
    monthly_expenses = float(form_data["monthly_expenses"])
    saving_level = form_data["saving_level"]
    etf_id = form_data["etf_id"]
    years = int(form_data["years"])
    start_capital = float(form_data["initial_investment"])

    free_budget = net_salary - monthly_expenses
    sparrate = free_budget * SPARLEVEL[saving_level]

    monthly_return = (ETFS[etf_id]["return"] / 100) / 12

    capital = start_capital
    invested = start_capital
    yearly_data = []

    for year in range(1, years + 1):
        for month in range(12):
            capital += sparrate
            invested += sparrate
            capital *= (1 + monthly_return)

        yearly_data.append({
            "year": year,
            "invested": format_euro(invested),
            "capital": format_euro(capital)
        })

    frei_verfuegbar = format_euro(free_budget)
    monthly_rate = format_euro(sparrate)
    final_value = format_euro(capital)
    profit = format_euro(capital - invested)

    top_unternehmen = get_top_unternehmen(etf_id)

    # Diagramm
    if yearly_data:
        jahre = [row["year"] for row in yearly_data]
        einzahlungen = [float(row["invested"].replace(".", "").replace(",", ".")) for row in yearly_data]
        kapitalwerte = [float(row["capital"].replace(".", "").replace(",", ".")) for row in yearly_data]

        fig, ax = plt.subplots()
        ax.plot(jahre, einzahlungen)
        ax.plot(jahre, kapitalwerte)

        os.makedirs("static", exist_ok=True)
        plt.savefig("static/kapitalentwicklung.png")
        plt.close()

    return render_template(
        "CashTex_AI_main.html",
        frei_verfuegbar_ergebnis=frei_verfuegbar,
        monthly_rate=monthly_rate,
        final_value=final_value,
        profit=profit,
        yearly_data=yearly_data,
        top_unternehmen=top_unternehmen,
        form_data=form_data,
        benutzer=benutzer
    )

# -------------------------
# REGISTRIEREN / SPEICHERN
# -------------------------
@app.route("/registrieren", methods=["POST"])
def registrieren():

    conn = get_db()
    cur = conn.cursor()

    vorname = request.form["Vorname"]
    nachname = request.form["Nachname"]

    # Prüfen ob Benutzer existiert
    cur.execute("""
    SELECT BenutzerID FROM Benutzer
    WHERE Vorname = ? AND Nachname = ?
    """, (vorname, nachname))

    user = cur.fetchone()

    if user:
        benutzer_id = user[0]

        # Überschreiben
        cur.execute("""
        UPDATE Sparplaene
        SET NetSalary=?, Expenses=?, SavingLevel=?, ETFID=?, Years=?, InitialInvestment=?
        WHERE BenutzerID=?
        """, (
            request.form["net_salary"],
            request.form["monthly_expenses"],
            request.form["saving_level"],
            request.form["etf_id"],
            request.form["years"],
            request.form["initial_investment"],
            benutzer_id
        ))

    else:
        # Neuer Benutzer
        cur.execute("INSERT INTO Benutzer (Vorname, Nachname) VALUES (?, ?)", (vorname, nachname))
        benutzer_id = cur.lastrowid

        cur.execute("""
        INSERT INTO Sparplaene
        (BenutzerID, NetSalary, Expenses, SavingLevel, ETFID, Years, InitialInvestment)
        VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (
            benutzer_id,
            request.form["net_salary"],
            request.form["monthly_expenses"],
            request.form["saving_level"],
            request.form["etf_id"],
            request.form["years"],
            request.form["initial_investment"]
        ))

    conn.commit()
    conn.close()

    return redirect("/")


if __name__ == "__main__":
    app.run(debug=True)