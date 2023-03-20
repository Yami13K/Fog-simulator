import numpy as np
from Simulator import Device
from operator import attrgetter
import copy
import bisect
import CalcTimeModel


class Server:
    def __init__(self, enum, bandwidth_fog_layer, file_sizes, seed, scenario_logger, system_state):

        # main components:
        self.bandwidth_fog_layer = bandwidth_fog_layer
        self.__id = enum
        self.system_state = system_state
        if system_state == 'generate scenarios':
            self.number_devices = seed.randint(5, 20)
            scenario_logger.append(('number_devices', self.number_devices))
        else:
            self.number_devices = scenario_logger.pop(0)[1]

        self.busy = False
        # lists for tasks types:
        self.__tasks_queue = []
        self.returning_tasks = []
        self.migrating_tasks = []
        self.executed_tasks_per_second = []

        if system_state == 'generate scenarios':
            self.queue_max_length = seed.randint(5, 10)
            self.cache_size = seed.randint(5, 10) * np.average(file_sizes)
            scenario_logger.append(('queue_size', self.queue_max_length ))
            scenario_logger.append(('cache_size', self.cache_size))
        else:
            self.queue_max_length = scenario_logger.pop(0)[1]
            self.cache_size = scenario_logger.pop(0)[1]

        self.task_in_execution = None
        self.devices = [Device.Device(i, self.cache_size, file_sizes, bandwidth_fog_layer, seed, scenario_logger,
                                      system_state) for i in range(self.number_devices)]
        self.free_devices = copy.deepcopy(self.devices)
        self.failed_devices = 0
        self.server_all_cpu = self.server_cpu()
        self.server_all_ram = self.server_ram()
        self.current_cpu = 0

    @property
    def get_id(self):
        return self.__id

    @property
    def get_queue(self):
        return self.__tasks_queue

    """
    functions:
    """

    def able_to_receive(self):
        return len(self.__tasks_queue) < self.queue_max_length

    def server_cpu(self):
        return sum([dv.cpu_rate for dv in self.devices])

    def server_ram(self):
        return sum([dv.ram_size for dv in self.devices])

    def receive_task(self, task):
        task.status = 'waiting in server'
        self.__tasks_queue.append(task)

    def mid_heavy_task(self):
        pw = [(dv.task_in_execution.task_weight(), dv.id) if dv.busy and dv.task_in_execution.completion_percentage\
                        < dv.task_in_execution.serving_time and dv.task_in_execution.status != 'blocked' else (0, -1)
              for dv in self.devices]

        pw.sort(reverse=True)
        return pw[int(len(pw)/2)][1]

    def get_best_device(self, task_cpu):

        #self.free_devices.sort(key=attrgetter('cpu_rate'))
        # cpu_values = [o.cpu_rate if self.devices[o.id].is_operating else -1e8 for o in self.free_devices]
        # low = 0
        # if cpu_values[0] == -1e8:
        #     low = bisect.bisect_right(cpu_values, -1e8, lo=0, hi=len(cpu_values))
        #
        # dv_idx = min(bisect.bisect_left(cpu_values, task_cpu, lo=low, hi=len(cpu_values)), len(self.free_devices)-1)
        chosen_device_id = self.free_devices[0].id
        self.free_devices.pop(0)
        #cpu_values.pop(dv_idx)
        ok = False
        if len(self.free_devices) > 0:# and cpu_values[-1] == -1e8:
            ok = True
        return chosen_device_id, ok

    def execute(self, time_counter, scenario_logger, seed, system_state=None,  task_logger=None, performance_logger=None):

        leaving_tasks = []
        # if all the free devices have failed.
        ok = sum([1 if not self.devices[o.id].is_operating else 0 for o in self.free_devices]) == len(self.free_devices)

        for idx, task in enumerate(self.__tasks_queue):

            if len(self.free_devices) == 0 or ok:  # no more free devices to accept tasks,
                # or they are in a failure mode.
                break

            # delete the part of the task that was already executed.
            task.compute_demand -= ((task.completion_percentage/CalcTimeModel.scale) * task.current_processing_cpu)

            task.completion_percentage = 0
            dv_idx, ok = self.get_best_device(task.compute_demand)

            task.serving_time = CalcTimeModel.serving_cost(task.compute_demand, self.devices[dv_idx].cpu_rate)
            task.processing_cost += task.serving_time
            task.change_mode('executing', task.serving_time + time_counter)
            self.devices[dv_idx].execute(task)

            leaving_tasks.append(idx)

        leaving_tasks.sort(reverse=True)
        for task_idx in leaving_tasks:
            self.__tasks_queue.pop(task_idx)

        # the system is actually executing, not just checking in the scheduler.
        if task_logger is not None:
            task_logger.task_status['waiting in server'][-1] += len(self.__tasks_queue)

            for idx, dv in enumerate(self.devices):
                dv.update_on_going(time_counter, task_logger)
                dv.charge_energy(scenario_logger, seed, system_state)
                dv.failing_prop(scenario_logger, seed, system_state)
                performance_logger.number_failed_devices[-1] += (not dv.is_operating)

            performance_logger.calculate_average_ec(self.devices)

    def check_returning(self, time_counter, done_tasks):
        leaving_server = []
        for task_idx, task in enumerate(self.returning_tasks):
            if task.changing_status_time <= time_counter:
                task.change_mode('done', time_counter)
                task.waiting_time = task.calc_wait_time(time_counter)
                done_tasks.append(task)
                leaving_server.append(task_idx)

        leaving_server.sort(reverse=True)
        for task_num in leaving_server:
            self.returning_tasks.pop(task_num)

    def utilization_and_ram(self):
        server_used_cpu, server_used_ram = 0, 0
        for dv in self.devices:
            cpu, ram = dv.utilization()

            server_used_cpu += cpu
            server_used_ram += ram

        return (server_used_cpu/self.server_all_cpu * 100), self.server_all_ram

    def power(self):
        return sum([dv.cpu_rate for dv in self.devices])

    def queue_occupation(self):
        return len(self.get_queue)/self.queue_max_length * 100

    def update_status(self, time_counter, task_logger):
        for dv in self.devices:
            free, returned_task = dv.update_state(time_counter)
            if free and returned_task is not None:
                self.free_devices.append(dv)
                returned_task.return_cost = CalcTimeModel.return_cost(returned_task.data_size, self.bandwidth_fog_layer)
                returned_task.change_mode('returning', returned_task.return_cost + time_counter)
                self.returning_tasks.append(returned_task)
                task_logger.task_status['returning'][-1] += 1

    def number_free_devices(self):
        return len(self.free_devices)

    def is_free(self):
        return len(self.free_devices) != 0

    def number_tasks(self):
        return len(self.returning_tasks) + len(self.migrating_tasks) + len(self.__tasks_queue) + (self.number_devices - len(self.free_devices))

    def number_tasks_in(self):
        return self.number_tasks() - len(self.returning_tasks)

    def load_calc(self):
        u, m = self.utilization_and_ram()
        return u

    def battery_power(self):
        return sum([d.batteryPower for d in self.devices])
