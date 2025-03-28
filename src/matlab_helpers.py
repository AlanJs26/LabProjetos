from scipy import io
import numpy as np


def load_matlab_data(file: str):
    """
    Load a .mat file. Expect that all data is stored inside the variable `dataset`,
    which is composed of N matrices which columns are organized in:
    accel.X, accel.Y, accel.Z, gyro.X, gyro.Y, gyro.Z
    """
    data = io.loadmat(file)

    return data["dataset"][0], data["continuous_dataset"]


def chunk_data(data, chunk_size):
    """
    Chunk data into smaller pieces of size chunk_size.
    """
    return data[:len(data) - len(data)%chunk_size].reshape(-1, chunk_size, 7)

def extract_classes(data):
    """
    Process data by extracting the most frequent class
    and removing the last column from the data.
    """
    classes = np.zeros(len(data))
    for i, item in enumerate(data):
        classes[i] = np.bincount(item[:, -1].astype(int)).argmax()
    data = data[:, :, :-1]
    return data, classes

def get_data(files: list[str], chunk_size: int = 50):
    """
    Load and process data from a list of .mat files.
    """
    all_data = []
    all_classes = []
    for file in files:
        data = load_matlab_data(file)[1]
        data = chunk_data(data, chunk_size)
        data, classes = extract_classes(data)
        all_data.append(data)
        all_classes.append(classes)
    all_data = np.concatenate(all_data, axis=0)
    all_classes = np.concatenate(all_classes, axis=0)
    return all_data, all_classes