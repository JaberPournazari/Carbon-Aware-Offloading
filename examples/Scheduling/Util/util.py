import csv,os

import numpy as np
from matplotlib import pyplot as plt

from leaf.infrastructure import NodeCarbon


def read_data(datatype):
    with open(datatype.lower() + '.csv', newline='') as f:
        reader = csv.reader(f)
        data = list(reader)
    return data


def write_data(datatype, row):
    fullfilename=datatype.lower() + '.csv'
    dirname=os.path.dirname(fullfilename)
    if not os.path.exists(dirname):
        os.makedirs(dirname)
    # open the file in the write mode
    with open(fullfilename, 'a', newline='') as f:
        writer = csv.writer(f)
        # write a row to the csv file
        writer.writerow(row)


def write_to_csv(node_energies,filename):
    # save results into csv file before plotting
    power_values = node_energies
    # Extract dynamic and static power values
    dynamic_power = [p.dynamic for p in power_values]
    static_power = [p.static for p in power_values]

    write_data(f'ResultsCsv/{filename}-dynamic', [f"{i:.3f}" for i in dynamic_power])
    write_data(f'ResultsCsv/{filename}-static', [f"{i:.3f}" for i in static_power])

def write_total_power(node_energies,filename,devices_len):
    dynamic_power = [p.dynamic for p in node_energies]
    static_power = [p.static for p in node_energies]
    total_power = sum(dynamic_power) + sum(static_power)
    write_data(f'ResultsCsv/{filename}-total', [devices_len,total_power])

def write_total(sum_time,filename,devices_len):
    write_data(f'ResultsCsv/{filename}-total', [devices_len,sum_time])


def write_scheduling_data(file_name,scheduling_dict):
    fullfilename = file_name.lower() + '.csv'
    dirname = os.path.dirname(fullfilename)
    if not os.path.exists(dirname):
        os.makedirs(dirname)

    # open the file in the write mode
    with open(fullfilename, 'a', newline='') as f:
        #writer = csv.writer(f)
        # write a row to the csv file
        #for k,v in scheduling_dict.items():
        #     f.write(str(k) +','+ str(v[0]) +','+ str(v[1]))
        result = ''.join(str(k) +','+ str(v[0]) +','+ str(v[1]) + '\n' for k, v in scheduling_dict.items())
        f.write(result)


def calculate_schedule_carbon(positions,devices,tasks):
    tmp = np.zeros(len(positions), dtype=int)
    battery_capacity = {k: v for k, v in enumerate(tmp)}

    for j in range(len(devices)):
        if isinstance(devices[j], NodeCarbon):
            battery_capacity[j] = devices[j].battery_power

    for k in range(len(positions)):
        if not isinstance(devices[positions[k]], NodeCarbon):
            continue
        elif isinstance(devices[positions[k]], NodeCarbon):
            if tasks[k].cu <= battery_capacity[k]:
                battery_capacity[k] = battery_capacity[k] - tasks[k].cu

    # This final result shows an array with length equal to length of positions array.
    # Each cell has value of 1 or 0.
    # 1: It used node batteries
    # 0: It did not use node batteries or node do not have battery or battery is occupied by another task
    # we use this array at the end of scheduling to calculate CO2 generation.
    final_schedule_carbon_used = [1 if v >= 1 else 0 for k, v in battery_capacity.items()]

    return final_schedule_carbon_used


