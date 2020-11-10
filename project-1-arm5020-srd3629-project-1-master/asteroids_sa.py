# asteroid_sa.py
# Summer DiStefano (srd3629) & Adam Mercer (arm5020)
# CSCI331 - Project #1 - Analyzing Different AI Algorithms


import random
import math
import pandas as pd
import asteroids_exp


# Mapping of specific moves in the game to a specific letter label.
MOVES = {'q': (-1, -1), 'w': (0, -1), 'e': (1, -1), 'a': (-1, 0),
         'd': (1, 0), 'z': (-1, 1), 'x': (0, 1), 'c': (1, 1), 's': (0, 0)}

# Mapping of move labels to single integer IDs.
MOVEIDS = {0: 'q', 1: 'w', 2: 'e', 3: 'a', 4: 'd', 5: 'z', 6: 'x', 7: 'c', 8: 's'}


class SA_Agent:
    """
    Agent responsible for running a game of asteroids using simulated annealing.
    """
    def __init__(self):
        """
        Initialize environment and initial solution.
        """
        self.args = asteroids_exp.parse_args()
        self.args['visual'] = True
        self.env_state, self.window_width, self.window_height = asteroids_exp.init_asteroid_model(self.args)
        self.view = None
        # Create an initial solution that will be changed by SA.
        self.solution = []
        self.solution.append(('s', 0))
        i = 0
        while i < self.window_width:
            self.solution.append(('d', 1))
            i += 1
        self.solution = self.run_sa()


    """simulate a solution, return a reward value (10 points) """
    def reward(self, solution):
        """
        Calculates the number of collisions that occur during a simulated path through the game. It iterates through all
        the steps of the path and calls the move function to determine the number of collisions during each step. The
        total number of collisions for the whole path is used as the reward value for a specific solution.
        arg solution: List of steps to be simulated
        return: Reward value (number of collisions)
        """
        num_collisions = 0
        for step in solution:
            xv, yv = MOVES[step[0]]
            move_state = asteroids_exp.move(self.env_state, xv, yv, step[1], self.window_width, self.window_height,
                                            self.args, lambda x: asteroids_exp.render(self.view, x))
            num_collisions += move_state.num_collisions
        return num_collisions


    """choose a new random solution, via a local edit of current solution (10 points) """
    def new_node(self, current):
        """
        Takes the current solution move set and randomly modifies the direction of one move to create a new solution.
        arg current: The current solution to copy and modify
        return: A new solution
        """
        new_sol = current.copy()  # copy of node 'current'
        num_moves = len(current)  # number of moves in current's solution
        edit_loc = random.randint(1, num_moves - 1)  # move in solution to be edited
        new_move = MOVEIDS[random.randint(0, 8)]  # new move to put into the edit location
        if new_move == 's':
            new_sol[edit_loc] = (new_move, 0)
        else:
            new_sol[edit_loc] = (new_move, 1)
        return new_sol


    def schedule(self, time):
        """
        Creates a schedule value based on the current time in the program.
        arg time: Current program time
        return: Schedule value
        """
        if time == 500:
            return 0
        return 1 / time


    """run high-level simulated annealing algorithm (30 points)"""
    def run_sa(self):
        """
        Main simulated-annealing algorithm. Used to determine a good path for specific asteroid games.
        return: Best solution found
        """
        current_node = self.solution
        sa_time = 1  # Current program time
        T = self.schedule(sa_time)  # Schedule value
        while sa_time > 0:
            # If schedule value is 0, keep current solution.
            if T == 0:
                return current_node
            next_node = self.new_node(current_node)  # Randomly generated new solution based on current solution
            delta_e = self.reward(next_node) - self.reward(current_node)  # Net reward between current & new solution
            # If net reward is positive, switch to new solution.
            if delta_e > 0:
                current_node = next_node
            else:
                """determine whether to move to new state or remain in same place (10 points) """
                probability = math.exp(delta_e / T)  # Probability new solution will be accepted
                random_num = random.random()
                # If probability > randomly generated decimal between 0 and 1, switch to new solution.
                if probability > random_num:
                    current_node = next_node
            sa_time += 1
            T = self.schedule(sa_time)
        return current_node


def main():
    a = SA_Agent()
    """ a.solution should be a list of ordered pairs of (directions, steps),
        just as in the asteroid_tree.py from hw4 
    """
    df = pd.DataFrame(a.solution, columns=['direction', 'time'])
    df.to_csv((".").join([a.args['in'].split(".")[0], "csv"]), index=False)
    print(a.env_state.goal)


if __name__ == '__main__':
    main()

# asteroid_sa.py
