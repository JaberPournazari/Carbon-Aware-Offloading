import numpy as np
import random

import leaf.application
import leaf.infrastructure
from leaf.infrastructure import *
from examples.Scheduling.setting import *

#calling this algorithm:
# Define the objective function (e.g., Sphere function)
# def sphere_function(x):
#     return sum(x ** 2)
#
#
# # Define the search space bounds
# bounds = [(-100, 100)] * 10  # 10-dimensional problem
#
# # Set SSA parameters
# num_squirrels = 50
# max_iter = 100
# gl = 0.9
# pc = 0.1
# pd = 0.1


class TaskDeviceScheduler:
    def __init__(self,devices, tasks, infrastructure, applications,bounds, num_squirrels, max_iter, gl, pc, pd):
        """
            Squirrel Search Algorithm (SSA)

            Parameters:
            - objective_function: The function to be optimized.
            - bounds: A list of tuples [(min, max)] for each dimension of the search space.
            - num_squirrels: Number of squirrels (population size).
            - max_iter: Maximum number of iterations.
            - gl: Global leader probability.
            - pc: Probability of random foraging.
            - pd: Probability of predator presence.

            Returns:
            - best_solution: The best solution found.
            - best_fitness: The fitness of the best solution.
            """
        self.devices = devices
        self.tasks = tasks
        self.infrastructure = infrastructure
        self.applications = applications
        self.bounds =bounds
        self.num_squirrels =num_squirrels
        self.max_iter =max_iter
        self.gl=gl
        self.pc=pc
        self.pd= pd

    def optimize(self):
        # Initialize the population of squirrels
        num_dimensions = len(self.bounds)
        population = np.zeros((self.num_squirrels, num_dimensions))
        for i in range(self.num_squirrels):
            for j in range(num_dimensions):
                population[i, j] = random.uniform(self.bounds[j][0], self.bounds[j][1])

        # Evaluate the fitness of each squirrel
        fitness = np.zeros(self.num_squirrels)
        for i in range(self.num_squirrels):
            fitness[i] = self.fitness(population[i])

        # Initialize the best solution
        best_index = np.argmin(fitness)
        best_solution = population[best_index]
        best_fitness = fitness[best_index]

        # Main loop
        for iteration in range(self.max_iter):
            for i in range(self.num_squirrels):
                if random.random() < self.gl:
                    # Global leader phase
                    new_position = population[i] + random.random() * (best_solution - population[i])
                else:
                    if random.random() < self.pc:
                        # Random foraging phase
                        new_position = np.zeros(num_dimensions)
                        for j in range(num_dimensions):
                            new_position[j] = random.uniform(self.bounds[j][0], self.bounds[j][1])
                    else:
                        # Predator presence phase
                        if random.random() < self.pd:
                            new_position = population[i] + random.random() * (population[best_index] - population[i])
                        else:
                            new_position = population[i] + random.random() * (
                                        population[random.randint(0, self.num_squirrels - 1)] - population[i])

                # Ensure the new position is within bounds
                new_position = np.clip(new_position, [b[0] for b in self.bounds], [b[1] for b in self.bounds])

                # Evaluate the new position
                new_fitness = self.fitness(new_position)

                # Update the squirrel's position if the new fitness is better
                if new_fitness < fitness[i]:
                    population[i] = new_position
                    fitness[i] = new_fitness

                    # Update the best solution if necessary
                    if new_fitness < best_fitness:
                        best_solution = new_position
                        best_fitness = new_fitness

            print(f"Iteration {iteration + 1}/{self.max_iter}, Best Fitness: {best_fitness}")

        return best_solution, best_fitness

    def fitness(self, positions):
        # print(positions)
        positions_set = set(positions)
        i = 0
        sum_total = 0
        sum_node = 0
        sum_link = 0
        sum_time = 0
        static = 0

        node_times = [0 for pos in set(self.devices)]

        for pos in positions:
            print('pos ' + str(pos))
            self.tasks[i].allocate(self.devices[pos])

            # self.tasks[i].node.power_model().power_per_cu=self.tasks[i].cu

            # calculating node consumed time
            node_times[pos] = node_times[pos] + self.tasks[i].cu / self.devices[pos].cu

            tmp = self.devices[pos].measure_power()
            sum_node = sum_node + tmp.dynamic

            if pos in positions_set:
                sum_node = sum_node + tmp.static
                positions_set.remove(pos)

            # calculating energy of links. here we do not consider energy linkes.
            # we will do it later
            app = self.applications[i]

            # for app in self.applications:
            for src_task_id, dst_task_id, data_flow in app.graph.edges.data("data"):
                src_task = app.graph.nodes[src_task_id]["data"]
                dst_task = app.graph.nodes[dst_task_id]["data"]

                if isinstance(src_task, leaf.application.SourceTask):
                    shortest_path = nx.shortest_path(self.infrastructure.graph, src_task.bound_node.name,
                                                     dst_task.node.name)
                else:
                    shortest_path = nx.shortest_path(self.infrastructure.graph, src_task.node.name,
                                                     dst_task.bound_node.name)

                links = [self.infrastructure.graph.edges[a, b, 0]["data"] for a, b in nx.utils.pairwise(shortest_path)]
                data_flow.allocate(links)

                for link in links:
                    tmp = link.measure_power()
                    sum_link = sum_link + tmp.dynamic
                # TODO: Do not sum duplicated linkes static power
                # sum_link=sum_link+tmp.static

                # data_flow.deallocate()

            # self.tasks[i].deallocate()
            i = i + 1

        sum_time = sum(node_times)
        sum_ram = sum_time * MICROPROCESSORS_POWER_RAM
        sum_total = sum_node + sum_ram + sum_link

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
