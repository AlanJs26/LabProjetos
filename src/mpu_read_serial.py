from flask import Flask, render_template_string, request, redirect, url_for, jsonify
from datetime import datetime
import threading
import csv
import os
import serial
import time
import sys
from src.visualizer import visualizar_realtime

app = Flask(__name__)
MOVIMENTO_ATIVO = False
TITULO = ""


# ========= THREAD: LEITURA SERIAL =========
def leitura_serial(titulo: str, porta_serial: str, baudrate: int):
    global MOVIMENTO_ATIVO
    global TITULO

    TITULO = titulo

    os.makedirs("dataset", exist_ok=True)
    csv_path = f"./dataset/{titulo.casefold().replace(' ', '_')}.csv"

    # Garante nome único
    while os.path.isfile(csv_path):
        csv_path = os.path.splitext(csv_path)[0] + "-novo.csv"

    print(f"📁 Salvando em: {csv_path}")

    try:
        ser = serial.Serial(porta_serial, baudrate, timeout=1)
        time.sleep(2)
        print(f"📡 Conectado à {porta_serial}")
    except serial.SerialException:
        print("⚠️ Erro ao abrir a porta serial!")
        return

    atualizar_visualizacao, parada_visualizacao = visualizar_realtime()

    with open(csv_path, mode="w", newline="") as file:
        writer = csv.writer(file)
        writer.writerow(
            [
                "timestamp",
                "ax1",
                "ay1",
                "az1",
                "gx1",
                "gy1",
                "gz1",
                "ax2",
                "ay2",
                "az2",
                "gx2",
                "gy2",
                "gz2",
                "em_movimento",
            ]
        )

        try:
            while not parada_visualizacao["sair"]:
                linha = ser.readline().decode("utf-8").strip()

                if not linha:
                    continue

                dados = linha.split(",")
                try:
                    dados_float = [float(valor) for valor in dados]
                    if len(dados_float) != 12:
                        continue

                    timestamp = datetime.now().timestamp()
                    linha_completa = [timestamp] + dados_float + [int(MOVIMENTO_ATIVO)]

                    writer.writerow(linha_completa)
                    print(",".join([str(l) for l in linha_completa]))

                    atualizar_visualizacao(*linha_completa)

                except ValueError:
                    print("⚠️ Dado inválido! Encerrando leitura.")
                    break
        except KeyboardInterrupt:
            pass

        print("🛑 Leitura serial encerrada.")

    ser.close()


# ========= FLASK APP =========


@app.route("/")
def index():
    global MOVIMENTO_ATIVO
    return render_template_string(
        """
        <html>
        <head>
            <title>Marcador de Movimento</title>
            <style>
                body {
                    font-family: Arial; text-align: center; padding: 30px;
                    display: flex; flex-direction: column; height: 100vh; margin: 0; padding: 0;
                }
                button {
                    font-size: 30px; padding: 20px 40px; border-radius: 12px; height: 100%;
                    border: none; color: white;
                    background-color: #007BFF;
                }
            </style>
            <script>
                function setMovimento(ativo) {
                    const btn = document.getElementById('btn')
                    btn.style.background = ativo ? 'green' : '#007BFF'
                    fetch('/set_movimento', {
                        method: 'POST',
                        headers: {
                            'Content-Type': 'application/json',
                        },
                        body: JSON.stringify({ativo: ativo})
                    });
                }
            </script>
        </head>
        <body>
            <h1>Movimento: {{ titulo }}</h1>
            <button 
                onmousedown="setMovimento(true)" 
                onmouseup="setMovimento(false)"
                ontouchstart="setMovimento(true)" 
                ontouchend="setMovimento(false)"
                id="btn"
            >
                Pressione para mover
            </button>
        </body>
        </html>
    """,
        ativo=MOVIMENTO_ATIVO,
        titulo=TITULO,
    )


@app.route("/set_movimento", methods=["POST"])
def set_movimento():
    global MOVIMENTO_ATIVO
    data = request.get_json()
    MOVIMENTO_ATIVO = data["ativo"]
    print(
        f"{'🟢 Iniciou' if MOVIMENTO_ATIVO else '🔴 Parou'} o movimento às {datetime.now()}"
    )
    return jsonify(success=True)


# ========= EXECUÇÃO =========

if __name__ == "__main__":
    # TITULO = input("Nome do Movimento: ").strip()
    titulo = sys.argv[1].strip()

    # Inicia leitura da serial em thread separada
    thread = threading.Thread(
        target=leitura_serial, daemon=True, args=(titulo, "COM5", 115200)
    )
    thread.start()

    print("🌐 Acesse http://localhost:5000 para marcar movimentos")
    app.run(host="0.0.0.0", port=5000)
