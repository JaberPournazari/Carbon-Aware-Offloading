import numpy as np
import csv
import random
import leaf.application
import leaf.infrastructure
from leaf.infrastructure import *
import sys
from examples.PSO_Scheduling.setting import *
from examples.PSO_Scheduling.Pso.PSO import *


class TaskDeviceScheduler:

    def __init__(self, devices, tasks, infrastructure, applications, num_particles=30, max_iter=100, c1=1.5, c2=1.5,
                 w=0.9, w_damp=0.99):
        self.devices = devices
        self.tasks = tasks
        self.infrastructure=infrastructure
        self.applications=applications
        self.num_tasks = len(tasks)
        self.num_devices = len(devices)

        self.list_fitness = []

        self.num_particles = num_particles
        self.max_iter = max_iter
        self.c1 = c1  # Cognitive (particle) weight
        self.c2 = c2  # Social (swarm) weight
        self.w = w  # Inertia weightx
        self.w_damp = w_damp  # Inertia damping after each iteration
        self.particles_position = np.random.randint(0, self.num_devices, size=(self.num_particles, self.num_tasks))
        self.particles_velocity = np.zeros_like(self.particles_position, dtype=float)
        self.particles_best_position = np.copy(self.particles_position)
        self.particles_best_score = np.array([self.fitness(pos) for pos in self.particles_best_position])
        self.global_best_position = self.particles_best_position[np.argmin(self.particles_best_score)]
        self.global_best_score = np.min(self.particles_best_score)
        self.best_min_iteration_number = self.max_iter

    def fitness(self, positions):
        # print(positions)
        positions_set=set(positions)
        i=0
        sum_total = 0
        sum_node=0
        sum_link=0
        sum_time=0
        static=0
        sum_emission=0
        node_times = [0 for pos in set(self.devices)]

        #added for test
        #positions=[1,2,1,3]
        tmp = np.zeros(len(positions),dtype=int)
        battery_capacity = {k:v for k,v in enumerate(tmp)}

        for j in range(len(self.devices)):
            if isinstance(self.devices[j],NodeCarbon):
                battery_capacity[j]=self.devices[j].battery_power


        for k in range(len(positions)):
            if not isinstance(self.devices[positions[k]],NodeCarbon):
                continue
            elif isinstance(self.devices[positions[k]],NodeCarbon):
                if self.tasks[k].cu <= battery_capacity[k]:
                    battery_capacity[k]=battery_capacity[k]- self.tasks[k].cu


        #This final result shows an array with length equal to length of positions array.
        #Each cell has value of 1 or 0.
        # 1: It used node batteries
        # 0: It did not use node batteries or node do not have battery or battery is occupied by another task
        # we use this array at the end of scheduling to calculate CO2 generation.
        final_schedule_carbon_used= [1 if v >=1 else 0 for k,v in battery_capacity.items()]




        for pos in positions:
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

                data_flow.deallocate()

            self.tasks[i].deallocate()
            i = i + 1

        sum_time = sum(node_times)
        sum_ram = sum_time * MICROPROCESSORS_POWER_RAM
        sum_total =sum_node + sum_ram + sum_link + sum_emission


        # print(positions)
        # print(sum_total)
        # print('==================')



        # TODO: Do not final sum for fitness
        return sum_total