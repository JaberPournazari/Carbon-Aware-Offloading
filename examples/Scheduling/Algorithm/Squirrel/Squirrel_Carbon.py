import networkx as nx

import examples.Scheduling.Algorithm.Squirrel.Squirrel
from examples.Scheduling.setting import MICROPROCESSORS_POWER_RAM
from examples.Scheduling.Util.util import calculate_schedule_carbon

import leaf.application
import leaf.infrastructure
from leaf.infrastructure import *

class TaskDeviceScheduler(examples.Scheduling.Algorithm.Squirrel.Squirrel.TaskDeviceScheduler):
    def __init__(self, devices, tasks, infrastructure, applications, bounds, num_squirrels, max_iter, gl, pc, pd):
        super().__init__(devices, tasks, infrastructure, applications, bounds, num_squirrels, max_iter, gl, pc, pd)

    def fitness(self, positions):
        # print(positions)
        positions_set=set(positions)
        i=0
        sum_total = 0
        sum_node=0
        sum_link=0
        sum_time=0
        static=0
        sum_emission = 0
        node_times = [0 for pos in set(self.devices)]

        final_schedule_carbon_used = calculate_schedule_carbon(positions, self.devices, self.tasks)

        for pos in positions:
            print('pos '+ str(pos))
            self.tasks[i].allocate(self.devices[pos])

            # self.tasks[i].node.power_model().power_per_cu=self.tasks[i].cu

            # calculating node consumed time
            node_times[pos] = node_times[pos] + self.tasks[i].cu / self.devices[pos].cu


            tmp = self.devices[pos].measure_power()
            sum_node = sum_node + tmp.dynamic

            if pos in positions_set:
                sum_node=sum_node+tmp.static
                positions_set.remove(pos)

            if final_schedule_carbon_used[i] == 0:
                sum_emission = sum_emission + tmp.dynamic

            # calculating energy of links. here we do not consider energy linkes.
            # we will do it later
            app=self.applications[i]

            #for app in self.applications:
            for src_task_id, dst_task_id, data_flow in app.graph.edges.data("data"):
                src_task = app.graph.nodes[src_task_id]["data"]
                dst_task = app.graph.nodes[dst_task_id]["data"]

                if isinstance(src_task,leaf.application.SourceTask):
                    shortest_path = nx.shortest_path(self.infrastructure.graph, src_task.bound_node.name,
                                                     dst_task.node.name)
                else:
                    shortest_path = nx.shortest_path(self.infrastructure.graph, src_task.node.name,
                                                     dst_task.bound_node.name)

                links = [self.infrastructure.graph.edges[a, b, 0]["data"] for a, b in nx.utils.pairwise(shortest_path)]
                data_flow.allocate(links)

                for link in links:
                    tmp=link.measure_power()
                    sum_link=sum_link+tmp.dynamic
                #TODO: Do not sum duplicated linkes static power
                #sum_link=sum_link+tmp.static

                #data_flow.deallocate()

            #self.tasks[i].deallocate()
            i = i + 1

        # each kilo watt has 0.5kg CO2
        sum_emission = sum_emission * 0.5 / 1000

        sum_time = sum(node_times)
        sum_ram = sum_time * MICROPROCESSORS_POWER_RAM
        sum_total =sum_node + sum_ram + sum_link + sum_emission


        # print(positions)
        # print(sum_total)
        # print('==================')


        for app in self.applications:
            for src_task_id, dst_task_id, data_flow in app.graph.edges.data("data"):
                data_flow.deallocate()


        for tsk in self.tasks:
            tsk.deallocate()

        # TODO: Do not final sum for fitness
        return sum_total