import numpy as np
import copy


class TLO:
    def __init__(self):
        self.thresholds = []

    @staticmethod
    def threshold_lexicographical_sort(data: np.ndarray):
        data = copy.deepcopy(data)
        data *= -1
        data = np.append(data, np.arange(data.shape[0]).reshape(*np.arange(data.shape[0]).shape, -1), axis=1)
        for obj in range(data.shape[1]-1):
            data = data[data[:, (data.shape[1]-obj-2)].argsort()]

        data = np.append(data, np.arange(1, data.shape[0]+1).reshape(*np.arange(1, data.shape[0]+1).shape, -1), axis=1)
        return data[:, -2:].astype(int), data.shape[0]


