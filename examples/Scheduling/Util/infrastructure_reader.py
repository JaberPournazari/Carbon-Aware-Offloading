import csv


def read_sensor_statics():
    fullfilename = 'ResultsCsv/dataset/sensor_statics.csv'
    result=[]
    with open(fullfilename, 'r', newline='') as f:
        reader = csv.reader(f,delimiter=',')
        for row in reader:
            result=row

    return [int(i) for i in result]

def read_sensors():
    fullfilename = 'ResultsCsv/dataset/sensors.csv'

    result = []
    with open(fullfilename, 'r', newline='') as f:
        reader = csv.reader(f,delimiter=',')
        for row in reader:
            result.append([float(i) for i in row])

    return result

def read_nodes_statics():
    fullfilename = 'ResultsCsv/dataset/nodes_statics.csv'
    result = []
    with open(fullfilename, 'r', newline='') as f:
        reader = csv.reader(f, delimiter=',')
        for row in reader:
            result = row

    return [float(i) for i in result]

def read_nodes():
    fullfilename = 'ResultsCsv/dataset/nodes.csv'
    result = []
    with open(fullfilename, 'r', newline='') as f:
        reader = csv.reader(f, delimiter=',')
        for row in reader:
            result.append(row)

    return result

def read_applications():
    fullfilename = 'ResultsCsv/dataset/applications.csv'
    result = []
    with open(fullfilename, 'r', newline='') as f:
        result=f.readlines()

    result=[int(i) for i in result]
    return result