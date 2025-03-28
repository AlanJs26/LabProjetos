import numpy as np
import keras
from keras import layers
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from src.matlab_helpers import get_data
import os
import joblib

def train(datasets: list[str]):
    # Simulação de dados (Substitua por seus dados reais)
    timesteps = 50  # Janela de 50 amostras
    num_features = 6  # Aceleração e orientação nos eixos X, Y, Z

    data, classes = get_data(datasets, chunk_size=timesteps)
    
    # Normalização dos dados
    scaler = StandardScaler()

    X = data.reshape(-1, num_features)  # Ajuste para o formato correto
    X = scaler.fit_transform(X)  # Normalização
    X = X.reshape(-1, timesteps, num_features)  # Voltar ao formato original

    # Convertendo rótulos para one-hot encoding
    y = keras.utils.to_categorical(classes, num_classes=3)

    # Divisão em treino e teste
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

    # Construção da Rede LSTM
    model = keras.Sequential([
        layers.LSTM(64, return_sequences=True, input_shape=(timesteps, num_features)),
        layers.LSTM(32),
        layers.Dense(32, activation="relu"),
        layers.Dense(3, activation="softmax")  # 3 classes
    ])

    # Compilação do modelo
    model.compile(optimizer="adam", loss="categorical_crossentropy", metrics=["accuracy"])

    # Treinamento
    model.fit(X_train, y_train, epochs=20, batch_size=16, validation_data=(X_test, y_test))

    # Salvar o scaler
    save_scaler(scaler, "model/scaler.pkl")
    save_model(model, "model/lstm_model.h5")

    # Avaliação
    loss, acc = model.evaluate(X_test, y_test)
    print(f"Acurácia: {acc:.4f}")

    # Criar a função de classificação usando build_classify_gesture_function
    classify_gesture = build_classify_gesture_function(model, scaler, timesteps, num_features)

    return classify_gesture

def build_classify_gesture_function(model, scaler, timesteps, num_features):
    """
    Build a function to classify gestures using the trained model.

    Args:
        model: The trained Keras model.
        scaler: The scaler used for normalization.
        timesteps: Number of timesteps in the input data.
        num_features: Number of features in the input data.

    Returns:
        A function that takes raw data and returns the predicted class.
    """
    def classify_gesture(data):
        data = scaler.transform(data.reshape(-1, num_features)).reshape(1, timesteps, num_features)
        pred = model.predict(data)
        return np.argmax(pred)  # Retorna a classe com maior probabilidade

    return classify_gesture

def save_model(model, filepath):
    """
    Save the trained model to a file.

    Args:
        model: The trained Keras model.
        filepath: Path to save the model file.
    """
    os.makedirs(os.path.dirname(filepath), exist_ok=True)
    model.save(filepath)
    print(f"Model saved to {filepath}")

def load_model(filepath):
    """
    Load a trained model from a file.

    Args:
        filepath: Path to the saved model file.

    Returns:
        The loaded Keras model.
    """
    if not os.path.exists(filepath):
        raise FileNotFoundError(f"No model file found at {filepath}")
    model = keras.models.load_model(filepath)
    print(f"Model loaded from {filepath}")
    return model

def save_scaler(scaler, filepath):
    """
    Save the scaler to a file.

    Args:
        scaler: The scaler object to save.
        filepath: Path to save the scaler file.
    """
    os.makedirs(os.path.dirname(filepath), exist_ok=True)
    joblib.dump(scaler, filepath)
    print(f"Scaler saved to {filepath}")

def load_scaler(filepath):
    """
    Load a scaler from a file.

    Args:
        filepath: Path to the saved scaler file.

    Returns:
        The loaded scaler object.
    """
    if not os.path.exists(filepath):
        raise FileNotFoundError(f"No scaler file found at {filepath}")
    scaler = joblib.load(filepath)
    print(f"Scaler loaded from {filepath}")
    return scaler

def load_classifier(model_filepath, scaler_filepath, timesteps, num_features):
    """
    Load the model and scaler from files and create the classification function.

    Args:
        model_filepath: Path to the saved model file.
        scaler_filepath: Path to the saved scaler file.
        timesteps: Number of timesteps in the input data.
        num_features: Number of features in the input data.

    Returns:
        A function that takes raw data and returns the predicted class.
    """
    model = load_model(model_filepath)
    scaler = load_scaler(scaler_filepath)
    classify_gesture = build_classify_gesture_function(model, scaler, timesteps, num_features)
    return classify_gesture