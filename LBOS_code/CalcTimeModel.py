import numpy as np

time_unit = 0.1  # sec --> 100 ms
scale = 1/time_unit


def scale_num(num):
    """
    :return:
    it calculate the actual value of the costs based on the clock of the system.
    """
    if num == 0:
        return num
    num *= scale
    return max(1, num)


def transfer_cost(input_data_size, bandwidth_resources):
    return scale_num(input_data_size / bandwidth_resources)


def return_cost(returned_data_size, bandwidth_resources):
    return np.ceil(scale_num(returned_data_size / bandwidth_resources))


def grab_files_cost(required_data_size, bandwidth_resources):
    return np.ceil(scale_num(required_data_size / bandwidth_resources))


def serving_cost(compute_demand, cpu_rate):
    return np.ceil(scale_num(compute_demand / cpu_rate))


def migrating_cost(input_data_size, bandwidth):
    return np.ceil(scale_num(input_data_size / bandwidth))