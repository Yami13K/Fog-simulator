from Simulator import FogLayer, UsersManager, TasksLogger, PerformanceLogger, Visualization
from LoadBalancingAgorithms import Scheduler
import warnings
import pickle
import numpy as np
import config as cf

warnings.filterwarnings("ignore")

system_state = 'generate scenarios'
# system_state = 'load scenarios'
rng2 = np.random.RandomState(1)

scenario_number = 4
for seed_num in range(14, 18):
    scenario_number += 1
    rng1 = np.random.RandomState(seed_num)

    if system_state == 'generate scenarios':
        scenario_logger = []
    else:
        with open('scenarios/scenario_' + str(seed_num) + '.pkl', 'rb') as saved:
            scenario_logger = pickle.load(saved)

    if system_state == 'generate scenarios':
        servers_num = int(rng1.uniform(5, 15))
        users_num = int(rng1.uniform(15, 30))
        scenario_logger.append(('servers_num', servers_num))
        scenario_logger.append(('users_num', users_num))
    else:
        servers_num = scenario_logger.pop(0)[1]
        users_num = scenario_logger.pop(0)[1]

    schedule_type = 'RL'
    greedy_type = 'reliability'
    # sorting algorithms --> ['NDS', 'TLO']
    sorting_algorithm = 'NDS'
    # reward types --> [non-linear-MO, linear-MO , SO]
    reward_type = 'SO'
    migration_method = 'Random'

    scheduler = Scheduler.Scheduler(schedule_type, migration_method,  servers_num, reward_type, sorting_algorithm,greedy_type, rng2,
                                    system_state)
    fog_layer = FogLayer.FogLayer(servers_num, scheduler, cf.bandwidth_fog_layer, rng1, scenario_logger, system_state)
    users_manager = UsersManager.UsersManager(users_num, rng1, scenario_logger, fog_layer.filesIds, system_state)

    task_logger = TasksLogger.TasksLogger()
    performance_logger = PerformanceLogger.PerformanceLogger(servers_num)
    visualizer = Visualization.Visualization()

    all_generated, all_done, all_out, generation_cnt = 0, 0, 0, 0
    rewards = []
    print('_____________________Start scenario ' + str(scenario_number) + ' method ' +
          schedule_type + '_______________________________')

    for time_counter in range(cf.time_steps):

        reward, next_state, actions, utilization = 0, 0, [], []

        new_tasks = users_manager.send_tasks(time_counter, task_logger, performance_logger, scenario_logger, rng1)
        all_generated += len(new_tasks)
        fog_layer.receive_tasks(new_tasks)

        # migration should happened here.
        reward_migration, next_state_migration, actions_migration, utilization_migration = fog_layer.scheduler.migration(
                fog_layer.servers, fog_layer.bandwidth_fog_layer, time_counter, task_logger, time_counter % 5 == 0)

        if fog_layer.are_servers_capable() and len(fog_layer.scheduler.tasks_buffer) > 0:
            reward, next_state, actions, utilization = fog_layer.schedule(task_logger, time_counter)
        else:
            # normally this happened in the schedule function
            task_logger.task_status['waiting in fog Buffer'].append(len(fog_layer.scheduler.tasks_buffer))

        done_tasks = fog_layer.execute(time_counter, task_logger, performance_logger, scenario_logger, rng1)
        performance_logger.average_utilization.append(np.mean(fog_layer.get_utilization()))

        all_done += len(done_tasks)

        if reward != 0:
            rewards.append(reward)

        if cf.visualization:
            if (time_counter % 100) == 0 and time_counter != 0:
                visualizer.vis_reward(rewards, performance_logger, True if (time_counter + 100) == cf.time_steps else False, schedule_type,
                                                     reward_type, sorting_algorithm)
                rewards = []

            if (time_counter % 1000) == 0 and time_counter != 0:
                visualizer.vis_average_reward(performance_logger, True if (time_counter + 1000) == cf.time_steps else False, schedule_type, reward_type, sorting_algorithm)

            visualizer.visualize_tasks_stat(task_logger, schedule_type, migration_method, (time_counter + 1) == cf.time_steps)
            if time_counter % 5 == 0:
                visualizer.visualize_measures(performance_logger, fog_layer, schedule_type, migration_method, reward_type, (time_counter + 10) == cf.time_steps)

        if cf.print_on_real_time:
            print('migration', time_counter, reward_migration, next_state_migration, actions_migration,
                  utilization_migration)
            print('schedule', time_counter, reward, next_state, actions, utilization)

        print('time_counter', time_counter)

    all_out = all_done + len(fog_layer.scheduler) + fog_layer.number_tasks()
    assert all_generated == all_out

    if cf.print_final_results:
        print(all_done, all_generated, all_done/all_generated)
        print(performance_logger.average_utilization)
        print(performance_logger.delay_measures['wait'])
        print(np.mean(performance_logger.delay_measures['wait']))
        print(np.mean(performance_logger.average_utilization))

    if system_state == 'generate scenarios':
        x = 'scenario_' + str(seed_num)
        with open('scenarios/' + x + '.pkl', 'wb') as saved:
            pickle.dump(scenario_logger, saved)

    results_save_path = 'performance_logger_' + schedule_type + '_' + migration_method + '_' + reward_type + '_' + greedy_type + '_' + \
        str(scenario_number)
    with open('Results_pkl/' + str(scenario_number) + '/' + results_save_path + '.pkl', 'wb') as saved:
        pickle.dump(performance_logger.__dict__, saved)

    results_save_path = 'tasks_logger_' + schedule_type + '_' + migration_method + '_' + reward_type + '_' + greedy_type + '_' + \
        str(scenario_number)
    with open('Results_pkl/' + str(scenario_number) + '/' + results_save_path + '.pkl', 'wb') as saved:
        pickle.dump(task_logger.__dict__, saved)

    print('_____________________ Done scenario ' + str(scenario_number) + '______________________________________')

