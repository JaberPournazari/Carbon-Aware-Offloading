import csv
import os

import leaf.application
from examples.Scheduling.setting import *


def check_dir_exists(fullfilename):
    dirname = os.path.dirname(fullfilename)
    if not os.path.exists(dirname):
        os.makedirs(dirname)


def write_nodes(nodes):
    fullfilename='ResultsCsv/dataset/nodes.csv'
    check_dir_exists(fullfilename)

    #results=[node.cu,node.static_power for node in nodes]
    results = [(node.cu, node.power_model.static_power,node.type[0]) for node in nodes]

    with open(fullfilename, 'a', newline='') as f:
        writer = csv.writer(f)
        # write a row to the csv file
        for row in results:
            writer.writerow(row)


def write_nodes_statics():
    fullfilename = 'ResultsCsv/dataset/nodes_statics.csv'
    check_dir_exists(fullfilename)
    with open(fullfilename, 'a', newline='') as f:
        writer = csv.writer(f)
        # write a row to the csv file
        writer.writerow([MICROPROCESSORS_INITIAL_POWER_MEAN,MICROPROCESSORS_REMAINING_POWER_MEAN,
                        MICROPROCESSORS_BATTERY_POWER,MICROPROCESSORS_POWER_PER_CU])


def write_sensors(sensor_nodes):
    fullfilename = 'ResultsCsv/dataset/sensors.csv'
    check_dir_exists(fullfilename)

    # results=[node.cu,node.static_power for node in nodes]
    results = [(sensor.power_model.max_power, sensor.power_model.static_power, sensor.cu) for sensor in sensor_nodes]

    with open(fullfilename, 'a', newline='') as f:
        writer = csv.writer(f)
        # write a row to the csv file
        for row in results:
            writer.writerow(row)


def write_sensor_statics():
    fullfilename = 'ResultsCsv/dataset/sensor_statics.csv'
    check_dir_exists(fullfilename)
    with open(fullfilename, 'a', newline='') as f:
        writer = csv.writer(f)
        # write a row to the csv file
        writer.writerow([SENSOR_INITIAL_POWER_MEAN, SENSOR_REMAINING_POWER_MEAN])


def write_applications(applications):
    # applications[0].tasks
    fullfilename = 'ResultsCsv/dataset/applications.csv'
    check_dir_exists(fullfilename)

    #x= applications[0].tasks(type_filter=leaf.application.ProcessingTask)[0].cu


    # results=[node.cu,node.static_power for node in nodes]
    tasks_cu = [app.tasks(type_filter=leaf.application.ProcessingTask)[0].cu for app in applications]

    with open(fullfilename, 'a', newline='') as f:
        # write a row to the csv file
        for cu in tasks_cu:
            f.write(str(cu)+'\r')