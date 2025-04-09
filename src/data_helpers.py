from scipy import io
import numpy as np
import os.path
import yaml


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


def get_data(field: str):
    """
    Load and process data from a list of .mat files.
    """
    with open("config/params.yaml", "r") as f:
        params = yaml.safe_load(f)

    available_classes: list[str] = params["classes"]
    chunk_size = params["timesteps"]
    dataset_description: dict[str, list[str]] = params[field]

    all_data = []
    all_classes = []
    for curr_class, files in dataset_description.items():

        for file in files:
            ext = os.path.splitext(file)[1]
            if ext == ".mat":
                data = load_matlab_data(file)[1]
            elif ext == ".csv":
                data = load_csv_data(file)
            else:
                raise Exception(f"Unknown file extension: {file}")

            data = chunk_data(data, chunk_size)

            class_id = available_classes.index(curr_class)
            if class_id == -1:
                raise Exception(
                    f"Invalid class_id = {class_id}. Check train_params.yaml if your data match the classes"
                )
            class_id += 1

            data, classes = extract_classes(data, class_id)
            all_data.append(data)
            all_classes.append(classes)
    all_data = np.concatenate(all_data, axis=0)
    all_classes = np.concatenate(all_classes, axis=0)
    return all_data, all_classes
