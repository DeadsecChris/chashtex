from flask import Flask, render_template, request
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

def get_top_unternehmen(etf_id):
    conn = sqlite3.connect(DB)
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

@app.get("/")
def home():
    return render_template("index.html")


@app.route("/berechnen", methods=["GET", "POST"])
def index():

    #  Formwerte speichern
    form_data = {
        "net_salary": "",
        "monthly_expenses": "",
        "saving_level": "mittel",
        "etf_id": "1",
        "years": "10",
        "initial_investment": "0"
    }

    frei_verfuegbar = ""
    monthly_rate = ""
    final_value = ""
    profit = ""
    yearly_data = []
    top_unternehmen = []

    if request.method == "POST":

        # Werte speichern
        form_data["net_salary"] = request.form["net_salary"]
        form_data["monthly_expenses"] = request.form["monthly_expenses"]
        form_data["saving_level"] = request.form["saving_level"]
        form_data["etf_id"] = request.form["etf_id"]
        form_data["years"] = request.form["years"]
        form_data["initial_investment"] = request.form["initial_investment"]

       # Berechnungen durchführen
        net_salary = float(form_data["net_salary"])
        monthly_expenses = float(form_data["monthly_expenses"])
        saving_level = form_data["saving_level"]
        etf_id = form_data["etf_id"]
        years = int(form_data["years"])
        start_capital = float(form_data["initial_investment"])

        free_budget = net_salary - monthly_expenses
        sparrate = free_budget * SPARLEVEL[saving_level]

        etf = ETFS[etf_id]
        monthly_return = (etf["return"] / 100) / 12

        capital = start_capital
        invested = start_capital

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

#Diagramm erstellen
    if yearly_data:
        jahre = [row["year"] for row in yearly_data]
        einzahlungen = [float(row["invested"].replace(".", "").replace(",", ".")) for row in yearly_data]
        kapitalwerte = [float(row["capital"].replace(".", "").replace(",", ".")) for row in yearly_data]

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

        legende = ax.legend(facecolor="#1f2937", edgecolor="#334155", fontsize=10)
        for text in legende.get_texts():
            text.set_color("white")

        plt.tight_layout()

        os.makedirs("static", exist_ok=True)
        plt.savefig(
            "static/kapitalentwicklung.png",
            bbox_inches="tight",
            facecolor=fig.get_facecolor()
        )
        plt.close()

    return render_template(
        "CashTex_AI_main.html",
        frei_verfuegbar_ergebnis=frei_verfuegbar,
        monthly_rate=monthly_rate,
        final_value=final_value,
        profit=profit,
        yearly_data=yearly_data,
        top_unternehmen=top_unternehmen,
        form_data=form_data  
    )


if __name__ == "__main__":
    app.run(debug=True)