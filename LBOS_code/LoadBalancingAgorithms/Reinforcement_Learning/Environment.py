import numpy as np
from LoadBalancingAgorithms.Reinforcement_Learning import State
from LoadBalancingAgorithms.Reinforcement_Learning.Sorting_methods import Sort


class Environment:
    def __init__(self, action_space_size):
        self.action_space_size_allocation = action_space_size
        self.observation_space_size_allocation = 3 ** self.action_space_size_allocation
        self.Q_table_allocation = np.zeros((self.observation_space_size_allocation, self.action_space_size_allocation))
        self.state = State.State(self.action_space_size_allocation)
        self.Q_table_updates = {}  # dict for indexes to be updated and time for updating.
        self.number_objectives = 4
        self.Q_table_MO = np.empty((self.observation_space_size_allocation, self.action_space_size_allocation),  dtype=
                                                            object)
        self.init_mo_table()
        # self.sorting_algorithm = NonDominatingSorting.NonDominatingSorting()
        self.sorter = Sort.Sort()

    def init_mo_table(self):
        for row in range(self.Q_table_MO.shape[0]):
            for col in range(self.Q_table_MO.shape[1]):
                self.Q_table_MO[row][col] = np.zeros(self.number_objectives)

    def random_action(self, indexes, seed):
        # check correct!
        return seed.choice(indexes)

    def sort_update_q_table(self, state, sort_type):
        data = self.Q_table_MO[state]
        data = np.stack(data)

        solutions, rev_num = self.sorter(sort_type, np.array(data))

        self.update_q_table(state, solutions, rev_num)

    def update_q_table(self, state, solutions, rev_num):
        for pair in solutions:
            self.Q_table_allocation[state][pair[0]] = rev_num - pair[1]

    def initialize_q_table(self):
        self.Q_table_allocation = np.zeros((self.observation_space_size_allocation, self.action_space_size_allocation))
        self.state.state_counter = 0
        self.state.state_dict.clear()
