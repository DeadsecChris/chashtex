from flask import Flask, render_template, request

app = Flask(__name__)


def start():
    user_name = "Bob"
    return render_template("index.html", name=user_name, tech_list=["eins","zwei","drei"])

def test():

    return render_template("test.html")

#Definition auf welche Datei es sich bezieht. Templates Ordner muss nicht angegeben werden.
@app.route("/test")
def pups():
    return

if __name__ =="__main__":
    app.run(debug=True)


#Wert aus dem HTML Viech abfragen und einer Varianblen übergeben
def nettorechenbums():
    netto_einkommen = request.form.get("net_salary")
    return netto_einkommen


#Beispielrechnung   
frei_verfügbar_ergebnis = 1 + 1 

#Wert wird in eine Variable vom HTML Viech reingeschrieben.
def frei_verfügbar(frei_verfügbares_ergebnis):
        return render_template("CashTex_HTML_Website.html", frei_verfügbar_ergebnis = frei_verfügbar_ergebnis)








