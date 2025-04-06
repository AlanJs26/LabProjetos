import numpy as np
import keras
from keras import layers
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.base import BaseEstimator, TransformerMixin
from src.data_helpers import get_data
import os
from pathlib import Path
import joblib

MODEL_FOLDER = Path("models")


def load_classifier(name: str):
    return build_classifier(load_model(name), load_preprocessor(name))


# Transformers personalizados para redimensionamento
class ReshapeTo2D(BaseEstimator, TransformerMixin):
    def fit(self, X, y=None):
        return self

    def __sklearn_is_fitted__(self):
        return True

    def transform(self, X):
        return X.reshape(-1, X.shape[2])


class ReshapeTo3D(BaseEstimator, TransformerMixin):
    def __init__(self, timesteps, num_features):
        self.timesteps = timesteps
        self.num_features = num_features

    def fit(self, X, y=None):
        return self

    def __sklearn_is_fitted__(self):
        return True

    def transform(self, X):
        return X.reshape(-1, self.timesteps, self.num_features)


def train_model(dataset_name: str, name: str):
    import yaml

    with open("config/params.yaml", "r") as f:
        params = yaml.safe_load(f)

    # Carregar dados
    data, classes = get_data(dataset_name)

    num_features = data.shape[2]
    timesteps = params["timesteps"]

    # Divisão treino/teste (corrigindo vazamento de dados)
    X_train, X_test, y_train, y_test = train_test_split(
        data, classes, test_size=0.2, random_state=42
    )

    # Pipeline de pré-processamento
    preprocessing_pipe = Pipeline(
        [
            ("reshape2d", ReshapeTo2D()),
            ("scaler", StandardScaler()),
            ("reshape3d", ReshapeTo3D(timesteps=timesteps, num_features=num_features)),
        ]
    )

    # Aplicar pré-processamento
    X_train_preprocessed = preprocessing_pipe.fit_transform(X_train)
    X_test_preprocessed = preprocessing_pipe.transform(X_test)

    # Converter labels para one-hot encoding
    y_train_cat = keras.utils.to_categorical(y_train, 3)
    y_test_cat = keras.utils.to_categorical(y_test, 3)

    # Construir modelo LSTM
    model = keras.Sequential(
        [
            layers.LSTM(
                64, return_sequences=True, input_shape=(timesteps, num_features)
            ),
            layers.LSTM(32),
            layers.Dense(32, activation="relu"),
            layers.Dense(3, activation="softmax"),
        ]
    )

    model.compile(
        optimizer="adam", loss="categorical_crossentropy", metrics=["accuracy"]
    )

    # Treinar modelo
    model.fit(
        X_train_preprocessed,
        y_train_cat,
        validation_data=(X_test_preprocessed, y_test_cat),
        epochs=20,
        batch_size=16,
    )

    # Salvar componentes
    save_model(model, name)
    save_preprocessor(preprocessing_pipe, name)

    return build_classifier(model, preprocessing_pipe)


def build_classifier(model, preprocessor):
    def classify_gesture(raw_data):
        processed_data = preprocessor.transform(raw_data)
        return np.argmax(model.predict(processed_data))

    return classify_gesture


# Save / Load preprocessor
def save_preprocessor(preprocessor, name):
    filepath = MODEL_FOLDER / f"preprocessing_pipe_{name}.pkl"
    os.makedirs(MODEL_FOLDER, exist_ok=True)
    joblib.dump(preprocessor, filepath, compress=9)
    print(f"Preprocessor saved to {filepath}")


def load_preprocessor(name):
    from sklearn.utils.validation import check_is_fitted

    preprocessor = joblib.load(MODEL_FOLDER / f"preprocessing_pipe_{name}.pkl")
    check_is_fitted(preprocessor)
    return preprocessor


# Save / Load model
def save_model(model, name):
    filepath = MODEL_FOLDER / f"{name}.keras"
    os.makedirs(MODEL_FOLDER, exist_ok=True)
    model.save(filepath)
    print(f"Model saved to {filepath}")


def load_model(name):
    filepath = MODEL_FOLDER / f"{name}.keras"
    if not filepath.is_file():
        raise FileNotFoundError(f"No model file found at {filepath}")
    model = keras.models.load_model(filepath)
    print(f"Model loaded from {filepath}")
    return model
