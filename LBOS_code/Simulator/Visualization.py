import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
import numpy as np
from scipy.stats import hmean


class Visualization:
    def __init__(self):
        # self.ax = plt.subplot()
        self.max_show = 60
        self.grid = plt.GridSpec(2, 2, wspace=0.3, hspace=1)
        self.grid2 = plt.GridSpec(4, 1, wspace=0.3, hspace=1)

    def vis_reward(self, rewards, performance_logger, last, schedule_type, reward_type, sorting_algorithm):
        if reward_type == 'SO':
            self.vis_reward_convergence_SO(rewards, performance_logger, last, schedule_type, reward_type, sorting_algorithm)
        else:
            self.vis_reward_convergence_MO(rewards, performance_logger, last, schedule_type, reward_type, sorting_algorithm)

    def vis_average_reward(self, performance_logger, last, schedule_type, reward_type, sorting_algorithm):
        if reward_type == 'SO':
            self.vis_reward_convergence_episodes_average_SO(performance_logger, last, schedule_type, reward_type,
                                                            sorting_algorithm)
        else:
            self.vis_reward_convergence_episodes_average_MO(performance_logger, last, schedule_type, reward_type,
                                                            sorting_algorithm)

    def visualize_measures(self, performance_logger, fog_layer, schedule_type, migration_type, reward_type, last):
        plt.figure("system measures")
        ax = plt.subplot(self.grid2[0, 0])
        ax.clear()

        for key, value in performance_logger.delay_measures.items():
            plt.plot(value, label='number of ' + key)
        plt.legend(prop={'size': 10}, loc='upper right')

        plt.title('delay measures', fontsize=8, weight='bold')
        plt.xlabel('time [sec]', weight='bold')
        plt.ylabel('tasks number', weight='bold')
        plt.legend(prop={'size': 7, 'weight': 'bold'}, loc='upper left')
        ax.xaxis.label.set_size(7)
        ax.yaxis.label.set_size(7)

        #ln = np.arange(max(0, len(value) - self.max_show), len(value), 4)
        #plt.xticks(range(len(ln)), ln)
        #ax.xaxis.set_major_locator(mticker.MultipleLocator(4))

        ax = plt.subplot(self.grid2[1, 0])
        ax.clear()
        plt.plot(performance_logger.energy_consumption, label='energy consumption')

        plt.title('average energy consumption', fontsize=8, weight='bold')
        plt.xlabel('time [sec]', weight='bold')
        plt.ylabel('energy values', weight='bold')
        plt.legend(prop={'size': 7, 'weight': 'bold'}, loc='upper left')
        ax.xaxis.label.set_size(7)
        ax.yaxis.label.set_size(7)

        #ln = np.arange(max(0, len(performance_logger.energy_consumption) - self.max_show),
                     #  len(performance_logger.energy_consumption), 4)
        #plt.xticks(range(len(ln)), ln)
        #ax.xaxis.set_major_locator(mticker.MultipleLocator(4))

        ax = plt.subplot(self.grid2[2, 0])
        ax.clear()
        plt.plot(performance_logger.number_failed_devices, label='number of failed devices')

        plt.title('number of failed devices', fontsize=8, weight='bold')
        plt.xlabel('time [sec]', weight='bold')
        plt.ylabel('number of devices', weight='bold')
        plt.legend(prop={'size': 7, 'weight': 'bold'}, loc='upper left')
        ax.xaxis.label.set_size(7)
        ax.yaxis.label.set_size(7)

        #ln = np.arange(max(0, len(performance_logger.number_failed_devices) - self.max_show),
                       #len(performance_logger.number_failed_devices), 4)
        #plt.xticks(range(len(ln)), ln)
        #ax.xaxis.set_major_locator(mticker.MultipleLocator(4))

        ax = plt.subplot(self.grid2[3, 0])
        ax.clear()

        for idx, s in enumerate(fog_layer.servers):
            name = 'server ' + str(idx)
            performance_logger.servers_status[name].append(s.load_calc())

        for key, value in performance_logger.servers_status.items():
            plt.plot(value, label=key)

        plt.title('throughput', fontsize=8, weight='bold')
        plt.xlabel('time [sec]', weight='bold')
        plt.ylabel('servers', weight='bold')
        plt.legend(prop={'size': 7, 'weight': 'bold'}, loc='upper left')
        ax.xaxis.label.set_size(7)
        ax.yaxis.label.set_size(7)
        #ln = np.arange(max(0, len(value) - self.max_show), len(value), 4)
        #plt.xticks(range(len(ln)), ln)
        #ax.xaxis.set_major_locator(mticker.MultipleLocator(4))
        plt.pause(0.04)



        #############

        if last:
            plt.savefig("results/" + str(schedule_type) + '_' + str(migration_type) + '_' + str(reward_type) + "_measures.svg")

    def visualize_tasks_stat(self, task_logger, schedule_type, migration_type, last):
        plt.figure("tasks")
        ax = plt.subplot()
        ax.clear()
        plt.title('Task System')
        plt.xlabel('Time Unit')
        plt.ylabel('Number Of Tasks')
        plt.grid(True)
        for key, value in task_logger.task_status.items():
            plt.plot(value[-self.max_show:], label=key)

        ln = np.arange(max(0, len(value) - self.max_show), len(value), 4)
        plt.xticks(range(len(ln)), ln)
        ax.xaxis.set_major_locator(mticker.MultipleLocator(4))

        plt.legend(prop={'size': 10}, loc='upper right')
        plt.pause(0.01)
        if last:
            plt.savefig("results/" + str(schedule_type) + '_' + str(migration_type) + "_tasks_status.png")

    def vis_rate_load(self, fog_layer, performance_logger, last, schedule_type):
        plt.figure("servers load")
        ax = plt.subplot()
        ax.clear()
        plt.title('Servers Load')
        plt.xlabel('Time Unit')
        plt.ylabel('Utilization')
        plt.grid(True)
        for idx, s in enumerate(fog_layer.servers):
            name = 'server ' + str(idx)
            performance_logger.servers_status[name].append(s.load_calc())

        for key, value in performance_logger.servers_status.items():
            plt.plot(value[-self.max_show:], label=key)
        ln = np.arange(max(0, len(value) - self.max_show), len(value), 4)
        plt.xticks(range(len(ln)), ln)
        ax.xaxis.set_major_locator(mticker.MultipleLocator(4))

        plt.legend(prop={'size': 10}, loc='upper right')
        plt.pause(0.04)
        if last:
            plt.savefig("results/" + str(schedule_type) + "_devices_status_results.png")

    def vis_reward_convergence_MO(self, rewards, performance_logger, last, schedule_type, reward_type, sorting_algorithm):
        plt.figure("Reward").suptitle('sorting algorithm ' + str(sorting_algorithm), fontsize=12, weight='bold')
        x = np.array(rewards).mean(axis=0)

        if isinstance(x, float):
            x = np.empty((4,))
            x[:] = np.nan

        performance_logger.rewards.append(x)
        labels = ['utilization std', 'occ std', 'utilization median', 'occ median']

        ax = plt.subplot(self.grid[0, 0])
        ax.clear()
        plt.title(labels[0])
        plt.xlabel('Time')
        plt.ylabel('average reward')
        plt.plot(np.array(performance_logger.rewards)[:, 0], marker='o')
        plt.grid(True)
        # plt.legend(prop={'size': 10}, loc='upper right')

        ax = plt.subplot(self.grid[0, 1])
        ax.clear()
        plt.title(labels[1])
        plt.xlabel('Time')
        plt.ylabel('average reward')
        plt.plot(np.array(performance_logger.rewards)[:, 1], marker='o')
        plt.grid(True)
        # plt.legend(prop={'size': 10}, loc='upper right')

        ax = plt.subplot(self.grid[1, 0])
        ax.clear()
        plt.title(labels[2])
        plt.xlabel('Time')
        plt.ylabel('average reward')
        plt.plot(np.array(performance_logger.rewards)[:, 2], marker='o')
        plt.grid(True)
        # plt.legend(prop={'size': 10}, loc='upper right')

        ax = plt.subplot(self.grid[1, 1])
        ax.clear()
        plt.title(labels[3])
        plt.xlabel('Time')
        plt.ylabel('average reward')
        plt.plot(np.array(performance_logger.rewards)[:, 3], marker='o')
        plt.grid(True)
        # plt.legend(prop={'size': 10}, loc='upper right')

        plt.pause(0.01)
        if last:
            plt.savefig("results/" + str(schedule_type) + "_reward_convergence_" +
                          str(reward_type) + "_" + str(sorting_algorithm) + ".png")

    def vis_reward_convergence_episodes_average_MO(self, performance_logger, last, schedule_type, reward_type,
                                                   sorting_algorithm):
        plt.figure("Reward average").suptitle('sorting algorithm ' + str(sorting_algorithm), fontsize=12, weight='bold')
        performance_logger.average_rewards.append(np.mean(performance_logger.rewards[-10:-1], axis=0))
        labels = ['utilization std', 'occ std', 'utilization median', 'occ median']

        ax = plt.subplot(self.grid[0, 0])
        ax.clear()
        plt.title(labels[0])
        plt.xlabel('Time')
        plt.ylabel('average reward')
        plt.plot(np.array(performance_logger.average_rewards)[:, 0], marker='o')
        plt.grid(True)
        # plt.legend(prop={'size': 10}, loc='upper right')

        ax = plt.subplot(self.grid[0, 1])
        ax.clear()
        plt.title(labels[1])
        plt.xlabel('Time')
        plt.ylabel('average reward')
        plt.plot(np.array(performance_logger.average_rewards)[:, 1], marker='o')
        plt.grid(True)
        # plt.legend(prop={'size': 10}, loc='upper right')

        ax = plt.subplot(self.grid[1, 0])
        ax.clear()
        plt.title(labels[2])
        plt.xlabel('Time')
        plt.ylabel('average reward')
        plt.plot(np.array(performance_logger.average_rewards)[:, 2], marker='o')
        plt.grid(True)
        # plt.legend(prop={'size': 10}, loc='upper right')

        ax = plt.subplot(self.grid[1, 1])
        ax.clear()
        plt.title(labels[3])
        plt.xlabel('Time')
        plt.ylabel('average reward')
        plt.plot(np.array(performance_logger.average_rewards)[:, 3], marker='o')
        plt.grid(True)
        # plt.legend(prop={'size': 10}, loc='upper right')

        plt.pause(0.01)
        if last:
            plt.savefig("results/" + str(schedule_type) + "_reward_episode_convergence_" +
                        str(reward_type) + "_" + str(sorting_algorithm) + ".png")

    def vis_reward_convergence_SO(self, rewards, performance_logger, last, schedule_type, reward_type, sorting_algorithm):
        plt.figure("Reward")
        x = np.mean(rewards)
        performance_logger.rewards.append(x)

        ax = plt.subplot()
        ax.clear()
        plt.title('Reward convergence')
        plt.xlabel('Time')
        plt.ylabel('average reward')
        plt.plot(np.array(performance_logger.rewards), marker='o')
        plt.grid(True)

        plt.pause(0.01)
        if last:
            plt.savefig("results/" + str(schedule_type) + "_reward_convergence_" +
                          str(reward_type) + "_" + str(sorting_algorithm) + ".png")

    def vis_reward_convergence_episodes_average_SO(self, performance_logger, last, schedule_type, reward_type,
                                                    sorting_algorithm):
        plt.figure("Reward average")
        performance_logger.average_rewards.append(np.mean(performance_logger.rewards[-10:-1]))
        ax = plt.subplot()
        ax.clear()
        plt.title('Reward Convergence')
        plt.xlabel('episodes')
        plt.ylabel('average reward')
        plt.plot(np.array(performance_logger.average_rewards), marker='o')
        plt.grid(True)

        plt.pause(0.01)
        if last:
            plt.savefig("results/" + str(schedule_type) + "_reward_episode_convergence_" +
                        str(reward_type) + "_" + str(sorting_algorithm) + ".png")
