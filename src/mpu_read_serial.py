from flask import Flask, render_template_string, request, redirect, url_for
from datetime import datetime
import threading
import csv
import os
import serial
import time

# ===== CONFIGURAÇÕES =====
PORTA_SERIAL = "COM5"      # Altere conforme necessário (ex: "/dev/ttyUSB0")
BAUDRATE = 115200

app = Flask(__name__)
MOVIMENTO_ATIVO = False

import sys
# TITULO = input("Nome do Movimento: ").strip()
TITULO = sys.argv[1].strip()

os.makedirs("dataset", exist_ok=True)
CAMINHO_ARQUIVO = f"./dataset/{TITULO.casefold().replace(' ', '_')}.csv"

# Garante nome único
while os.path.isfile(CAMINHO_ARQUIVO):
    CAMINHO_ARQUIVO = os.path.splitext(CAMINHO_ARQUIVO)[0] + "-novo.csv"

print(f"📁 Salvando em: {CAMINHO_ARQUIVO}")

# ========= THREAD: LEITURA SERIAL =========
def leitura_serial():
    global MOVIMENTO_ATIVO
    try:
        ser = serial.Serial(PORTA_SERIAL, BAUDRATE, timeout=1)
        time.sleep(2)
        print(f"📡 Conectado à {PORTA_SERIAL}")
    except serial.SerialException:
        print("⚠️ Erro ao abrir a porta serial!")
        return

    with open(CAMINHO_ARQUIVO, mode="w", newline="") as file:
        writer = csv.writer(file)
        writer.writerow(["timestamp",
                         "ax1", "ay1", "az1", "gx1", "gy1", "gz1",
                         "ax2", "ay2", "az2", "gx2", "gy2", "gz2",
                         "em_movimento"])

        try:
            while True:
                linha = ser.readline().decode("utf-8").strip()

                if not linha:
                    continue

                dados = linha.split(",")
                try:
                    dados_float = [float(valor) for valor in dados]
                    if len(dados_float) != 12:
                        continue

                    timestamp = datetime.now().timestamp()
                    linha_completa = [timestamp] + dados_float + [1 if MOVIMENTO_ATIVO else 0]
                    writer.writerow(linha_completa)
                    print(f"{timestamp},{','.join(dados)},{1 if MOVIMENTO_ATIVO else 0}")

                except ValueError:
                    print("⚠️ Dado inválido! Encerrando leitura.")
                    break

        except KeyboardInterrupt:
            print("🛑 Leitura serial encerrada.")

    ser.close()

# ========= FLASK APP =========

@app.route("/")
def index():
    global MOVIMENTO_ATIVO
    return render_template_string("""
        <html>
        <head>
            <title>Marcador de Movimento</title>
            <style>
                body { font-family: Arial; text-align: center; padding: 30px; }
                button {
                    font-size: 30px; padding: 20px 40px; border-radius: 12px;
                    border: none; color: white;
                    background-color: {{ 'green' if ativo else '#007BFF' }};
                }
            </style>
        </head>
        <body>
            <h1>Movimento: {{ titulo }}</h1>
            <form method="POST" action="/toggle">
                <button type="submit">{{ 'Parar' if ativo else 'Iniciar' }} Movimento</button>
            </form>
            <p>Status: <strong>{{ '🟢 EM MOVIMENTO' if ativo else '🔴 PARADO' }}</strong></p>
        </body>
        </html>
    """, ativo=MOVIMENTO_ATIVO, titulo=TITULO)


@app.route("/toggle", methods=["POST"])
def toggle_movimento():
    global MOVIMENTO_ATIVO
    MOVIMENTO_ATIVO = not MOVIMENTO_ATIVO
    print(f"{'🟢 Iniciou' if MOVIMENTO_ATIVO else '🔴 Parou'} o movimento às {datetime.now()}")
    return redirect(url_for("index"))

# ========= EXECUÇÃO =========

if __name__ == "__main__":
    # Inicia leitura da serial em thread separada
    thread = threading.Thread(target=leitura_serial, daemon=True)
    thread.start()

    print("🌐 Acesse http://localhost:5000 para marcar movimentos")
    app.run(host="0.0.0.0", port=5000)
