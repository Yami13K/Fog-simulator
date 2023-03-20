class ScenarioGenerator:
    def __init__(self):
        """
        all the variables used in the generate function should be defined here with initial value:
        example:
        self.number_servers = 0
        """
    def generate(self):
        """
        parameters:
        1- number of servers: a number between 2 and 8, follows the uniform distribution
        2- number of users: between 5 and 30
            a number of servers between (2 and 4) shouldn't have more than 15 users.
            a number of servers between (4 and 6) shouldn't have more than 20 users.
            a number of servers between (6 and 8) shouldn't have more than 30 users.
        3- bandwidth: random number between 1 and 8 multiplied with 1e6
        4- time: number between 100 and 1000 second. use --> random.randint()
        5- task sending rate: normal distribution (mu, sigma) sigma = 0.5 and mu is random between 1 and 5.
        6- task next Time Of Sending Task = number follows the poisson distribution where lamda = task sending rate
        7- number of devices: random between 1 and 5 for every server (list it size is the servers number)
        8- schedule_type: random choice from this list ['RL', 'Random']
        9- reward_type:  random choice from this list ['non-linear-MO', 'linear-MO' , 'SO']
        10- sorting type: random choice from this list ['TLO', 'NDS']
        11- average cop rate: normal distribution with mu = random number 1--> 5 * (2 ** 30)
        and sigma = random number 0.1 --> 0.5 * (2 ** 30)
        ***** average_data_size = np.random.uniform(low=200*1024, high=500*1024)
        12- use the average_data_size to generate a variable called task data size with exponential distribution

        :return:
        an object with all the values generated.
        """
