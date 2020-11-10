import tkinter as tk
import time
import json
import tkinter
import time
import argparse
import copy
import pandas as pd
import asteroids_exp
import pdb


class Agent:

    def __init__(self):
        self.args = asteroids_exp.parse_args()
        self.args['visual'] = True
        self.state, self.window_width, self.window_height = asteroids_exp.init_asteroid_model(self.args)
        self.view = None

    def act(self, state, direction, time):
        xv, yv = self.get_move(direction)
        state = asteroids_exp.move(state, xv, yv, time, self.window_width, self.window_height, self.args,
                                   lambda x: asteroids_exp.render(self.view, x))
        return state

    def get_move(self, key):
        return asteroids_exp.MOVES[key]


class Search_Agent(Agent):
    class Strategy:
        def __init__(self):
            self.stack = []

        def next(self):
            return self.stack.pop()

        def add(self, node):
            self.stack.append(node)

    class Node:
        def __init__(self, parent, state, move):
            self.parent = parent
            self.state = copy.deepcopy(state)
            self.move = move
            self.leaves = {}
            self.visited = {}

        def expand(self, outer):
            (direction, time) = self.move

            for action in ['q', 'w', 'a', 's', 'z', 'x', 'e', 'd', 'c', 's']:
                # note that 's' is also a legal move
                if self.parent and self.parent.move[0] == action:
                    continue
                for time in [1]:
                    state = outer.act(self.state, action, time)
                    child = outer.Node(self, state, (action, time))
                    self.leaves[(action, time)] = child
            return self.leaves.values()

    def retrieve_path(self, node):
        # print (node)
        if node.parent == None:
            return [node.move]
        else:
            path = self.retrieve_path(node.parent)
            path.append(node.move)
            return path

    def run(self):
        root = self.Node(None, self.state, ('s', 0))
        strategy = self.Strategy()
        strategy.add(root)
        try:
            while (True):
                current = strategy.next()
                if current.state.goal == asteroids_exp.Goal.SUCCESS:
                    path = self.retrieve_path(current)
                    print("success!")
                    return path
                if current.state.goal == asteroids_exp.Goal.OK:
                    leaves = current.expand(self)
                    for leaf in leaves:
                        strategy.add(leaf)
        except IndexError:
            return []


bfs = Search_Agent()
path = bfs.run()
df = pd.DataFrame(path, columns=['direction', 'time'])
df.to_csv((".").join([bfs.args['in'].split(".")[0], "csv"]), index=False)
