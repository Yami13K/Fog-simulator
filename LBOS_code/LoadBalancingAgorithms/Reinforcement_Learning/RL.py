import numpy as np
import copy
from LoadBalancingAgorithms.Reinforcement_Learning import Environment, Reward
from LoadBalancingAgorithms import Scheduler


class RL:
    def __init__(self, space_size, rl_agent_type, reward_type='migration', sorting_algorithm_name='None', delay_period=20, episodes=10,
                 decay=1, gamma=0.9, lr=0.3, epsilon=1):
        self.rl_agent_type = rl_agent_type
        self.episodes = episodes
        self.epsilon = epsilon
        self.episodes_epsilon = epsilon
        self.decay = decay

        self.gamma = gamma
        self.lr = lr
        self.environment = Environment.Environment(space_size)
        self.number_assigned_tasks = 12  # number of tasks to assign per second.
        self.min_epsilon = 0.1
        self.delay_period = delay_period  # only delay the reward for one second.
        self.reward = Reward.Reward(reward_type)
        self.reward_type = reward_type
        self.over_all_rewards = []
        self.sorting_algorithm_name = sorting_algorithm_name

    def __call__(self, servers, tasks, time_counter, seed, bandwidth_fog_layer=0):
        if self.rl_agent_type == 'migration':
            return self.rl_migration_agent(servers, bandwidth_fog_layer, time_counter, seed)
        else:
            return self.rl_algorithm(servers, tasks, time_counter, seed)

    def rl_algorithm(self, servers_snapshot, tasks, time_counter, seed):
        """
        :param servers_snapshot: a snapshot of the system status.
        :param tasks: the tasks to be assigned.
        :param time_counter: current time.
        :return:
        the reward, next_state, actions of the previous selection (based on the delay value).

        """
        # if time_counter % 1000 == 0:  # start a new episode.
        #    self.episodes_epsilon = self.epsilon

        reward, next_state, actions, utilization = 0, 0, [], []

        # time to get the delayed reward:
        if time_counter in self.environment.Q_table_updates.keys():
            reward, next_state, actions, utilization = self.update_q_table(servers_snapshot, time_counter)
            self.over_all_rewards.append(reward)

        selected_servers = len(tasks) * [-1]

        copy_tasks = copy.deepcopy(tasks)
        _, current_state = self.environment.state.get_current_state(servers_snapshot)

        self.environment.Q_table_updates[time_counter + self.delay_period] = []

        for idx, task in enumerate(copy_tasks):

            capabilities = [server.able_to_receive() for server in servers_snapshot]
            indexes = np.where(np.array(capabilities) == 1)[0]  # only choose from the acceptable solutions.
            if len(indexes) == 0:
                break

            if seed.rand() < self.episodes_epsilon:
                action = self.environment.random_action(indexes, seed)
            else:  # arg max (ranks are in inverse) --> the higher the better. (do this for mo)
                action = indexes[np.argmax(self.environment.Q_table_allocation[current_state, indexes])]

            # perform action:
            servers_snapshot[action].receive_task(task)
            servers_snapshot[action].execute(time_counter, [],  seed)
            selected_servers[idx] = action

            # save action to get the reward later.
            self.environment.Q_table_updates[time_counter + self.delay_period].\
                append((current_state, action))

        self.episodes_epsilon = max(self.episodes_epsilon * self.decay, self.min_epsilon)

        return selected_servers, reward, next_state, actions, utilization

    def rl_migration_agent(self, servers_snapshot, bandwidth_fog_layer, time_counter, seed):
        """
        :param servers_snapshot: a snapshot of the system status.
        :param time_counter: current time.
        :param bandwidth_fog_layer

        :return:
        the reward, next_state, actions of the previous selection (based on the delay value).

        """
        reward, next_state, actions, utilization = 0, 0, [], []
        servers_to_migrate_from = []

        # time to get the delayed reward:
        if time_counter in self.environment.Q_table_updates.keys():
            reward, next_state, actions, utilization = self.update_q_table(servers_snapshot, time_counter)
            self.over_all_rewards.append(reward)

        _, current_state = self.environment.state.get_current_state(servers_snapshot)

        self.environment.Q_table_updates[time_counter + self.delay_period] = []

        for _ in range(2):  # perform migration to 2 of the servers.
            capabilities = [server.number_free_devices() <= server.number_devices for server in servers_snapshot]
            indexes = np.where(np.array(capabilities) == 1)[0]  # only choose from the acceptable solutions.

            # no possible actions.
            if len(indexes) == 0:
                return servers_to_migrate_from, reward, next_state, actions, utilization

            if seed.rand() < self.episodes_epsilon:
                action = self.environment.random_action(indexes, seed)
            else:
                action = indexes[np.argmax(self.environment.Q_table_allocation[current_state, indexes])]

            # perform action: heaviest_task
            dv_id = servers_snapshot[action].mid_heavy_task()

            if dv_id == -1:  # no device suited for migration.
                continue
            Scheduler.Scheduler.perform_migration([(action, dv_id)], servers_snapshot, bandwidth_fog_layer,
                                                  time_counter)
            servers_to_migrate_from.append((action, dv_id))

        self.episodes_epsilon = max(self.episodes_epsilon * self.decay, self.min_epsilon)

        if len(servers_to_migrate_from) == 0: # no possible migrations.
            return servers_to_migrate_from, reward, next_state, actions, utilization

        # save action to get the reward later.
        self.environment.Q_table_updates[time_counter + self.delay_period]. \
                append((current_state, action))

        # in case the delay was zero:
        if time_counter in self.environment.Q_table_updates.keys():
            reward, next_state, actions, utilization = self.update_q_table(servers_snapshot, time_counter)
            self.over_all_rewards.append(reward)

        return servers_to_migrate_from, reward, next_state, actions, utilization

    def update_q_table(self, servers_snapshot, time_counter):
        """
        :return:
        updates the Q-table with the delayed reward.
        """
        state, next_state = self.environment.state.get_current_state(servers_snapshot)
        reward, utilization = self.reward(self.environment.state.sct_table)

        actions = []
        for pair in self.environment.Q_table_updates[time_counter]:
            if self.reward_type == 'non-linear-MO':
                for objective in range(len(reward)):

                    temp_diff = reward[objective] + self.gamma * np.max(self.environment.Q_table_MO[next_state][objective]) \
                                - self.environment.Q_table_MO[pair[0], pair[1]][objective]
                    self.environment.Q_table_MO[pair[0], pair[1]][objective] += (self.lr * temp_diff)
            else:
                temp_diff = reward + self.gamma * np.max(self.environment.Q_table_allocation[next_state]) \
                            - self.environment.Q_table_allocation[pair[0], pair[1]]
                self.environment.Q_table_allocation[pair[0], pair[1]] += (self.lr * temp_diff)

            actions.append(pair[1])

        if self.reward_type == 'non-linear-MO':
            prev_state = self.environment.Q_table_updates[time_counter][0][0]
            self.environment.sort_update_q_table(prev_state, self.sorting_algorithm_name)

        # delete this changes...
        self.environment.Q_table_updates.pop(time_counter)
        return reward, state, actions, utilization
