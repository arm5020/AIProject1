
import tkinter as tk 
import pandas as pd
import json
import tkinter
import argparse
import copy
import pdb
#from getkey import getkey
from enum import Enum

MOVES = {'q': (-1, -1), 'w': (0, -1), 'e': (1,-1), 'a':(-1,0),
    'd': (1, 0), 'z': (-1, 1),'x': (0,1),'c': (1,1), 's': (0,0)}

class Goal(Enum):
    """Indicate whether we've reached a goal or not"""
    FAIL = 0
    OK = 1
    SUCCESS = 2

class Asteroid:
    """Represent a model of an asteroid"""
    def __init__(self,x,y,s,v):
        self.x = x
        self.y = y
        self.s = s
        self.v = v

    def coords(self):
        """return a bounding box for the ship"""
        return self.x-self.s/2, self.y-self.s/2, self.x + self.s/2, self.y + self.s/2

class Ship:
    """Represent a model of a ship"""
    def __init__(self, x,y,fuel):
        self.x = x
        self.y = y
        self.fuel = fuel
        self.yv = 0
        self.xv = 0 
        self.lastx = 0
        self.lasty = 0

    def coords(self):
        """return a bounding box for the ship"""        
        return self.x-1, self.y-1, self.x+1, self.y+1

class State:
    """Represent state of puzzle at high level"""
    def __init__(self, asteroids, ship):
        self.asteroids = asteroids
        self.ship = ship
        self.goal = Goal.OK
        self.num_collisions = 0

class View:
    """Manage the visual presentation"""
    def __init__(self, window, canvas, asteroids,spaceship_center, spaceship_outer, fuel):
        self.window = window
        self.canvas = canvas
        self.asteroids = asteroids
        self.spaceship_center = spaceship_center
        self.spaceship_outer = spaceship_outer
        self.fuel = fuel 

def collision(state, window_height):
    """Test for collistions between ship and asteroid"""

    collided = False
    for asteroid in state.asteroids:
        b = asteroid.coords()
        if ((b[0] <= state.ship.x <= b[2]) and (b[1] <= state.ship.y <= b[3])):
            collided = True
    
    if state.ship.x < 0 or state.ship.y < 0 or state.ship.y >= window_height:
            collided = True
    return collided

def create_window(window_width, window_height):
    """The main window of the animation"""

    window = tkinter.Tk()
    window.title("Asteroid Belt")  
    # Uses python 3.6+ string interpolation
    window.geometry(f'{window_width}x{window_height}')
    return window
 
def create_canvas(window):
    """Create a canvas for animation and add it to main window"""

    canvas = tkinter.Canvas(window)
    canvas.configure(bg="black")
    canvas.pack(fill="both", expand=True)
    return canvas

def parse_args():
    """Parse all command line arguments."""

    ap = argparse.ArgumentParser()

    # Add the arguments to the parser
    ap.add_argument("-i", "--in", required=True,
       help="Name of input file")
    ap.add_argument("-m", "--move", 
       help="Name of move file")
    ap.add_argument("-v", "--visual", action='store_true', 
        help="visualize") # this is what a flag argument looks like
    args = vars(ap.parse_args())
    return args

def read_spec(filename):
    """Read the specifications for the asteroid game here"""

    f = open(filename)
    initial = json.load(f)
    return initial

def init_asteroid_model(args):
    """Create asteroid belt model"""
    
    initial_data = read_spec(args["in"])
    initial_state = State ([Asteroid(x,y,s,v) for s,x,y,v in zip(initial_data['s'],initial_data['x'],initial_data['y'],initial_data['v'])], Ship(1, initial_data['h']/2, initial_data['f']))
    window_width=initial_data['w']
    window_height=initial_data['h']

    #print ("Remaining fuel: %d" % initial_state.ship.fuel)

    return initial_state, window_width, window_height

def coords(canvas, item):
    """Return the center of a canvas item

    Arguments

    item -- the item whose coordinates are desired
    """
    
    x1,y1,x2,y2 = canvas.coords(item)
    return (x2+x1)/2, (y2+y1)/2

