import numpy as np


class State:
    def __init__(self, action_space_size_allocation, alpha=0.07, server_cpu_usage_threshold=0.1):
        self.alpha = alpha  # 0.07
        self.server_cpu_usage_threshold = server_cpu_usage_threshold  # 0.10

        self.action_space_size_allocation = action_space_size_allocation
        self.observation_space_size_allocation = 3 ** self.action_space_size_allocation
        self.sct_table = np.zeros((self.action_space_size_allocation,  8))
        self.state_counter = 0
        self.state_dict = {}
        self.queue_threshold = 0.5

    def abstract_server_status(self, server):
        server_cpu_usage, server_ram_usage = server.utilization_and_ram()
        utilization_percent = server_cpu_usage/100
        queue_len_percent = len(server.get_queue)/server.queue_max_length

        if queue_len_percent == 0 and utilization_percent <= 0.3:
            return 0
        elif 0 <= queue_len_percent < self.queue_threshold:
            return 1
        else:
            return 2

    def server_status(self, index, server):
        utilization_percent = self.sct_table[index, 2]/100
        queue_len_percent = len(server.get_queue)/server.queue_max_length

        if queue_len_percent == 0 and utilization_percent <= 0.3:
            return 0

        elif 0 <= queue_len_percent < self.queue_threshold and utilization_percent <= 0.8:
            return 1
        else:
            return 2

    # calculate adaptive weight of a server.
    def calculate_server_aw(self, server_cache, server_cpu_usage, server_ram_usage):
        return self.alpha * (server_ram_usage*server_cache / max(1, server_cpu_usage))

    # calculate the threshold adaptive weighting (threshold loading)
    def calculate_taw(self, list_aw, list_cpu_usage, servers):
        taw = 0
        threshold = sum(list_cpu_usage) * self.server_cpu_usage_threshold

        for idx, aw in enumerate(list_aw):
            if servers[idx].utilization_and_ram()[0] <= threshold:
                taw = max(taw, aw)
        return taw

    def get_current_state(self, servers):
        current_state_for_allocation = []

        if sum(self.sct_table[:, 2]) != 0:
            self.sct_table[:, 7] = self.sct_table[:, 2]  # as the old utilization.

        for index, server in enumerate(servers):
            server_id = server.get_id
            server_cache = server.cache_size
            server_cpu_usage, server_ram_usage = server.utilization_and_ram()
            queue_occupation = server.queue_occupation()
            # server_aw = self.calculate_server_aw(server_cache, server_cpu_usage, server_ram_usage)
            self.sct_table[index, 0] = server_id
            self.sct_table[index, 1] = server_cache
            self.sct_table[index, 2] = server_cpu_usage
            self.sct_table[index, 3] = queue_occupation
            self.sct_table[index, 4] = self.server_status(index, server)
            current_state_for_allocation.append(self.sct_table[index, 4])

        # NOT SURE....
        # server_aaw = np.average(self.sct_table, axis=0)[3]
        # server_taw = self.calculate_taw(self.sct_tabl
        # e[:, 3], self.sct_table[:, 2], servers)

        # for index, server in enumerate(servers):
        #    self.sct_table[index, 4] = server_taw
        #    self.sct_table[index, 5] = server_aaw
        #    self.sct_table[index, 6] = self.server_status(index)
            #
        # 2 is the overload state, if it existed --> its invalid space.
        return self.encode_state(current_state_for_allocation)

    def encode_state(self, state):
        state = tuple(state)
        if state in self.state_dict.keys():
            return state, self.state_dict[state]

        self.state_dict[state] = self.state_counter
        self.state_counter += 1
        return state, self.state_dict[state]
