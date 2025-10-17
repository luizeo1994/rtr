from flask import Flask, render_template, request, redirect, url_for
import pandas as pd

app = Flask(__name__)

PLANILHA = "indicativos.xlsx"

# Função para carregar dados da planilha
def carregar_dados():
    df = pd.read_excel(PLANILHA, header=None, names=["Retransmissor", "Receptores"])
    dados = []
    for _, row in df.iterrows():
        if pd.notna(row["Retransmissor"]) and pd.notna(row["Receptores"]):
            retransmissor = row["Retransmissor"].strip()
            receptores = [r.strip() for r in row["Receptores"].split("/") if r.strip()]
            dados.append((retransmissor, receptores))
    return dados

dados = carregar_dados()

@app.route("/", methods=["GET", "POST"])
def index():
    global dados
    resultados = []
    consulta = ""

    if request.method == "POST":
        # Recarregar planilha
        if "reload" in request.form:
            dados = carregar_dados()
            return redirect(url_for("index"))

        consulta = request.form["indicativo"].strip().upper()

        for retransmissor, receptores in dados:
            # Busca exata
            if consulta == retransmissor.replace(" ", ""):
                resultados.append({
                    "tipo": "retransmissor",
                    "retransmissor": retransmissor,
                    "receptores": receptores
                })
            elif consulta in receptores:
                resultados.append({
                    "tipo": "receptor",
                    "retransmissor": retransmissor,
                    "receptores": receptores
                })
            # Busca parcial
            elif consulta in retransmissor or any(consulta in r for r in receptores):
                resultados.append({
                    "tipo": "parcial",
                    "retransmissor": retransmissor,
                    "receptores": receptores
                })

    return render_template("index.html", resultados=resultados, consulta=consulta)

if __name__ == "__main__":
    # Para desenvolvimento local continue usando: python app.py
    # Em produção (Render) o Gunicorn irá gerir o processo e fornecer a porta via env var PORT
    import os
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
