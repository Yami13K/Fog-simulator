import numpy as np
import copy
from LoadBalancingAgorithms.Reinforcement_Learning import Environment


class RAA:
    def __init__(self, space_size, episodes=5, decay=0.99, gamma=0.1, lr=0.1, epsilon=0.4):
        self.episodes = episodes
        self.epsilon = epsilon
        self.episodes_epsilon = epsilon
        self.decay = decay
        self.gamma = gamma
        self.lr = lr
        self.environment = Environment.Environment(space_size)

    def __call__(self, servers, task):
        return self.rl_algorithm(servers, task)

    @staticmethod
    def get_reward(org_state, invalid_state):
        if org_state.count(1) == len(org_state):  # goal reached
            return 50
        if sum(org_state) == 3:
            return 15
        if sum(org_state) == 2 or sum(org_state) == 4:
            return 5
        if sum(org_state) == 5:
            return -25
        return -50

    def assign_task(self, task, action, servers_snapshot):
        if servers_snapshot[action].is_free():
            dv_idx = servers_snapshot[action].free_devices[0]
            servers_snapshot[action].devices[dv_idx].task_in_execution = task

        # ELSE add to the queue.
        org_state, encoded_current_state, invalid_state = self.environment.state.get_current_state(servers_snapshot)
        reward = self.get_reward(org_state, invalid_state)
        return encoded_current_state, reward, invalid_state

    def rl_algorithm(self, servers_snapshot, task):
        copy_task = copy.deepcopy(task)

        # we are clearing the table, because after each task, the system changed... which means
        # old rewards are no longer reliable.
        self.environment.initialize_q_table()
        _, current_state, invalid_state = self.environment.state.get_current_state(servers_snapshot)
        self.episodes_epsilon = self.epsilon

        for episode in range(self.episodes):

            # action is the server number (shouldn't stuck in the loop).
            while True:
                if np.random.rand() < self.episodes_epsilon:
                    action = self.environment.random_action()
                else:
                    action = np.argmax(self.environment.Q_table_allocation[current_state, :])

                if servers_snapshot[action].able_to_receive():
                    break

            next_state, reward, invalid_state = self.assign_task(copy_task, action, servers_snapshot)
            temp_diff = reward + self.gamma * np.max(self.environment.Q_table_allocation[next_state]) - \
                        self.environment.Q_table_allocation[current_state, action]

            self.environment.Q_table_allocation[current_state, action] += (self.lr * temp_diff)
            self.episodes_epsilon *= self.decay

            # Its only one step problem.
            # current_state = next_state

            # undo the action to start over.
            servers_snapshot[action].task_in_execution = None

        return np.argmax(self.environment.Q_table_allocation[current_state])

