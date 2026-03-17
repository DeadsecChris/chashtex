from flask import Flask, render_template, request
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import os

app = Flask(__name__)

# ETF Daten
ETFS = {
    "1": {"name": "MSCI World", "return": 8.0},
    "2": {"name": "S&P 500", "return": 8.5},
    "3": {"name": "Emerging Markets", "return": 7.2}
}

# Sparlevel
SPARLEVEL = {
    "wenig": 0.10,
    "mittel": 0.20,
    "hoch": 0.30,
    "sehr_hoch": 0.50
}


@app.route("/berechnen", methods=["GET", "POST"])
def index():

    # Standardwerte für ersten Seitenaufruf
    frei_verfuegbar = ""
    monthly_rate = ""
    final_value = ""
    profit = ""
    yearly_data = []

    # Prüfen ob Formular abgeschickt wurde
    if request.method == "POST":

        net_salary = float(request.form["net_salary"])
        monthly_expenses = float(request.form["monthly_expenses"])
        saving_level = request.form["saving_level"]
        etf_id = request.form["etf_id"]
        years = int(request.form["years"])
        start_capital = float(request.form["initial_investment"])

        # Frei verfügbares Geld
        free_budget = net_salary - monthly_expenses

        # Sparrate
        sparrate = free_budget * SPARLEVEL[saving_level]

        # ETF Rendite
        etf = ETFS[etf_id]
        annual_return = etf["return"] / 100
        monthly_return = annual_return / 12

        capital = start_capital
        invested = start_capital

        for year in range(1, years + 1):

            for month in range(12):
                capital += sparrate
                invested += sparrate
                capital *= (1 + monthly_return)

            yearly_data.append({
                "year": year,
                "invested": round(invested, 2),
                "capital": round(capital, 2)
            })


        frei_verfuegbar = round(free_budget, 2)
        monthly_rate = round(sparrate, 2)
        final_value = round(capital, 2)
        profit = round(final_value - invested, 2)

    # Diagramm erstellen
# Diagramm erstellen
    jahre = [row["year"] for row in yearly_data]
    einzahlungen = [row["invested"] for row in yearly_data]
    kapitalwerte = [row["capital"] for row in yearly_data]

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

# Ergebnisse an Template übergeben

    return render_template(
        "CashTex_AI_main.html",
        frei_verfügbar_ergebnis=frei_verfuegbar,
        monthly_rate=monthly_rate,
        final_value=final_value,
        profit=profit,
        yearly_data=yearly_data
    )


if __name__ == "__main__":
    app.run(debug=True)