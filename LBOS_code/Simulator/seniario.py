import numpy as np


class Senirio:
    def __init__(self):
        self.servers_num = 0
        self.users_num = 0

    def generate(self):
        self.servers_num = np.random.randint(1, 10)
        if self.servers_num < 5:
            self.users_num = np.random.randint(1, 15)
        else:
            self.users_num = np.random.randint(15, 30)