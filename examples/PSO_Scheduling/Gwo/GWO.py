# -*- coding: utf-8 -*-
"""
Created on Mon May 16 00:27:50 2016

@author: Hossam Faris

https://github.com/7ossam81/EvoloPy/blob/master/EvoloPy/solution.py
"""

import random
import numpy
import math
import leaf.application
import leaf.infrastructure
from leaf.infrastructure import *
from examples.PSO_Scheduling.setting import *

class TaskDeviceScheduler:

#def GWO(objf, lb, ub, dim, SearchAgents_no, Max_iter):
    def __init__(self, devices, tasks, infrastructure, applications, lb, ub, dim, SearchAgents_no, Max_iter):
        # Max_iter=1000
        # lb=-100
        # ub=100
        # dim=30
        # SearchAgents_no=5

        self.devices=devices
        self.tasks=tasks
        self.infrastructure=infrastructure
        self.applications=applications
        self.Max_iter = Max_iter
        self.lb = lb
        self.ub = ub
        self.dim = dim
        self.SearchAgents_no = SearchAgents_no
        self.best_min_iteration_number = Max_iter

    def optimize(self):
        Max_iter=self.Max_iter
        lb=self.lb
        ub = self.ub
        dim= self.dim
        SearchAgents_no= self.SearchAgents_no

        # initialize alpha, beta, and delta_pos
        Alpha_pos = numpy.zeros(dim)
        Alpha_score = float("inf")

        Beta_pos = numpy.zeros(dim)
        Beta_score = float("inf")

        Delta_pos = numpy.zeros(dim)
        Delta_score = float("inf")

        if not isinstance(lb, list):
            lb = [lb] * dim
        if not isinstance(ub, list):
            ub = [ub] * dim

        # Initialize the positions of search agents
        Positions = numpy.zeros((SearchAgents_no, dim))
        for i in range(dim):
            Positions[:, i] = (
                numpy.random.uniform(0, 1, SearchAgents_no) * (ub[i] - lb[i]) + lb[i]
            )

        Positions=Positions.astype(int)

        Positions[:, i]= [int(j) for j in Positions[:, i]]

        Convergence_curve = numpy.zeros(Max_iter)

        # Main loop
        for l in range(0, Max_iter):
            for i in range(0, SearchAgents_no):

                # Return back the search agents that go beyond the boundaries of the search space
                for j in range(dim):
                    Positions[i, j] = numpy.clip(Positions[i, j], lb[j], ub[j])

                # Calculate objective function for each search agent
                fitness = self.fitness(Positions[i, :])

                # Update Alpha, Beta, and Delta
                if fitness < Alpha_score:
                    Delta_score = Beta_score  # Update delta
                    Delta_pos = Beta_pos.copy()
                    Beta_score = Alpha_score  # Update beta
                    Beta_pos = Alpha_pos.copy()
                    Alpha_score = fitness
                    # Update alpha
                    Alpha_pos = Positions[i, :].copy()

                    self.best_min_iteration_number= l

                if fitness > Alpha_score and fitness < Beta_score:
                    Delta_score = Beta_score  # Update delte
                    Delta_pos = Beta_pos.copy()
                    Beta_score = fitness  # Update beta
                    Beta_pos = Positions[i, :].copy()

                if fitness > Alpha_score and fitness > Beta_score and fitness < Delta_score:
                    Delta_score = fitness  # Update delta
                    Delta_pos = Positions[i, :].copy()

            a = 2 - l * ((2) / Max_iter)
            # a decreases linearly fron 2 to 0

            # Update the Position of search agents including omegas
            for i in range(0, SearchAgents_no):
                for j in range(0, dim):

                    r1 = random.random()  # r1 is a random number in [0,1]
                    r2 = random.random()  # r2 is a random number in [0,1]

                    A1 = 2 * a * r1 - a
                    # Equation (3.3)
                    C1 = 2 * r2
                    # Equation (3.4)

                    D_alpha = abs(C1 * Alpha_pos[j] - Positions[i, j])
                    # Equation (3.5)-part 1
                    X1 = Alpha_pos[j] - A1 * D_alpha
                    # Equation (3.6)-part 1

                    r1 = random.random()
                    r2 = random.random()

                    A2 = 2 * a * r1 - a
                    # Equation (3.3)
                    C2 = 2 * r2
                    # Equation (3.4)

                    D_beta = abs(C2 * Beta_pos[j] - Positions[i, j])
                    # Equation (3.5)-part 2
                    X2 = Beta_pos[j] - A2 * D_beta
                    # Equation (3.6)-part 2

                    r1 = random.random()
                    r2 = random.random()

                    A3 = 2 * a * r1 - a
                    # Equation (3.3)
                    C3 = 2 * r2
                    # Equation (3.4)

                    D_delta = abs(C3 * Delta_pos[j] - Positions[i, j])
                    # Equation (3.5)-part 3
                    X3 = Delta_pos[j] - A3 * D_delta
                    # Equation (3.5)-part 3

                    Positions[i, j] = (X1 + X2 + X3) / 3  # Equation (3.7)

            Convergence_curve[l] = Alpha_score

            if l % 1 == 0:
                print(["At iteration " + str(l) + " the best fitness is " + str(Alpha_score)])

        bestIndividual = Alpha_pos
        self.global_best_position=bestIndividual
        self.global_best_score = Alpha_score

        return Alpha_score

    def fitness(self, positions):
        # print(positions)
        positions_set=set(positions)
        i=0
        sum_total = 0
        sum_node=0
        sum_link=0
        sum_time=0
        static=0
        node_times = [0 for pos in set(self.devices)]

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
        sum_total =sum_node + sum_ram + sum_link


        # print(positions)
        # print(sum_total)
        # print('==================')



        # TODO: Do not final sum for fitness
        return sum_total

    def get_best_assignment(self):
        return self.global_best_position, self.global_best_score
