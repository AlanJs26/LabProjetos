from scipy import io
import numpy as np
import os.path


def load_matlab_data(file: str):
    """
    Load a .mat file. Expect that all data is stored inside the variable `dataset`,
    which is composed of N matrices which columns are organized in:
    accel.X, accel.Y, accel.Z, gyro.X, gyro.Y, gyro.Z
    """
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
    return data[: len(data) - len(data) % chunk_size].reshape(-1, chunk_size, 7)


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
        ext = os.path.splitext(file)[1]
        if ext == ".mat":
            data = load_matlab_data(file)[1]
        elif ext == ".csv":
            data = load_csv_data(file)
        else:
            raise Exception(f"Unknown file extension: {file}")
        data = chunk_data(data, chunk_size)
        data, classes = extract_classes(data)
        all_data.append(data)
        all_classes.append(classes)
    all_data = np.concatenate(all_data, axis=0)
    all_classes = np.concatenate(all_classes, axis=0)
    return all_data, all_classes

