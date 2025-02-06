import numpy as np
from pong import *
from nn import *
import json
from tqdm import tqdm
import time

TOTAL = 10000

def custom_decoder(obj):
    for key, value in obj.items():
        if isinstance(value, list):
            obj[key] = np.array(value)
    return obj



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
        

def train_p2(nn1, nn2):
    done_count = 0
    curr_x = None
    curr_x2 = None
    prev_x = None
    prev_x2 = None
    total = TOTAL
    game = Pong()
    count =0
    progress_bar = tqdm(total=total, desc="Progress", unit="iteration")
    #running_reward = None
    #reward_sum = 0
    xs,hs,dlogps,drs = [],[],[],[]
    while (count < total):
        curr_x = game.get_state1()
        curr_x2 = game.get_state2()
        x = curr_x - prev_x if prev_x is not None else np.zeros(nn1.D)
        x2 = curr_x2 - prev_x2 if prev_x2 is not None else np.zeros(nn2.D)
        prev_x =  curr_x
        prev_x2 = curr_x2
        aprob, _ = nn1.policy_forward(x)
        aprob2, h = nn2.policy_forward(x2)
        action1 = 2 if np.random.uniform() < aprob else 3
        action2 = 2 if np.random.uniform() < aprob2 else 3       
        xs.append(x2)
        hs.append(h)
        y = 1 if action2 == 2 else 0
        dlogps.append(y-aprob2)
        done = game.move(action1,action2)
        if done:
            drs.append(float(game.get_reward2()))
        else:
            drs.append(0.0)
        if done:
            done_count+=1
            
            exp = np.vstack(xs)
            eph = np.vstack(hs)
            epdlogp = np.vstack(dlogps)
            epr = np.vstack(drs)
            xs,hs,dlogps,drs = [],[],[],[]
            discounted_epr = nn2.discount_rewards(epr)
            discounted_epr -= np.mean(discounted_epr)
            discounted_epr /= np.std(discounted_epr)

            epdlogp *= discounted_epr
            grad = nn2.policy_backward(eph, epdlogp,exp)
            for k in nn2.model:
                nn2.grad_buffer[k] +=grad[k]
            if done_count == nn2.batchSize:
                count +=1
                done_count =0
                progress_bar.update(1)

                for k,v in nn2.model.items():
                    g = nn1.grad_buffer[k]
                    nn2.rmsprop_cache[k] = nn2.decay_rate * nn2.rmsprop_cache[k] + (1-nn2.decay_rate) * g**2
                    nn2.model[k] += nn2.learning_rate * g /(np.sqrt(nn2.rmsprop_cache[k]) + 1e-5)
                    nn2.grad_buffer[k] = np.zeros_like(v)
            if count %100 == 0:
                with open("weights2.json", 'w') as file:
                    json.dump(nn2.model, file, default=custom_encoder)

            game.reset()
 

def train_p1(nn1, nn2):
    done_count = 0
    curr_x = None
    curr_x2 = None
    prev_x = None
    prev_x2 = None
    total = TOTAL
    game = Pong()
    count =0
    progress_bar = tqdm(total=total, desc="Progress", unit="iteration")
    #running_reward = None
    #reward_sum = 0
    xs,hs,dlogps,drs = [],[],[],[]
    while (count < total):
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
        xs.append(x)
        hs.append(h)
        y = 1 if action1 == 2 else 0
        dlogps.append(y-aprob)
        done = game.move(action1,action2)
        if done:
            drs.append(float(game.get_reward1()))
        else:
            drs.append(0.0)
        if done:
            done_count+=1
            
            exp = np.vstack(xs)
            eph = np.vstack(hs)
            epdlogp = np.vstack(dlogps)
            epr = np.vstack(drs)
            xs,hs,dlogps,drs = [],[],[],[]
            discounted_epr = nn1.discount_rewards(epr)
            discounted_epr -= np.mean(discounted_epr)
            discounted_epr /= np.std(discounted_epr)

            epdlogp *= discounted_epr
            grad = nn1.policy_backward(eph, epdlogp,exp)
            for k in nn1.model:
                nn1.grad_buffer[k] +=grad[k]
            if done_count == nn1.batchSize:
                count +=1
                done_count =0
                progress_bar.update(1)

                for k,v in nn1.model.items():
                    g = nn1.grad_buffer[k]
                    nn1.rmsprop_cache[k] = nn1.decay_rate * nn1.rmsprop_cache[k] + (1-nn1.decay_rate) * g**2
                    nn1.model[k] += nn1.learning_rate * g /(np.sqrt(nn1.rmsprop_cache[k]) + 1e-5)
                    nn1.grad_buffer[k] = np.zeros_like(v)
            if count %100 == 0:
                with open("weights1.json", 'w') as file:
                    json.dump(nn1.model, file, default=custom_encoder)
            game.reset()

            game.reset()

def stupid():
    games = []
    game = Pong()
    done = False
    while not done:
        games.append(game.get_state1())
        done = game.move(0,0)
    write_games(games)

def main(add_weights = False):
    nn1 = NN();
    nn2 = NN(); 
    if add_weights:
        with open("weights1.json", 'r') as file:
            loaded_model = json.load(file, object_hook=custom_decoder)
        with open("weights2.json", 'r') as file:
            loaded_model = json.load(file, object_hook=custom_decoder)

    for i in range(5):
        train_p1(nn1,nn2)
        train_p2(nn1,nn2)
    get_example_games(nn1,nn2)
    #stupid()

if __name__ == '__main__':
    main()
