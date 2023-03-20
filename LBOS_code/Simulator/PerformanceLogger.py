import numpy as np


class PerformanceLogger:
    def __init__(self, number_servers):
        self.servers_status = {}
        self.rewards = []
        self.average_rewards = []
        self.delay_measures = {}
        self.energy_consumption = []
        self.temp_ec = []
        self.number_failed_devices = []
        self.average_utilization = []

        for s in range(number_servers):
            name = 'server ' + str(s)
            self.servers_status[name] = []

        self.delay_measures['execute'] = []
        self.delay_measures['migration'] = []
        self.delay_measures['block'] = []
        self.delay_measures['wait'] = []

    @staticmethod
    def get_average(tasks, attr_name):
        av = np.average(list(map(lambda x: getattr(x, attr_name), tasks)))
        return av if not np.isnan(av) else 0

    def calculate_average_delay(self, tasks):
        self.delay_measures['execute'].append(self.get_average(tasks, 'serving_time'))
        self.delay_measures['migration'].append(self.get_average(tasks, 'migration_cost'))
        self.delay_measures['block'].append(self.get_average(tasks, 'grab_files_cost'))
        self.delay_measures['wait'].append(self.get_average(tasks, 'waiting_time'))

    # average energy consumption.
    def calculate_average_ec(self, devices):
        self.temp_ec.append(self.get_average(devices, 'energy_differ'))

    def over_all_average_ec(self):
        self.energy_consumption.append(np.average(self.temp_ec))
        self.temp_ec.clear()