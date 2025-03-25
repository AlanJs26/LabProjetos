from scipy import io


def load_matlab_data(file: str):
    """
    Load a .mat file. Expect that all data is stored inside the variable `dataset`,
    which is composed of N matrices which columns are organized in:
    accel.X, accel.Y, accel.Z, gyro.X, gyro.Y, gyro.Z
    """
    data = io.loadmat(file)

    return data["dataset"][0], data["continuous_dataset"][0]
