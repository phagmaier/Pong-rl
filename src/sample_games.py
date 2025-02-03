import numpy as np
from pong import *
from rl import *
import json
from tqdm import tqdm


def deserialize_numpy(d):
    return {k: np.array(v) for k, v in d.items()}  

def set_weights(nn):
    with open("w1.json", "w") as f:
        json.dump(nn.model, f, default=serialize_numpy)

    with open("w2.json", "w") as f:
        json.dump(nn.model, f, default=serialize_numpy)




def write_game(twoDarr):
    #print("WRITING GAME")
    with open('one_game.txt', 'w') as f:
        for i in twoDarr:
            f.write(f"{int(i[0])} {int(i[1])} {int(i[2])} {int(i[3])} {int(i[4])} {int(i[5])}\n")

def serialize_numpy(obj):
    if isinstance(obj, np.ndarray):
        return obj.tolist()  # Convert NumPy array to a list
    raise TypeError(f"Type {type(obj)} not serializable")


def run(game, nn):
    set_weights(nn)
    game_history = []
    prev_x = None
    prev_x2 = None
    done = False
    cur_x = None
    cur_x2 = None
    while not done:
        game_history.append(game.get_state())
        x = cur_x - prev_x if prev_x is not None else np.zeros(nn.D)
        x2 = cur_x2 - prev_x2 if prev_x2 is not None else np.zeros(nn.D)
        prev_x = cur_x
        prev_x2 = cur_x2  # Fixed typo in prevx2
        
        # Pass player flag to policy_forward
        aprob, _ = nn.policy_forward(x, player1=True)
        aprob2, _= nn.policy_forward(x2, player1=False)
        
        action = 1 if np.random.uniform() < aprob else 2
        action2 = 1 if np.random.uniform() < aprob2 else 2
        cur_x, _, done,cur_x2,_= game.move(action, action2)
    write_game(game_history)

if __name__ == '__main__':
    nn = NN()
    pong = Pong()
    run(pong, nn)
