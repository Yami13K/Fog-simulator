import numpy as np


class Reward:
    def __init__(self, reward_type):
        self.type = reward_type

    @staticmethod
    def inv_sigmoid(x):
        return 1 / (1 + np.exp(0.4*(x-24)))

    @staticmethod
    def utilization_diff(sct_table):
        x = sum([sct_table[index][7] - sct_table[index][2] if sct_table[index][4] == 2 else 0 for index in range(sct_table.shape[0])])

        return x, sct_table[:, 2]

    def __call__(self, sct_table):
        if self.type == 'migration':
            return self.utilization_diff(sct_table)
        if self.type == 'non-linear-MO':
            return self.non_linear_mo_reward(sct_table)
        elif self.type == 'linear-MO':
            return self.linear_mo_reward(sct_table)
        else:
            return self.so_reward(sct_table)

    def inverse_std(self, column):
        diff = np.std(column)
        return self.inv_sigmoid(diff)

    def non_linear_mo_reward(self, sct_table):
        """
        non linear, multi objective reward. (returns a vector of reward objectives)
        """
        utilization = sct_table[:, 2]
        queue_occupation = sct_table[:, 3]
        std_utilization = self.inverse_std(utilization)
        std_occupation = self.inverse_std(queue_occupation)

        return [std_utilization, std_occupation, np.median(utilization), np.median(queue_occupation)], utilization

    def linear_mo_reward(self, sct_table):
        """
        linear, multi objective reward. (using weighted sum)
        """
        utilization = sct_table[:, 2]
        queue_occupation = sct_table[:, 3]
        std_utilization = self.inverse_std(utilization)
        std_occupation = self.inverse_std(queue_occupation)
        return std_utilization + std_occupation + 0.3 * (np.median(utilization)/100) +\
               0.3 * np.median(queue_occupation)/100

    def so_reward(self, sct_table):
        """
        single objective reward. (based on utilization only).
        """
        queue_occupation = sct_table[:, 3]
        utilization = sct_table[:, 2]

        return self.inverse_std(utilization), utilization
