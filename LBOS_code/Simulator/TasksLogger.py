class TasksLogger:
    def __init__(self):
        self.task_status = {}

        self.task_status['generated'] = []
        self.task_status['waiting in fog Buffer'] = []
        self.task_status['waiting in server'] = []
        self.task_status['executing'] = []
        self.task_status['returning'] = []
        self.task_status['done'] = []
        self.task_status['failing'] = []
        self.task_status['blocked'] = []
        self.task_status['migrating'] = []

    def init_stat(self):
        self.task_status['waiting in server'].append(0)
        self.task_status['executing'].append(0)
        self.task_status['failing'].append(0)
        self.task_status['blocked'].append(0)
        self.task_status['returning'].append(0)
