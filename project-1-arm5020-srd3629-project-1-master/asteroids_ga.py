# asteroid_ga.py
# Summer DiStefano (srd3629) & Adam Mercer (arm5020)
# CSCI331 - Project #1 - Analyzing Different AI Algorithms

import tkinter as tk
import time
import json
import tkinter
import argparse
import random
import copy
import math
import pandas as pd
import asteroids_exp
import pdb
import numpy

# import ga

# Mapping of specific moves in the game to a specific letter label.
MOVES = {'q': (-1, -1), 'w': (0, -1), 'e': (1, -1), 'a': (-1, 0),
         'd': (1, 0), 'z': (-1, 1), 'x': (0, 1), 'c': (1, 1), 's': (0, 0)}

# Mapping of move labels to single integer IDs.
MOVEIDS = {0: 'q', 1: 'w', 2: 'e', 3: 'a', 4: 'd', 5: 'z', 6: 'x', 7: 'c', 8: 's'}



class Solution:
    def __init__(self, solution):
        self.fitness = 0
        self.solution = solution


class GAAgent:
    def __init__(self):
        self.args = asteroids_exp.parse_args()
        self.args['visual'] = True
        self.env_state, self.window_width, self.window_height = asteroids_exp.init_asteroid_model(self.args)
        self.view = None
        self.pop_size = 2
        self.population = []
        # Initialize population with 2 starting solutions.
        self.init_pop()
        # Run program and get final solution.
        self.solution = self.run_ga(4)

    def init_pop(self):
        """ Create two initial starting solutions. """
        solution1 = [('s', 0)]
        solution2 = [('s', 0)]
        i = 0
        while i < self.window_width + 1:
            solution1.append(('e', 1))
            solution2.append(('x', 1))
            i += 1
        sol1 = Solution(solution1)
        sol2 = Solution(solution2)
        self.population.append(sol1)
        self.population.append(sol2)

    def calc_pop_fitness(self, population):
        pop = population
        tot = 0
        for sol in pop:
            fit = self.fitnessCalc(sol)
            sol.fitness = fit
            tot += fit
        return tot

    def fitnessCalc(self, sol):
        num_collisions = 0
        fuel_left = 0
        goal = 0
        for step in sol.solution:
            xv, yv = MOVES[step[0]]
            move_state = asteroids_exp.move(self.env_state, xv, yv, step[1], self.window_width, self.window_height,
                                            self.args, lambda x: asteroids_exp.render(self.view, x))
            num_collisions += move_state.num_collisions
            fuel_left = move_state.ship.fuel
            goal = move_state.goal
        fuel = fuel_left
        col = num_collisions
        if goal == asteroids_exp.Goal.SUCCESS:
            z = 100
        else:
            z = 0

        sol.fitness = (fuel) + (-1 * col) + z
        return sol.fitness

    def select_mating_pool(self, population):
        sol1 = population[0]
        sol2 = population[1]

        if sol2.fitness > sol1.fitness:
            temp = sol2
            sol2 = sol1
            sol1 = temp

        for sol in population:
            if sol.fitness > sol1.fitness:
                sol1 = sol
            elif sol.fitness > sol2.fitness:
                sol2 = sol

        par = [sol1, sol2]

        return par

    def crossover(self, parents, num_offspring):
        offspring = []  # Set of solutions
        sol_len = len(parents[0].solution) # Number of moves in a solution
        crossover_point = math.floor(sol_len / 2)  # Point in parent solutions where crossover will take place.
        # Create a solution set for each offspring.
        for i in range(num_offspring):
            solution = []
            # Fill solution up to before the crossover point with movements from parent1's solution.
            parent1 = parents[0]
            for j in range(0, crossover_point):
                solution.append(parent1.solution[j])
            # Fill the rest of solution with movements from parent2's solution.
            parent2 = parents[1]
            for j in range(crossover_point + 1, sol_len):
                solution.append(parent2.solution[j])
            # Append solution to offspring list.
            sol = Solution(solution)
            offspring.append(sol)
        return offspring

    def mutation(self, population):
        """ Mutate a random single move in each solution in the population. """
        for solution in population:
            num_moves = len(solution.solution)  # number of moves in the current solution
            edit_loc = random.randint(1, num_moves - 1)  # move in solution to be edited
            new_move = MOVEIDS[random.randint(0, 8)]  # new move to put into the edit location
            if new_move == 's':
                solution.solution[edit_loc] = (new_move, 0)
            else:
                solution.solution[edit_loc] = (new_move, 1)
        return population

    def run_ga(self, solPerPop):

        newPop = self.population

        numGenerations = 20

        for gen in range(numGenerations):
            print("Generation : ", gen)

            parents = self.select_mating_pool(newPop)
            self.calc_pop_fitness(parents)

            offspring_crossover = self.crossover(parents, solPerPop)
            self.calc_pop_fitness(offspring_crossover)

            offspring_mutation = self.mutation(offspring_crossover)
            self.calc_pop_fitness(offspring_mutation)

            newPop = []
            for i in range(len(parents)):
                newPop.append(parents[i])
            for x in range(len(offspring_mutation)):
                newPop.append(offspring_mutation[x])

        best = newPop[0]
        for x in newPop:
            if x.fitness > best.fitness:
                best = x
        return best

def main():
    a = GAAgent()
    print(a.solution.solution)
    df = pd.DataFrame(a.solution.solution, columns=['direction', 'time'])
    df.to_csv(".".join([a.args['in'].split(".")[0], "csv"]), index=False)


main()
