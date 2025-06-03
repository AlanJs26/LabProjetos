from functools import reduce
import numpy as np
import os.path
from numpy.typing import NDArray
import yaml
from glob import glob
from sklearn.model_selection import train_test_split
import pickle
from tsaug import TimeWarp, Crop, Quantize, Drift, Reverse
from collections import Counter
from typing import Literal

RANDOM_STATE = 42
np.random.seed(RANDOM_STATE)
preloaded = False


def load_matlab_data(file: str):
    """
    Load a .mat file. Expect that all data is stored inside the variable `dataset`,
    which is composed of N matrices which columns are organized in:
    accel.X, accel.Y, accel.Z, gyro.X, gyro.Y, gyro.Z
    """
    from scipy import io

    data = io.loadmat(file)

    return data["dataset"][0], data["continuous_dataset"]


def load_csv_data(file: str):
    # timestamp,ax1,ay1,az1,gx1,gy1,gz1,ax2,ay2,az2,gx2,gy2,gz2,em_movimento
    # shape = (:, 14)
    data = np.genfromtxt(file, delimiter=",", skip_header=1)

    # ignore timestamp
    return data[:, 1:]


def chunk_data(data, chunk_size):
    """
    Chunk data into smaller pieces of size chunk_size.
    """
    length = data.shape[0]
    num_features = data.shape[1]
    return data[: length - length % chunk_size, :].reshape(-1, chunk_size, num_features)


def extract_classes(data, class_id: int):
    """
    Process data by extracting the most frequent class
    and removing the last column from the data.
    """
    classes = np.zeros(len(data))
    for i, item in enumerate(data):
        classes[i] = (
            0 if np.bincount(item[:, -1].astype(int)).argmax() == 0 else class_id
        )
    data = data[:, :, :-1]
    return data, classes


def aplicar_undersampling(
    x_data: np.ndarray, y_data: np.ndarray, verbose: bool = True
) -> tuple[np.ndarray, np.ndarray]:
    """
    Aplica a técnica de undersampling aos dados fornecidos.

    Args:
        x_data (np.ndarray): Array NumPy contendo as características (features).
        y_data (np.ndarray): Array NumPy contendo os rótulos das classes.
        verbose (bool): Se True, imprime mensagens sobre o processo de undersampling.

    Returns:
        tuple[np.ndarray, np.ndarray]: Uma tupla contendo os arrays x_data e y_data
                                       após o undersampling. Se o undersampling não for
                                       aplicável (ex: dados vazios, uma única classe),
                                       retorna os dados originais.
    """
    if x_data.shape[0] == 0:
        if verbose:
            print("\nIgnorando undersampling: Dados de entrada vazios.")
        return x_data, y_data

    # Usar Counter para obter contagens para a mensagem de log inicial
    contagens_iniciais_dict = Counter(y_data)

    # np.unique é útil para obter as classes únicas e suas contagens para o processamento
    classes_unicas, contagens_np = np.unique(y_data, return_counts=True)

    if len(classes_unicas) <= 1:
        if verbose:
            print(
                "\nIgnorando undersampling: Apenas uma classe ou sem diversidade de classes nos dados de entrada."
            )
        return x_data, y_data

    if verbose:
        print("\nRealizando undersampling...")
        print(f"Contagem original das classes: {dict(contagens_iniciais_dict)}")

    # Determina o número de amostras da classe minoritária
    min_amostras = min(contagens_np)

    if verbose:
        print(f"Amostras por classe após undersampling (minoria): {min_amostras}")

    lista_x_subamostrados = []
    lista_y_subamostrados = []

    for rotulo_classe in classes_unicas:
        # Encontra os índices para a classe atual
        indices_da_classe = np.where(y_data == rotulo_classe)[0]

        # Seleciona aleatoriamente 'min_amostras' índices para esta classe
        # O argumento 'replace=False' garante que não selecionamos o mesmo índice múltiplas vezes
        indices_aleatorios = np.random.choice(
            indices_da_classe, size=min_amostras, replace=False
        )

        # Adiciona os dados e rótulos selecionados às listas
        lista_x_subamostrados.extend(x_data[indices_aleatorios])
        lista_y_subamostrados.extend(y_data[indices_aleatorios])

    # Converte as listas para arrays numpy
    novos_x_data = np.array(lista_x_subamostrados)
    novos_y_data = np.array(lista_y_subamostrados)

    # Embaralha os dados subamostrados combinados para garantir
    # que as amostras de diferentes classes estejam misturadas
    indices_permutados = np.random.permutation(len(novos_x_data))
    novos_x_data = novos_x_data[indices_permutados]
    novos_y_data = novos_y_data[indices_permutados]

    if verbose:
        contagens_finais = Counter(novos_y_data)
        print(f"Contagem das classes após undersampling: {dict(contagens_finais)}")
        print("Undersampling concluído.")

    return novos_x_data, novos_y_data


