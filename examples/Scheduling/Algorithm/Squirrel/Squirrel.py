import numpy as np
import random

import leaf.application
import leaf.infrastructure
from leaf.infrastructure import *
from examples.Scheduling.setting import *

import examples.Scheduling.Util.Fitness as ft

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
    def __init__(self,devices, tasks, infrastructure, applications,bounds, num_squirrels, max_iter, gl, pc, pd,carbon):
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
        self.carbon=carbon
        self.best_min_iteration_number = max_iter

    def optimize(self):
        # Initialize the population of squirrels
        num_dimensions = len(self.bounds)
        population = np.zeros((self.num_squirrels, num_dimensions))
        for i in range(self.num_squirrels):
            for j in range(num_dimensions):
                population[i, j] = random.uniform(self.bounds[j][0], self.bounds[j][1])

        population = population.astype(int)

        # Evaluate the fitness of each squirrel
        fitness = np.zeros(self.num_squirrels)
        for i in range(self.num_squirrels):
            fitness[i] = ft.fitness(population[i],self.carbon, self.tasks,self.devices,self.applications,self.infrastructure)

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

                new_position = new_position.astype(int)
                # Evaluate the new position
                new_fitness = ft.fitness(new_position, self.carbon, self.tasks, self.devices, self.applications, self.infrastructure)

                # Update the squirrel's position if the new fitness is better
                if new_fitness < fitness[i]:
                    population[i] = new_position
                    fitness[i] = new_fitness

                    self.best_min_iteration_number= iteration

                    # Update the best solution if necessary
                    if new_fitness < best_fitness:
                        best_solution = new_position
                        best_fitness = new_fitness

            print(f"Iteration {iteration + 1}/{self.max_iter}, Best Fitness: {best_fitness}")

        self.global_best_position=best_solution
        self.global_best_score=best_fitness

        return best_solution, best_fitness

    def get_best_assignment(self):
        return self.global_best_position, self.global_best_score