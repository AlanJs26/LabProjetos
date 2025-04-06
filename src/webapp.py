from flask import Flask, render_template
from flask_socketio import SocketIO
import time
import serial
from src.train_lib import load_classifier
import numpy as np
import yaml

app = Flask(__name__, template_folder="flask", static_folder="flask/static")
socketio = SocketIO(app)
thread = None

RUNNING = False

with open("config/params.yaml", "r") as f:
    params = yaml.safe_load(f)
classes = ["none"] + params["classes"]


def serial_thread(porta_serial: str, baudrate: int, timesteps: int, model_name: str):
    global RUNNING
    global classes

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
                continue

            try:
                dados_float = [float(valor) for valor in linha.split(",")]
                if len(dados_float) != 12:
                    continue

                data.append(dados_float)

                if len(data) == timesteps:
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


def run_webapp(porta_serial: str, baudrate: int, timesteps: int, model_name: str):
    global RUNNING

    thread = socketio.start_background_task(target=serial_thread, args=(porta_serial, baudrate, timesteps, model_name))  # type: ignore
    socketio.run(app)
    RUNNING = False
