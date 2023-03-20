from Simulator import User


class UsersManager:
    def __init__(self, users_num, seed, scenario_logger, files_ids, system_state):
        self.users_num = users_num
        self.system_state = system_state
        self.users = self.generate_users(scenario_logger, seed, files_ids)

    def generate_users(self, scenario_logger, seed, files_ids):

        users = [User.User(i, seed, scenario_logger, files_ids, self.system_state) for i in range(self.users_num)]
        return users

    def send_tasks(self, time_counter, task_logger, performance_logger, scenario_logger, seed):
        new_tasks = []
        for user in self.users:
            if user.next_time_sending_task <= time_counter:
                new_tasks.append(user.send_task(time_counter, scenario_logger, seed))
        task_logger.task_status['generated'].append(len(new_tasks))
        return new_tasks
