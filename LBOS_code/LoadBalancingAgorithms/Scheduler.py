from LoadBalancingAgorithms import Random, Migrator, greedy
from LoadBalancingAgorithms.Reinforcement_Learning import RAA, RL, State
from operator import attrgetter
import copy
import numpy as np
import CalcTimeModel


class Scheduler:
    def __init__(self, algorithm_name, migration_method, servers_num, reward_type, sorting_algorithm, greedy_type,  seed, system_state):
        self.tasks_buffer = []
        self.seed = seed
        self.system_state = system_state
        self.algorithm_name = algorithm_name
        self.space_size = servers_num
        self.reward_type = reward_type
        self.sorting_algorithm_name = sorting_algorithm
        self.greedy_type = greedy_type
        self.algorithm = self.choose_algorithm()
        self.state_obj = State.State(0)
        self.migration_method = migration_method
        self.migrator = Migrator.Migrator()

    def __len__(self):
        return len(self.tasks_buffer)

    def choose_algorithm(self):
        if self.algorithm_name == 'Random':
            algorithm = Random.Random()
        elif self.algorithm_name == 'RAA':
            raise ValueError('Not working currently')
            # algorithm = RAA.RAA(self.space_size)
        elif self.algorithm_name == 'RL':
            algorithm = RL.RL(self.space_size, 'schedule', self.reward_type, self.sorting_algorithm_name,
                              delay_period=5,
                              decay=0.993)
        elif self.algorithm_name == 'greedy':
            algorithm = greedy.Greedy(self.greedy_type)
        else:
            raise ValueError('algorithm does not exist')
        return algorithm

    def schedule(self, org_servers_snapshot, time_counter):
        servers_snapshot = copy.deepcopy(org_servers_snapshot)
        tasks_copy_buffer = copy.deepcopy(self.tasks_buffer)

        # append id's of selected servers.
        selected_servers, reward, next_state, actions, utilization = self.algorithm(servers_snapshot, tasks_copy_buffer[
                                                                                                      :self.algorithm.
                                                                                    number_assigned_tasks], time_counter,
                                                                                    self.seed)

        return selected_servers, reward, next_state, actions, utilization

    @staticmethod
    def perform_migration(servers_to_migrate_from, servers, bandwidth_fog_layer, time_counter, task_logger=None):
        for pair in servers_to_migrate_from:
            server_id, dv_id = pair[0], pair[1]
            servers[server_id].devices[dv_id].task_in_execution.migration_cost += \
                CalcTimeModel.migrating_cost(servers[server_id].devices[dv_id].task_in_execution.data_size,
                                             bandwidth_fog_layer)
            servers[server_id].devices[dv_id].task_in_execution.change_mode('migrating', servers
                        [server_id].devices[dv_id].task_in_execution.migration_cost + time_counter)

            servers[server_id].migrating_tasks.append(servers[server_id].devices[dv_id].task_in_execution)
            servers[server_id].devices[dv_id].free_task()
            servers[server_id].free_devices.append(servers[server_id].devices[dv_id])
            if task_logger is not None:
                task_logger.task_status['migrating'][-1] += 1

    def migration(self, servers, bandwidth_fog_layer, time_counter, task_logger, migrate):
        reward, next_state, actions, utilization = 0, 0, 0, 0
        task_logger.task_status['migrating'].append(0)
        if migrate:
            self.tasks_buffer.sort(key=attrgetter('moment_generation'))
            servers_to_migrate_from, reward, next_state, actions, utilization = self.migrator(self.migration_method,
                            self.space_size, self.state_obj, servers, bandwidth_fog_layer, time_counter, self.seed)
            self.perform_migration(servers_to_migrate_from, servers, bandwidth_fog_layer, time_counter, task_logger)

        self.check_migrating(servers, time_counter)
        return reward, next_state, actions, utilization

    def check_migrating(self, servers,  time_counter):
        for server in servers:
            leaving_server = []
            for task_idx, task in enumerate(server.migrating_tasks):
                if task.changing_status_time <= time_counter:
                    task.status = 'waiting in fog Buffer'
                    self.tasks_buffer.append(task)
                    leaving_server.append(task_idx)

            leaving_server.sort(reverse=True)
            for task_num in leaving_server:
                server.migrating_tasks.pop(task_num)

    def __call__(self, org_servers_snapshot, time_counter):
        selected_servers = self.schedule(org_servers_snapshot, time_counter)
        return selected_servers
