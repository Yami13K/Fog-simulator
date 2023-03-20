import numpy as np
import copy
from LoadBalancingAgorithms.Reinforcement_Learning import RL, State, Reward


class Migrator:

    def __init__(self):
        self.RL_agent = None

    def initiate_migrations(self, state_obj, servers, seed):
        """
        :param state_obj:
        :param servers: a reference to the original servers to migrate tasks from overloaded tasks.
        :return: the updated servers.
        """
        servers_to_migrate_from = []
        for server in servers:
            if state_obj.abstract_server_status(server) == 2:  # overloaded.
                dv = seed.choice(server.devices)
                cnt = 0
                while not dv.busy or dv.task_in_execution.completion_percentage \
                        >= dv.task_in_execution.serving_time or dv.task_in_execution.status == 'blocked':
                    cnt += 1
                    dv = seed.choice(server.devices)
                    if cnt > server.number_devices*3:
                        break
                if cnt > server.number_devices*3:
                    continue

                servers_to_migrate_from.append((server.get_id, dv.id))
        return servers_to_migrate_from, 0, 0, 0, 0

    def __call__(self, type_migration, space_size,  state_obj, servers, bandwidth_fog_layer, time_counter, seed):
        snapshot_servers = copy.deepcopy(servers)
        if type_migration == 'Random':
            return self.initiate_migrations(state_obj, snapshot_servers, seed)
        else:
            if self.RL_agent is None:
                self.RL_agent = RL.RL(space_size, 'migration', delay_period=5, decay=0.95)
            return self.RL_agent(snapshot_servers, [], time_counter, seed, bandwidth_fog_layer)
