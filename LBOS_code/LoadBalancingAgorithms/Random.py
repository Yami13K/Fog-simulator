import numpy as np
import copy


class Random:
    def __init__(self):
        self.number_assigned_tasks = 12  # min with the buffer length.

    def __call__(self, servers, tasks_queue, time_counter, seed):
        return self.random_selection(servers, tasks_queue, time_counter, seed)

    def random_selection(self, servers, tasks_queue, time_counter, seed):
        selected_servers = [-1] * len(tasks_queue)
        servers_snapshot = copy.deepcopy(servers)
        copy_tasks = copy.deepcopy(tasks_queue)

        for idx, task in enumerate(copy_tasks):
            server_idx = seed.choice(len(servers_snapshot))
            if servers_snapshot[server_idx].able_to_receive():
                task.current_server_id = servers_snapshot[server_idx].get_id
                selected_servers[idx] = server_idx
                servers_snapshot[server_idx].receive_task(task)
                servers_snapshot[server_idx].execute(time_counter, [], seed)

            capable = (sum([s.able_to_receive() for s in servers_snapshot])) > 0
            if not capable:
                break

        return selected_servers, 0, 0, 0, 0
