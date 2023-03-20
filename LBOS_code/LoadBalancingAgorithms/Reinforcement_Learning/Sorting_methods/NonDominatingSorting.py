import numpy as np


class NonDominatingSorting:
    @staticmethod
    def get_dominant_number(data: np.ndarray):
        dominated_number = np.zeros(shape=data.shape[0], dtype='float32')
        for i in range(data.shape[0]):
            w = (data[i] < data).any(axis=1)
            z = (data[i] <= data).all(axis=1)
            domination_value = np.argwhere(w & z).flatten()
            dominated_number[i] = domination_value.shape[0]
        return dominated_number

    @staticmethod
    def get_domination_list(data: np.ndarray):
        domination = [[] for _ in range(data.shape[0])]
        for i in range(data.shape[0]):
            x = (data[i] >= data).all(axis=1)
            y = (data[i] > data).any(axis=1)
            current_dominated = np.argwhere((x & y)).flatten()
            domination[i].extend(current_dominated.tolist())
        return domination

    def non_dominating_sort(self, data: np.ndarray):
        solution, indices = [], []
        dominated_by, domination = self.get_dominant_number(data), self.get_domination_list(data)
        cnt = 0
        while len(solution) != data.shape[0]:
            cnt += 1
            indexes = np.where(dominated_by == 0)[0]
            if len(indexes) == 0:
                break
            best_sol = data[indexes]
            for sol, idx in zip(best_sol, indexes):
                solution.append((idx, cnt))
            indices.extend(indexes)
            for idx in indexes:
                for value in domination[idx]:
                    dominated_by[value] -= 1
                dominated_by[idx] = 100000
        # return [np.array(indices), solution]

        return solution, cnt
