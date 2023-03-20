import numpy as np
from Simulator import Task


class User:
    def __init__(self, enum, seed, scenario_logger, files_ids, system_state):
        self.__id = enum
        self.system_state = system_state
        self.mu = 8
        self.sigma = 2
        if system_state == 'generate scenarios':

            self.taskSendingRate = max(0, seed.normal(self.mu, self.sigma))
            scenario_logger.append(('taskSendingRate', self.taskSendingRate))
            self.__nextTimeOfSendingTask = seed.poisson(lam=self.taskSendingRate)
            scenario_logger.append(('nextTimeOfSendingTask', self.__nextTimeOfSendingTask))
            self.__average_data_size = seed.uniform(low=200*1024, high=500*1024)
            scenario_logger.append(('average_data_size', self.__average_data_size))
            self.__average_comp_demand = seed.uniform(low=1000000000, high=16000000000)
            scenario_logger.append(('average_comp_demand', self.__average_comp_demand))

        else:
            self.taskSendingRate = max(0, scenario_logger.pop(0)[1])
            self.__nextTimeOfSendingTask = max(1, scenario_logger.pop(0)[1])
            self.__average_data_size = scenario_logger.pop(0)[1]
            self.__average_comp_demand = scenario_logger.pop(0)[1]

        self.files_ids = files_ids

    @property
    def next_time_sending_task(self):
        return self.__nextTimeOfSendingTask

    @property
    def user_id(self):
        return self.__id

    def update_sending_rate(self, mu, sigma, scenario_logger, seed):
        self.mu = min(mu, self.mu)
        self.sigma = min(sigma, self.sigma)
        if self.system_state == 'generate scenarios':
            random_taskSendingRate = seed.normal(self.mu, self.sigma)
            scenario_logger.append(('random_taskSendingRate', random_taskSendingRate))
        else:
            random_taskSendingRate = scenario_logger.pop(0)[1]
            scenario_logger.append(('random_taskSendingRate', random_taskSendingRate))

        self.taskSendingRate = max(0, random_taskSendingRate)
        #print('mu', self.mu , 'sigma', self.sigma, 'random_taskSendingRate', random_taskSendingRate)


    def change_next_sending_time(self, time_counter, scenario_logger, seed):
        if self.system_state == 'generate scenarios':
            lam_nextTimeOfSendingTask = seed.poisson(lam=self.taskSendingRate)
            scenario_logger.append(('lam_nextTimeOfSendingTask', lam_nextTimeOfSendingTask))

        else:
            lam_nextTimeOfSendingTask = scenario_logger.pop(0)[1]

        self.__nextTimeOfSendingTask = time_counter + max(1, lam_nextTimeOfSendingTask)

    '''
    generate a task and sending it, then update the next time this user will send another task.
    Assuming every user sends one task every unit of time (second).
    '''
    def send_task(self, time_counter, scenario_logger, seed,  mu=1e10, sigma=1e10):

        if self.system_state == 'generate scenarios':
            task_type = seed.randint(1, 4)  # 1 is real-time , 2 is important, 3 is time-tolerance.
            scenario_logger.append(('task_type', task_type))

        else:
            task_type = scenario_logger.pop(0)[1]

        t = Task.Task(self.__id, task_type, self.__average_data_size, self.__average_comp_demand,
                  time_counter, seed, scenario_logger, self.files_ids, self.system_state)

        # t.insert_log('waiting', time_counter)

        self.update_sending_rate(mu, sigma, scenario_logger, seed)
        self.change_next_sending_time(time_counter, scenario_logger, seed)
        return t
