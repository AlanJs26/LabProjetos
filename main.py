import typer
from pathlib import Path

app = typer.Typer(context_settings={"help_option_names": ["-h", "--help"]})

@app.command()
def train(model_name: str = "model"):
    """
    Train model and save it into './models/{model_name}.h5'
    """
    from src.train_lib import train_model

    train_model("train_data", model_name)


@app.command()
def metrics(model_name: str = "model", n_pred: int = 100):
    """
    Load model and show a confusion matrix\n

    --n-pred : number of predictions to construct the confusion matrix
    """
    from src.train_lib import load_classifier
    import numpy as np
    from sklearn.metrics import confusion_matrix, accuracy_score
    from src.data_helpers import get_data
    import yaml
    from tqdm import tqdm

    with open("config/params.yaml", "r") as f:
        params = yaml.safe_load(f)

    data, classes = get_data("test_data")

    classify_gesture = load_classifier(model_name)

    # Seleciona N elementos aleatórios de data e classes
    indices = np.random.choice(len(data), size=len(data) if n_pred <= 0 else min(n_pred, len(data)), replace=False)
    X_test = [data[i] for i in indices]
    y_test = [classes[i] for i in indices]

    # Inicializa listas para armazenar as classes previstas e reais
    y_pred = []
    y_true = []

    # Realiza a classificação e armazena os resultados com barra de progresso
    for i in tqdm(range(len(X_test)), desc="Classifying"):
        classe_predita = classify_gesture(np.expand_dims(X_test[i], axis=0))
        y_pred.append(classe_predita)
        y_true.append(y_test[i])

    # Calcula a confusion matrix
    cm = confusion_matrix(y_true, y_pred)
    print("Acuracia: ", accuracy_score(y_true, y_pred))

    from sklearn.metrics import ConfusionMatrixDisplay
    import matplotlib.pyplot as plt

    disp = ConfusionMatrixDisplay(
        confusion_matrix=cm, display_labels=["none"] + params["classes"]
    )
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

    try:
        # Inicia leitura da serial em thread separada
        thread = threading.Thread(
            target=leitura_serial, args=(classe, COM, baudrate), daemon=True
        )
        thread.start()

        flask_app.run(host="0.0.0.0", port=5000)
    except KeyboardInterrupt:
        import os
        os._exit(1)


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
