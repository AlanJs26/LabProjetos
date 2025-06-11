from flask import Flask, render_template, request, jsonify
from flask_socketio import SocketIO
import time
import serial
from src.train_lib import load_classifier
import numpy as np
import yaml
from src.data_helpers import get_classes
from src.data_helpers import preload_data

preload_data("config/params.yaml", use_cache=True)

app = Flask(__name__, template_folder="flask", static_folder="flask/static")
socketio = SocketIO(app)
thread = None

data = []
MOVIMENTO_ATIVO = False
RUNNING = False

classes = get_classes()

def serial_thread(porta_serial: str, baudrate: int, timesteps: int, model_name: str):
    global RUNNING
    global classes
    global data

    RUNNING = True

    try:
        ser = serial.Serial(porta_serial, baudrate, timeout=1)
        time.sleep(2)
        print(f"📡 Conectado à {porta_serial}")
    except serial.SerialException:
        print("⚠️ Erro ao abrir a porta serial!")
        return

    classify_gesture = load_classifier(model_name)

    data = []
    try:
        while RUNNING:
            linha = ser.readline().decode("utf-8").strip()

            if not linha:
                print("⚠️ Linha vazia recebida!")
                continue

            try:
                dados_float = [float(valor) for valor in linha.split(",")]
                if len(dados_float) != 12:
                    continue
                
                if MOVIMENTO_ATIVO:
                    data.append(dados_float)

                if len(data) == timesteps:
                # if len(data)>0 and not MOVIMENTO_ATIVO:
                    prediction = classify_gesture(
                        np.expand_dims(np.array(data), axis=0)
                    )
                    if prediction > 0:
                        socketio.emit("movimento", classes[prediction])
                    data = []

            except ValueError:
                print("⚠️ Dado inválido!")
                continue
    except KeyboardInterrupt:
        pass

    print("🛑 Leitura serial encerrada.")
    ser.close()


@socketio.on("connect")
def connect():
    print("🌐 CONNECTED")


@app.route("/")
def index():
    global classes
    return render_template("index.html", classes=classes)

@app.route("/set_movimento", methods=["POST"])
def set_movimento():
    global MOVIMENTO_ATIVO
    global data
    response = request.get_json()
    if response['ativo'] == True:
        data = []
    MOVIMENTO_ATIVO = response["ativo"]
    print(
        f"{'🟢 Iniciou' if MOVIMENTO_ATIVO else '🔴 Parou'} o movimento"
    )
    return jsonify(success=True)


def run_webapp(porta_serial: str, baudrate: int, timesteps: int, model_name: str):
    global RUNNING

    thread = socketio.start_background_task(serial_thread, porta_serial, baudrate, timesteps, model_name)  # type: ignore
    socketio.run(app)
    RUNNING = False
