import numpy as np


class Task:
    def __init__(self, user_id, task_type,  avg_data_size, avg_comp_demand, moment_generation, seed, scenario_logger,
                 files_ids, system_state):

        # information:
        self.user_id = user_id
        self.current_server_id = -1
        self.system_state = system_state
        self.idx_queue = -1
        # task components:
        if system_state == 'generate scenarios':
            self.__dataSize = seed.exponential(avg_data_size)  # [bit] (how much RAM)
            scenario_logger.append(('task_data_size', self.__dataSize))

            self.compute_demand = seed.exponential(avg_comp_demand)  # [cycles/sec]
            scenario_logger.append(('task_compute_demand', self.compute_demand))

            random_start_limit = seed.randint(5, 12)
            scenario_logger.append(('random_start_limit', random_start_limit))

        else:
            self.__dataSize = scenario_logger.pop(0)[1]
            self.compute_demand = scenario_logger.pop(0)[1]
            random_start_limit = scenario_logger.pop(0)[1]

        self.current_processing_cpu = 0
        self.needed_files = []
        self.files = {}
        self.generate_needed_files(seed, scenario_logger, files_ids)
        self.type = task_type
        self.moment_generation = moment_generation
        self.logger = []  # event --> time interval.
        self.start_limit = self.moment_generation + random_start_limit
        # current status of task:

        self.serving_time = 0
        self.processing_cost = 0
        self.grab_files_cost = 0
        self.return_cost = 0
        self.migration_cost = 0
        self.waiting_time = 0
        self.all_cost = 0
        self.completion_percentage = 0
        self.fetching_percentage = 0
        self.expected_fetching_time = 0
        self.required_data_size = 0

        # this variable is to tell us in what stage the task is (waiting, transferring , executing, Blocked, failed)x
        self.status = 'generated'
        self.changing_status_time = 0

        # execution details.

    @property
    def data_size(self):
        return self.__dataSize

    def generate_needed_files(self, seed, scenario_logger, files_ids):
        for i in range(10):  # 10%, 20% ... 100%
            if self.system_state == 'generate scenarios':
                x = seed.uniform(0.1, 1)
                scenario_logger.append(('file_needed_prop', x))
            else:
                x = scenario_logger.pop(0)[1]
            if x < 0.2:
                if self.system_state == 'generate scenarios':
                    self.files[i * 10] = seed.choice(files_ids)
                    scenario_logger.append(('chosen_file', self.files[i*10]))
                else:
                    self.files[i*10] = scenario_logger.pop(0)[1]

    def assign_server_id(self, server_id):
        self.current_server_id = server_id

    def calc_all_cost(self):
        return self.serving_time + self.return_cost + self.waiting_time

    def calc_wait_time(self, time_counter):
        return (time_counter - self.moment_generation) - (self.serving_time + np.ceil(self.migration_cost) + np.ceil(
            self.return_cost) + np.ceil(self.grab_files_cost))

    def insert_log(self, event, st, en=-1):

        if (en != -1 and st == -1) or (len(self.logger) > 0 and self.logger[-1][0] == event and self.logger[-1][1][1] !=
                                       -1):   # we have an unclosed interval we want to close.
            log = self.logger[-1]
            self.logger.pop()
            self.logger.append((log[0], (log[1][0], en)))

        else:
            self.logger.append((event, (st, en)))

    def change_mode(self, new_mode, changing_time):
        self.changing_status_time = changing_time
        self.status = new_mode

    def get_last_state(self):
        return self.logger[len(self.logger)-1][0]

    def task_weight(self):
        return (self.data_size * self.compute_demand) / (self.completion_percentage/self.serving_time * 100)
