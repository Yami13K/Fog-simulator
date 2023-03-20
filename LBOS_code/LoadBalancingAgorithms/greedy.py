import numpy as np
import copy


class Greedy:

    def __init__(self, tp):
        self.number_assigned_tasks = 12  # min with the buffer length.
        self.tp = tp

    def __call__(self, servers, tasks_queue, time_counter, seed):
        if self.tp == 'cpu':
            return self.greedy_selection(servers, tasks_queue, time_counter, seed)
        if self.tp == 'reliability':
            return self.greedy_selection_reliability(servers, tasks_queue, time_counter, seed)

    def greedy_selection(self, servers, tasks_queue, time_counter, seed):
        selected_servers = [-1] * len(tasks_queue)
        servers_snapshot = copy.deepcopy(servers)
        copy_tasks = copy.deepcopy(tasks_queue)
        cpus = []
        for server in servers_snapshot:
            cpu, _ = server.utilization_and_ram()
            cpus.append(cpu)

        for idx, task in enumerate(copy_tasks):
            mn_cpu = min(cpus)
            server_id = cpus.index(mn_cpu)

            if servers_snapshot[server_id].able_to_receive():
                task.current_server_id = servers_snapshot[server_id].get_id
                selected_servers[idx] = server_id
                servers_snapshot[server_id].receive_task(task)
                servers_snapshot[server_id].execute(time_counter, [], seed)
                cpus[server_id], _ = servers_snapshot[server_id].utilization_and_ram()

            capable = (sum([s.able_to_receive() for s in servers_snapshot])) > 0
            if not capable:
                break

        return selected_servers, 0, 0, 0, 0

    def greedy_selection_reliability(self, servers, tasks_queue, time_counter, seed):
        selected_servers = [-1] * len(tasks_queue)
        servers_snapshot = copy.deepcopy(servers)
        copy_tasks = copy.deepcopy(tasks_queue)
        bps = []
        for server in servers_snapshot:
            bp = server.battery_power()
            bps.append(bp)

        for idx, task in enumerate(copy_tasks):
            mx_bp = max(bps)
            server_id = bps.index(mx_bp)

            if servers_snapshot[server_id].able_to_receive():
                task.current_server_id = servers_snapshot[server_id].get_id
                selected_servers[idx] = server_id
                servers_snapshot[server_id].receive_task(task)
                servers_snapshot[server_id].execute(time_counter, [], seed)
                bps[server_id] = servers_snapshot[server_id].battery_power()

            capable = (sum([s.able_to_receive() for s in servers_snapshot])) > 0
            if not capable:
                break

        return selected_servers, 0, 0, 0, 0
