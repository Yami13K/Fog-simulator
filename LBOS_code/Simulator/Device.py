import numpy as np
import copy
from Simulator import CacheMemory
import CalcTimeModel


class Device:
    def __init__(self, enum, cache_size, file_sizes, bandwidth_fog_layer, seed, scenario_logger, system_state):
        self.id = enum
        self.system_state = system_state
        if system_state == 'generate scenarios':
            self.cpu_rate = seed.normal(4 * (2 ** 30), (2 ** 30))  # #  # 2G per sec.   ##
            scenario_logger.append(('cpu_rate', self.cpu_rate))

            self.ram_size = seed.uniform(20 * (2 ** 20), 50 * (2 ** 20))
            scenario_logger.append(('ram_size', self.ram_size))

            self.batteryPower = min(1, max(seed.normal(0.7, 0.1), 0))
            scenario_logger.append(('batteryPower', self.batteryPower))

        else:
            self.cpu_rate = scenario_logger.pop(0)[1]
            self.ram_size = scenario_logger.pop(0)[1]
            self.batteryPower = min(1, max(scenario_logger.pop(0)[1], 0))

        self.busy = False
        self.task_in_execution = None

        self.used_ram = 0
        self.old_util = 0

        # energy and operating parameters.

        self.is_operating = True
        self.energy_differ = 0
        self.__effective_switched = 5 * 1e-27

        # cache:
        self.cache_size = cache_size
        self.files_sizes = file_sizes
        self.filesIds = np.array(range(len(self.files_sizes))).tolist()
        self.bandwidth_fog_layer = bandwidth_fog_layer
        self.cache_memory = CacheMemory.CacheMemory(cache_size, file_sizes)

    def get_files_from_cache(self, needed_files, time_counter):
        data_size = 0
        for file in needed_files:
            existed = self.cache_memory.add_file_to_memory(file, self.files_sizes[file], time_counter)
            data_size += (not existed) * self.files_sizes[file]
        # for now we will take the number of memory-grabbed files  * (1 M for each)
        return data_size

    def get_file(self, time_counter, files):
        """
        :return:
        its updates the task info.
        1- pick a random file.
        2- add it to the files in the task.
        3- calc the time to fetch the data, start fetching.
        4- change the logs.
        """
        self.task_in_execution.expected_fetching_time = 0
        for file in files:
            self.task_in_execution.needed_files.append(file)
            required_data_size = self.get_files_from_cache([file], time_counter)
            grab_files_time = CalcTimeModel.grab_files_cost(required_data_size, self.bandwidth_fog_layer)

            self.task_in_execution.grab_files_cost += grab_files_time
            self.task_in_execution.expected_fetching_time += grab_files_time
            self.task_in_execution.required_data_size += required_data_size

    def execute(self, task):
        if self.used_ram > self.ram_size:
            raise ValueError('SMALL RAM.')

        self.task_in_execution = task
        self.busy = True
        self.task_in_execution.current_processing_cpu = self.cpu_rate

    def free_task(self):
        self.task_in_execution = None
        self.used_ram = 0
        self.busy = False

    def update_on_going(self, time_counter, task_logger):

        if self.task_in_execution is not None and self.is_operating:
            if self.task_in_execution.status == 'blocked':
                self.task_in_execution.fetching_percentage += 1
                task_logger.task_status['blocked'][-1] += 1

            else:
                current_execution_percentage = (self.task_in_execution.completion_percentage/self.task_in_execution.
                                                serving_time) * 100
                if len(self.task_in_execution.files.keys()) > 0 and list(self.task_in_execution.files.keys())[0] < \
                        current_execution_percentage and self.task_in_execution.status == 'executing':
                    files = []
                    while len(self.task_in_execution.files.keys()) > 0 and list(self.task_in_execution.files.keys())[0] \
                            < current_execution_percentage:
                        files.append(self.task_in_execution.files.pop(list(self.task_in_execution.files.keys())[0]))

                    self.get_file(time_counter, files)
                    if self.task_in_execution.expected_fetching_time != 0:
                        self.task_in_execution.status = 'blocked'
                        self.task_in_execution.fetching_percentage += 1
                        task_logger.task_status['blocked'][-1] += 1

                if self.task_in_execution.status == 'executing':
                    self.task_in_execution.completion_percentage += 1
                    self.energy_consumption()

                    task_logger.task_status['executing'][-1] += 1

        elif self.task_in_execution is not None and not self.is_operating:  # failure case:
            task_logger.task_status['failing'][-1] += 1
            self.energy_differ = 0

    def update_state(self, time_counter):
        returned_task = None
        if self.task_in_execution is not None and self.task_in_execution.status == 'blocked' and \
                self.task_in_execution.fetching_percentage == self.task_in_execution.expected_fetching_time:
            self.task_in_execution.status = 'executing'
            self.task_in_execution.fetching_percentage = 0

        elif self.task_in_execution is not None and self.task_in_execution.\
                completion_percentage == self.task_in_execution.serving_time:
            self.busy = False
            self.used_ram = 0
            returned_task = copy.deepcopy(self.task_in_execution)
            self.task_in_execution = None

        return (not self.busy), returned_task

    def utilization(self):
        return (0, 0) if self.task_in_execution is None else (min(self.task_in_execution.compute_demand, self.cpu_rate),
                                                              self.task_in_execution.data_size)

    def energy_consumption(self):
        """
        :return: calculates the new value of battery power and update the is-operating value.
        """

        self.energy_differ = self.cpu_rate * self.__effective_switched * \
                             (self.task_in_execution.compute_demand / self.task_in_execution.serving_time)
        self.batteryPower = max(self.batteryPower - self.energy_differ, 0)
        self.is_operating = (self.batteryPower > 0)

    def charge_energy(self, scenario_logger, seed, system_state):
        if system_state == 'generate scenarios':
            charge_prop = seed.uniform(0, 1)
            charge_value = seed.uniform(0, 0.1)

            scenario_logger.append(('charge_prop', charge_prop))
            scenario_logger.append(('charge_value', charge_value))
        else:
            charge_prop = scenario_logger.pop(0)[1]
            charge_value = scenario_logger.pop(0)[1]

        if charge_prop > 0.5:  # charge:
            self.batteryPower = min(self.batteryPower + charge_value, 1)
            self.is_operating = (self.batteryPower > 0)

            # charge a random number between 0 and 20 %.

    def failing_prop(self, scenario_logger, seed, system_state):
        if system_state == 'generate scenarios':
            fail_probability = seed.uniform(0, 1)
            scenario_logger.append(('fail_probability', fail_probability))

        else:
            fail_probability = scenario_logger.pop(0)[1]

        if fail_probability > 0.8:
            self.batteryPower = 0
            self.is_operating = False
