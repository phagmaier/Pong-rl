import numpy as np
from pong import *
from nn import *
import json
from tqdm import tqdm
import time

TOTAL = 100000

def custom_encoder(obj):
    return obj.tolist()

def write_games(arr):
    with open("games.txt", 'w') as file:
        for i in arr:
            file.write(f"{i[0]} {i[1]} {i[2]} {i[3]} {i[4]} {i[5]}\n")

def get_example_games(nn1, nn2):
    curr_x = None
    curr_x2 = None
    prev_x = None
    prev_x2 = None
    game = Pong()
    done = False
    games = []
    for _ in range(10):
        while not done:
            games.append(game.get_state1())
            curr_x = game.get_state1()
            curr_x2 = game.get_state2()
            x = curr_x - prev_x if prev_x is not None else np.zeros(nn1.D)
            x2 = curr_x2 - prev_x2 if prev_x2 is not None else np.zeros(nn2.D)
            prev_x =  curr_x
            prev_x2 = curr_x2
            aprob, h = nn1.policy_forward(x)
            aprob2, _ = nn2.policy_forward(x2)
            action1 = 2 if np.random.uniform() < aprob else 3
            action2 = 2 if np.random.uniform() < aprob2 else 3
            done = game.move(action1,action2)
        game.reset()
        done = False
    write_games(games)

def error_check(nn1, nn2):
    curr_x = None
    curr_x2 = None
    prev_x = None
    prev_x2 = None
    game = Pong()
    done = False
    games = []
    for _ in range(500):
        games.append(game.get_state1())
        curr_x = game.get_state1()
        curr_x2 = game.get_state2()
        x = curr_x - prev_x if prev_x is not None else np.zeros(nn1.D)
        x2 = curr_x2 - prev_x2 if prev_x2 is not None else np.zeros(nn2.D)
        prev_x =  curr_x
        prev_x2 = curr_x2
        aprob, h = nn1.policy_forward(x)
        aprob2, _ = nn2.policy_forward(x2)
        action1 = 2 if np.random.uniform() < aprob else 3
        action2 = 2 if np.random.uniform() < aprob2 else 3
        done = game.move(action1,action2)
        if done:
            print("GAME ENDED")
            game.reset()
            done = False
    write_games(games)

        
def main(add_weights = False):
    nn1 = NN();
    nn2 = NN(); 
    get_example_games(nn1,nn2)

if __name__ == '__main__':
    main()