def split_none_class(data, classes):
    def reduce_callback(acc, pair):
        d, is_none = pair

        if is_none:
            acc[0].append(d)
        else:
            acc[1].append(d)

        return acc

    none_data, class_data = reduce(reduce_callback, zip(data, classes), ([], []))
    return np.array(none_data), np.array(class_data)


train_data = {"x": np.array([]), "y": np.array([])}
test_data = {"x": np.array([]), "y": np.array([])}
all_classes = []


def preload_data(params_file: str, use_cache=False):
    global train_data
    global test_data
    global all_classes

    new_data = {}

    if use_cache and os.path.isfile("cache.pickle"):
        with open("cache.pickle", "rb") as f:
            train_data, test_data, all_classes = pickle.load(f)
    else:
        with open(params_file, "r") as f:
            params = yaml.safe_load(f)

        ignored_classes = params["ignored_classes"]
        class_pairs: list[tuple[str, str]] = list(
            filter(
                lambda x: x[1] not in ignored_classes,
                map(
                    lambda x: tuple(x.split(":", 1)),
                    params["classes"],
                ),
            )
        )
        available_classes = list(map(lambda x: x[1], class_pairs))
        chunk_size = params["timesteps"]

        augmenter = (
            TimeWarp() * 5  # random time warping 5 times in parallel
            + Quantize(
                n_levels=[10, 20, 30]
            )  # random quantize to 10-, 20-, or 30- level sets
            + Drift(max_drift=(0.1, 0.5))
            @ 0.8  # with 80% probability, random drift the signal up to 10% - 50%
        )

        for file_class, class_name in class_pairs:
            folder_path = "dataset_folder"
            for filepath in glob(f"{params[folder_path]}/{file_class}*.csv"):
                csv_data = load_csv_data(filepath)

                chunked_data = chunk_data(csv_data, chunk_size)

                class_id = available_classes.index(class_name) + 1
                if class_id == 0:
                    raise Exception(
                        f"Invalid class_id = {class_id}. Check train_params.yaml if your data match the classes"
                    )

                chunked_data, classes = extract_classes(chunked_data, class_id)
                none_data, class_data = split_none_class(chunked_data, classes)

                if "None" not in new_data:
                    new_data["None"] = none_data
                else:
                    new_data["None"] = np.append(new_data["None"], none_data, axis=0)

                if class_name not in new_data:
                    new_data[class_name] = class_data
                else:
                    new_data[class_name] = np.append(
                        new_data[class_name], class_data, axis=0
                    )
            new_data[class_name] = augmenter.augment(new_data[class_name])

        all_classes = ["None"] + available_classes

        new_data_dict = {"x": [], "y": []}
        for field, data in new_data.items():
            class_id = all_classes.index(field)
            new_data_dict["x"].extend(data)
            new_data_dict["y"].extend(np.ones(len(data)) * class_id)

        new_np_data_dict = {"x": np.array([]), "y": np.array([])}
        new_np_data_dict["x"], new_np_data_dict["y"] = aplicar_undersampling(
            np.array(new_data_dict["x"]),
            np.array(new_data_dict["y"]),
            verbose=True,  # Mantenha True para ver os logs ou False para desativá-los
        )
        (
            train_data["x"],  # type: ignore
            test_data["x"],  # type: ignore
            train_data["y"],  # type: ignore
            test_data["y"],  # type: ignore
        ) = train_test_split(
            new_np_data_dict["x"],
            new_np_data_dict["y"],
            test_size=0.2,
            random_state=RANDOM_STATE,
            shuffle=False,
        )

        with open("cache.pickle", "wb") as f:
            pickle.dump([train_data, test_data, all_classes], f)

    print("= Train")
    print(train_data["x"].shape)
    for key, value in zip(*np.unique(train_data["y"], return_counts=True)):
        class_name = all_classes[int(key)]
        print(class_name, value)

    print("\n= Test")
    print(test_data["x"].shape)
    for key, value in zip(*np.unique(test_data["y"], return_counts=True)):
        class_name = all_classes[int(key)]
        print(class_name, value)

    global preloaded
    preloaded = True


def get_data(field: Literal["train", "test"]):
    """
    Load and process data from a list of .mat files.
    """
    global preloaded
    if not preloaded:
        raise Exception("Data not preloaded yet")

    if field == "train":
        return train_data["x"], train_data["y"]
    elif field == "test":
        return test_data["x"], test_data["y"]

    raise Exception("invalid dataset type")


def get_classes():
    global preloaded
    if not preloaded:
        raise Exception("Data not preloaded yet")
    return all_classes
