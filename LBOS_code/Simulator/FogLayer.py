import numpy as np
from Simulator import Server


class FogLayer:

    def __init__(self, servers_num, scheduler, bandwidth_fog_layer, seed, scenario_logger, system_state):
        self.servers_num = servers_num
        self.system_state = system_state
        self.bandwidth_fog_layer = bandwidth_fog_layer
        self.scheduler = scheduler
        self.numberOfFiles = 1000
        self.filesIds = np.array(range(self.numberOfFiles)).tolist()
        if system_state == 'generate scenarios':
            self.file_sizes = seed.normal(0.7 * (8 * 10 ** 6), 0.2 * (8 * 10 ** 6), self.numberOfFiles).tolist()
            scenario_logger.append(('file_sizes', self.file_sizes))
            # [bit/sec], bandwidth
        else:
            self.file_sizes = scenario_logger.pop(0)[1]

        self.servers = [Server.Server(i, bandwidth_fog_layer, self.file_sizes, seed,
                                      scenario_logger, system_state) for i in range(self.servers_num)]

    def receive_tasks(self, tasks):
        for task in tasks:
            task.status = 'waiting in fog Buffer'
            self.scheduler.tasks_buffer.append(task)

    def schedule(self, task_logger, time_counter):
        selected_servers, reward, next_state, actions, utilization = self.scheduler(self.servers, time_counter)
        leaving_tasks = []
        for task_num, server_idx in enumerate(selected_servers):
            if server_idx != -1:
                self.servers[server_idx].receive_task(self.scheduler.tasks_buffer[task_num])
                leaving_tasks.append(task_num)

        leaving_tasks.sort(reverse=True)
        for task_num in leaving_tasks:
            self.scheduler.tasks_buffer.pop(task_num)

        task_logger.task_status['waiting in fog Buffer'].append(len(self.scheduler.tasks_buffer))
        return reward, next_state, actions, utilization

    def execute(self, time_counter, task_logger, performance_logger, scenario_logger, seed):
        task_logger.init_stat()  # initiate the dict.
        performance_logger.number_failed_devices.append(0)

        done_tasks = []
        for server in self.servers:
            server.update_status(time_counter, task_logger)
            server.execute(time_counter, scenario_logger, seed, self.system_state, task_logger, performance_logger)
            server.check_returning(time_counter, done_tasks)

        task_logger.task_status['done'].append(len(done_tasks))
        performance_logger.calculate_average_delay(done_tasks)
        performance_logger.over_all_average_ec()
        return done_tasks

    def number_tasks(self):
        return sum([s.number_tasks() for s in self.servers])

    def are_servers_capable(self):
        return (sum([s.able_to_receive() for s in self.servers])) > 0

    def get_utilization(self):
        res = []
        for server in self.servers:
            u, _ = server.utilization_and_ram()
            res.append(u)
        return res