def render(view,state):
    """Visualize a state

    Arguments

    state -- the state to be visualized
    """

    if view == None:
        return
    x,y = coords(view.canvas,view.spaceship_center)
    view.canvas.move(view.spaceship_center, state.ship.x*SCALE-x, state.ship.y*SCALE-y)       
    view.canvas.move(view.spaceship_outer, state.ship.x*SCALE-x, state.ship.y*SCALE-y)       
    for a1, a2 in zip(view.asteroids, state.asteroids):
        x,y = coords(view.canvas,a1)
        view.canvas.move(a1, a2.x*SCALE - x, a2.y*SCALE - y)

    if state.goal == Goal.FAIL:
        view.canvas.create_text(view.canvas.winfo_width()/2, view.canvas.winfo_height()/2, text="You Lose!", fill="red", font=('Helvetica',72))
    elif state.goal == Goal.SUCCESS:
        view.canvas.create_text(view.canvas.winfo_width()/2, view.canvas.winfo_height()/2, text="You Win!", fill="yellow", font=('Helvetica',72))

    view.canvas.itemconfig(view.fuel, text="Fuel: %d" % state.ship.fuel)

    view.window.update()

def init_asteroid_view(state, window_width, window_height):
    """create asteroid belt view

    arguments:

    state -- state of the game
    window_width -- width of window
    window_height -- height of window
    """

    global SCALE, TIME

    TIME = 0 # for display only
    SCALE = 5 # for display only

    window = create_window(window_width * SCALE, window_height * SCALE)
    canvas = create_canvas(window)

    asteroids = [canvas.create_rectangle((a.x-a.s/2)*SCALE,(a.y-a.s/2)*SCALE,(a.x+a.s/2)*SCALE,(a.y+a.s/2)*SCALE,fill="blue", outline="white", width=4) for a in state.asteroids]
    spaceship_outer = canvas.create_oval((state.ship.x)*SCALE-10,state.ship.y*SCALE-10,state.ship.x*SCALE+10,state.ship.y*SCALE+10, outline="yellow", width=2)
    spaceship_center = canvas.create_oval(state.ship.x*SCALE-1,state.ship.y*SCALE-1,state.ship.x*SCALE+1,state.ship.y*SCALE+1, fill="red", outline="red", width=4)
    fuel = canvas.create_text(window_width*SCALE/2, (window_height-50)*SCALE, text="Fuel: %d" % state.ship.fuel, fill="green", font=('Helvetica',36))
    return View(window, canvas, asteroids,spaceship_center, spaceship_outer, fuel)

def move(state, xv, yv, time, window_width, window_height, args, renderer):
    """simulate a move through the asteroid belt

    arguments:

    state -- state of the game
    window_width -- width of window
    window_height -- height of window
    xv -- velocity in x direction
    yv -- velocity in y direction
    window_width -- width of window
    window_height -- height of window
    args -- command line args
    renderer -- command for visualizing output
    """
    state = copy.deepcopy(state)
    
    if xv != state.ship.xv or yv != state.ship.yv:
        state.ship.fuel -= 1
        if state.ship.fuel < 0:
            state.goal = Goal.FAIL
            if args["visual"]:
                renderer(state)
            return state

    state.ship.xv = xv
    state.ship.yv = yv

    for i in range(time):
        for a in state.asteroids:
            a.y += a.v
            if a.y + a.s/2 > window_height:
                a.y = a.s/2

        state.ship.x += xv
        state.ship.y += yv

        if collision(state,window_height):
            state.goal = Goal.FAIL
            state.num_collisions += 1
        if state.ship.x >= window_width:
            state.goal = Goal.SUCCESS
            if args["visual"]:
                renderer(state)
            return state
        if args["visual"]:
            renderer(state)

    #state.goal = Goal.OK
    return state

def main():
    args = parse_args()

    initial_state, window_width, window_height  = init_asteroid_model(args)
    view = init_asteroid_view(initial_state, window_width, window_height)
    state = copy.deepcopy(initial_state)
    
    moves = pd.read_csv(args["move"])
    for i, rec in moves.iterrows():
        if args["visual"]:
            render(view,state)
            #key = getkey()
        vx, vy = MOVES[rec['direction']]
        state = move(state, vx, vy, rec['time'], window_width, window_height, args, lambda x: render(view, x))
        if state.goal != Goal.OK:
            break
    if args["visual"]:
        render(view,state)
        #key = getkey()

    else:
        print(state.goal)
        print("Fuel left: %d" % state.ship.fuel)

if __name__ == '__main__':
    main()


