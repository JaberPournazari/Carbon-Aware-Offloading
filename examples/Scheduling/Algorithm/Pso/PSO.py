############################################################################################################
import numpy as np
import csv
import random
import leaf.application
import leaf.infrastructure
from leaf.infrastructure import *
import sys
from examples.Scheduling.setting import *
import examples.Scheduling.Util.Fitness as ft

class TaskDeviceScheduler:
    # def __init__(self, devices, tasks,infrastructure,applications,num_particles=30, max_iter=100, c1=1.5, c2=1.5, w=0.9,
    #              w_damp=0.99):
    def __init__(self, devices, tasks, infrastructure, applications, carbon ,num_particles=30, max_iter=100, c1=1.5, c2=1.5,
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
        self.carbon = carbon
        self.particles_position = np.random.randint(0, self.num_devices, size=(self.num_particles, self.num_tasks))
        self.particles_velocity = np.zeros_like(self.particles_position, dtype=float)
        self.particles_best_position = np.copy(self.particles_position)
        self.particles_best_score = np.array([ft.fitness(pos,self.carbon, self.tasks,self.devices,self.applications,self.infrastructure) for pos in self.particles_best_position])
        self.global_best_position = self.particles_best_position[np.argmin(self.particles_best_score)]
        self.global_best_score = np.min(self.particles_best_score)
        self.best_min_iteration_number = self.max_iter
        self.scheduling_dict={}


    def __check_multi_params__(self,alpha,beta,gamma,delta):
        if alpha+beta+gamma+delta != 1:
            raise ValueError("Sum of multi-objective parameters should be equal to 1.")

    def optimize(self):
        print('Starting B-PSO')
        best_min_iteration_number = self.max_iter
        for l in range(self.max_iter):
            print(l)
            for i in range(self.num_particles):
                # Update velocity and position (using modified PSO rules for permutations)
                for j in range(self.num_tasks):
                    # Calculate velocity update
                    r1, r2 = random.random(), random.random()
                    cognitive_component = self.c1 * r1 * (
                                self.particles_best_position[i][j] - self.particles_position[i][j])
                    social_component = self.c2 * r2 * (self.global_best_position[j] - self.particles_position[i][j])
                    self.particles_velocity[i][j] += self.w * self.particles_velocity[i][
                        j] + cognitive_component + social_component

                # Apply a permutation based velocity handling method
                temp_position = np.argsort(np.argsort(self.particles_velocity[i]))
                self.particles_position[i] = np.random.permutation(temp_position)

                #====== Added by Reza ===================
                # TODO: PSO body should be changed or studied more (Apply a permutation based velocity handling method)
                arr = self.particles_position[i].copy()
                for k in range(len(self.particles_position[i])):
                    if arr[k] >= self.num_devices:
                        arr[k] = np.random.randint(0, self.num_devices)

                self.particles_position[i] = arr.copy()
                #========================================

                # Calculate fitness
                current_fitness = ft.fitness(self.particles_position[i], self.carbon, self.tasks,self.devices,self.applications,self.infrastructure)



                # Update personal best
                if current_fitness < self.particles_best_score[i]:
                    self.particles_best_score[i] = current_fitness
                    self.particles_best_position[i] = self.particles_position[i].copy()
                    self.list_fitness.append(current_fitness)

                # Update global best
                if current_fitness < self.global_best_score:
                    best_min_iteration_number = l
                    self.global_best_score = current_fitness
                    self.global_best_position = self.particles_position[i].copy()

            self.scheduling_dict[l]=[self.global_best_position,self.global_best_score]

            # Dampen inertia weight
            self.w *= self.w_damp

        self.best_min_iteration_number = best_min_iteration_number
        print("best_number_iteration_print = ", best_min_iteration_number)

    def get_best_assignment(self):
        return self.global_best_position, self.global_best_score


