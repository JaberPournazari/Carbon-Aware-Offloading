from examples.Scheduling.Util.util import calculate_schedule_carbon
from examples.Scheduling.setting import MICROPROCESSORS_POWER_RAM

import leaf.application
import leaf.infrastructure
from leaf.infrastructure import *
from examples.Scheduling.setting import *
import numpy as np

def fitness(positions, carbon, tasks, devices,applications,infrastructure):
    positions_set = set(positions)
    i = 0
    sum_total = 0
    sum_node = 0
    sum_link = 0
    sum_time = 0
    static = 0
    sum_emission = 0
    node_times = [0 for pos in set(devices)]

    # Recharge batteries after optimizing for calculating again
    for dv in devices:
        dv.free_battery = MICROPROCESSORS_BATTERY_POWER

    #calculating variance of random position that algorithm provided
    #variance= np.var(positions)

    # if carbon:
    #     final_schedule_carbon_used = calculate_schedule_carbon(positions, devices, tasks)

    for pos in positions:
        #print('Node free battery before: ',  devices[pos]._get_free_battery())

        tasks[i].allocate(devices[pos])

        #print('Node free battery after: ', devices[pos]._get_free_battery())

        # calculating node consumed time
        node_times[pos] = round(node_times[pos] + tasks[i].cu / devices[pos].cu, 4)

        tmp = devices[pos].measure_power()
        sum_node = round(sum_node + tmp.dynamic)

        #   carbon = 700 - dynami power + static power + link power  = X --> -X * CO2Gram
        if pos in positions_set:
            sum_node = round(sum_node + tmp.static, 4)
            positions_set.remove(pos)

        if carbon:
            #if final_schedule_carbon_used[i] == 0:
            emis_calc = devices[pos]._get_free_battery() - tmp.dynamic
            if emis_calc < 0 :
                sum_emission= abs(emis_calc)

        # calculating energy of links. here we do not consider energy linkes.
        # we will do it later
        app = applications[i]

        # for app in self.applications:
        for src_task_id, dst_task_id, data_flow in app.graph.edges.data("data"):
            src_task = app.graph.nodes[src_task_id]["data"]
            dst_task = app.graph.nodes[dst_task_id]["data"]

            if isinstance(src_task, leaf.application.SourceTask):
                shortest_path = nx.shortest_path(infrastructure.graph, src_task.bound_node.name,
                                                 dst_task.node.name)
            else:
                shortest_path = nx.shortest_path(infrastructure.graph, src_task.node.name,
                                                 dst_task.bound_node.name)

            links = [infrastructure.graph.edges[a, b, 0]["data"] for a, b in nx.utils.pairwise(shortest_path)]
            data_flow.allocate(links)

            for link in links:
                tmp = link.measure_power()
                sum_link = sum_link + tmp.dynamic
            # TODO: Do not sum duplicated linkes static power
            # sum_link=sum_link+tmp.static

            # data_flow.deallocate()

        # self.tasks[i].deallocate()
        i = i + 1

    if carbon:
        # Each kilowatt.hour(Joule) has 0.842kg CO2
        #sum_emission = round(sum_emission * 0.842 / 1000 , 4)
        sum_emission = sum_emission * 0.842 / 1000
        #sum_emission = sum_emission

    sum_time = sum(node_times)
    sum_ram = sum_time * MICROPROCESSORS_POWER_RAM

    if carbon:
        #sum_total = 0.04*sum_node + 0.01*sum_ram + 0.01*sum_link + 0.94*sum_emission
        sum_total = 0.5 * sum_emission
    else:
        sum_total = 0.96*sum_node + 0.02*sum_ram + 0.02*sum_link

    # print(positions)
    # print(sum_total)
    # print('==================')

    for app in applications:
        for src_task_id, dst_task_id, data_flow in app.graph.edges.data("data"):
            data_flow.deallocate()

    for tsk in tasks:
        tsk.deallocate()


    # TODO: Do not final sum for fitness
    return sum_total