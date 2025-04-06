import typer
from pathlib import Path

app = typer.Typer(context_settings={"help_option_names": ["-h", "--help"]})

datasets = [
    "matlab_datasets/ippon-dataset.mat",
    "matlab_datasets/wazari-dataset.mat",
]


@app.command()
def train(model_name: str = "model", timesteps: int = 50):
    """
    Train model and save it into './models/{model_name}.h5'\n

    --timesteps : number of data elements to feed the model and once
    """
    from src.train_lib import train_model

    train_model(datasets, model_name, timesteps)


@app.command()
def metrics(model_name: str = "model", n_pred: int = 100, timesteps: int = 50):
    """
    Load model and show a confusion matrix\n

    --n-pred : number of predictions to construct the confusion matrix\n
    --timesteps : number of data elements to feed the model and once
    """
    from src.train_lib import load_classifier
    import numpy as np
    from sklearn.metrics import confusion_matrix
    from src.data_helpers import get_data

    data, classes = get_data(datasets, chunk_size=timesteps)

    classify_gesture = load_classifier(model_name)

    # Seleciona N elementos aleatórios de data e classes
    indices = np.random.choice(len(data), size=n_pred, replace=False)
    X_test = [data[i] for i in indices]
    y_test = [classes[i] for i in indices]

    # Inicializa listas para armazenar as classes previstas e reais
    y_pred = []
    y_true = []

    # Realiza a classificação e armazena os resultados
    for i in range(n_pred):
        classe_predita = classify_gesture(np.expand_dims(X_test[i], axis=0))
        y_pred.append(classe_predita)
        y_true.append(y_test[i])

    # Calcula a confusion matrix
    cm = confusion_matrix(y_true, y_pred)

    from sklearn.metrics import ConfusionMatrixDisplay
    import matplotlib.pyplot as plt

    disp = ConfusionMatrixDisplay(confusion_matrix=cm)
    disp.plot(cmap="viridis", values_format="d")
    plt.title("Matriz de Confusão")
    plt.show()


@app.command()
def captura(classe: str, COM: str = "COM5", baudrate: int = 115200):
    """
    Lê os dados da IMU enviados via serial, classifica-os utilizando uma interface web e os salva em um arquivo .csv na pasta ./dataset \n

    --classe : classe do movimento em captura\n
    --COM : porta serial em que os dados serão recebidos\n
    --baudrate : frequencia da porta serial
    """
    import threading
    from src.mpu_read_serial import leitura_serial
    from src.mpu_read_serial import app as flask_app

    # Inicia leitura da serial em thread separada
    thread = threading.Thread(
        target=leitura_serial, args=(classe, COM, baudrate), daemon=True
    )
    thread.start()

    flask_app.run(host="0.0.0.0", port=5000)


@app.command()
def visualize(file: Path):
    """
    Visualiza uma das capturas salvas em um arquivo .csv
    """
    import pandas as pd
    from src.visualizer import visualizar_dataframe

    df = pd.read_csv(file)
    visualizar_dataframe(df)


@app.command()
def web(
    COM: str = "COM5",
    baudrate: int = 115200,
    timesteps: int = 50,
    model_name: str = "model",
):
    """
    Hospeda uma página web para visualização das detecções do modelo em tempo real\n

    --timesteps : number of data elements to feed the model and once\n
    --COM : porta serial em que os dados serão recebidos\n
    --baudrate : frequencia da porta serial
    """
    from src.webapp import run_webapp

    run_webapp(COM, baudrate, timesteps, model_name)


if __name__ == "__main__":
    app()
