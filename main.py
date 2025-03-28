from src.matlab_helpers import load_matlab_data, get_data
import numpy as np
from src.train import load_classifier, train
from sklearn.metrics import confusion_matrix

datasets = ["matlab_datasets/ippon-dataset.mat", "matlab_datasets/wazari-dataset.mat"]

timesteps = 50  # Janela de 50 amostras
num_features = 6  # Aceleração e orientação nos eixos X, Y, Z

data, classes = get_data(datasets, chunk_size=timesteps)
classify_gesture = load_classifier("model/lstm_model.h5", "model/scaler.pkl", timesteps, num_features)
# classify_gesture = train(datasets)

N = 300

# Seleciona N elementos aleatórios de data e classes
indices = np.random.choice(len(data), size=N, replace=False)
X_test = [data[i] for i in indices]
y_test = [classes[i] for i in indices]

# Inicializa listas para armazenar as classes previstas e reais
y_pred = []
y_true = []

# Realiza a classificação e armazena os resultados
for i in range(N):
    classe_predita = classify_gesture(X_test[i])
    y_pred.append(classe_predita)
    y_true.append(y_test[i])

# Calcula a confusion matrix
cm = confusion_matrix(y_true, y_pred)

# Exibe a confusion matrix em formato de texto
print("Confusion Matrix:")
for row in cm:
    print(" ".join(map(str, row)))


# from src.cronometro import cronometro
# cronometro()
