import numpy as np
from pong import *
from rl import *
import json
from tqdm import tqdm


def write_game(twoDarr):
    #print("WRITING GAME")
    with open('sample_game.txt', 'w') as f:
        for i in twoDarr:
            f.write(f"{int(i[0])} {int(i[1])} {int(i[2])} {int(i[3])} {int(i[4])} {int(i[5])}\n")

def serialize_numpy(obj):
    if isinstance(obj, np.ndarray):
        return obj.tolist()  # Convert NumPy array to a list
    raise TypeError(f"Type {type(obj)} not serializable")


def run(game, nn):
    my_count = 0
    game_history = []
    end_goal = 500000
    cur_x = game.get_state() 
    cur_x2 = game.get_state2()
    prev_x = None
    prev_x2 = None
    xs,hs,dlogps,drs = [],[],[],[]
    xs2,hs2,dlogps2,drs2 = [],[],[],[]
    running_reward = None
    running_reward2 = None
    reward_sum = 0
    reward_sum2 = 0
    episode_number = 0

    progress_bar = tqdm(total=end_goal, desc="Progress", unit="iteration")
        
    #while episode_number//nn.batch_size < 1000000:
    while episode_number//nn.batch_size < end_goal:

        if (episode_number+1)//nn.batch_size ==end_goal:
            game_history.append(game.get_state())
        
        x = cur_x - prev_x if prev_x is not None else np.zeros(nn.D)
        x2 = cur_x2 - prev_x2 if prev_x2 is not None else np.zeros(nn.D)
        prev_x = cur_x
        prev_x2 = cur_x2  # Fixed typo in prevx2
        
        # Pass player flag to policy_forward
        aprob, h = nn.policy_forward(x, player1=True)
        aprob2, h2 = nn.policy_forward(x2, player1=False)
        
        action = 1 if np.random.uniform() < aprob else 2
        action2 = 1 if np.random.uniform() < aprob2 else 2
        
        xs.append(x)
        xs2.append(x2)
        hs.append(h)
        hs2.append(h2)
        # Remove duplicate append
        # hs2.append(h2)  # This was duplicated
        
        y = 1 if action == 2 else 0
        y2 = 1 if action2 == 2 else 0
        dlogps.append(y - aprob)
        dlogps2.append(y2 - aprob2)
        
        cur_x, reward, done,cur_x2,reward2 = game.move(action, action2)
        #cur_x2, reward2, _ = game.move(action2, False)
        
        reward_sum += reward
        reward_sum2 += reward2
        
        drs.append(reward)
        drs2.append(reward2)
        
        if done:
            my_count +=1
            episode_number += 1
            
            # Process player 1
            epx = np.vstack(xs)
            eph = np.vstack(hs)
            epdlogp = np.vstack(dlogps)
            epr = np.vstack(drs)
            
            # Process player 2
            epx2 = np.vstack(xs2)
            eph2 = np.vstack(hs2)
            epdlogp2 = np.vstack(dlogps2)
            epr2 = np.vstack(drs2)
            
            # Clear arrays
            xs,hs,dlogps,drs = [],[],[],[]
            xs2,hs2,dlogps2,drs2 = [],[],[],[]
            
            # Calculate discounted rewards for both players
            discounted_epr = nn.discount_rewards(epr)
            discounted_epr -= np.mean(discounted_epr)
            discounted_epr /= np.std(discounted_epr)
            
            discounted_epr2 = nn.discount_rewards(epr2)
            discounted_epr2 -= np.mean(discounted_epr2)
            discounted_epr2 /= np.std(discounted_epr2)
            
            # Update gradients for both players
            epdlogp *= discounted_epr
            epdlogp2 *= discounted_epr2
            
            grad = nn.policy_backward(eph, epdlogp, epx, player1=True)
            grad2 = nn.policy_backward(eph2, epdlogp2, epx2, player1=False)
            
            for k in nn.model: 
                nn.grad_buffer[k] += grad[k]
            
            for k in nn.model2: 
                nn.grad_buffer2[k] += grad2[k]


            if episode_number % nn.batch_size == 0:
                progress_bar.update(1)
                #print(f"DONE WITH ITERATION: {episode_number//nn.batch_size}")
                for k,v in nn.model.items():
                    g = nn.grad_buffer[k]
                    nn.rmsprop_cache[k] = nn.decay_rate * nn.rmsprop_cache[k] + (1-nn.decay_rate) * g**2
                    nn.model[k] += nn.learning_rate * g/(np.sqrt(nn.rmsprop_cache[k]) + 1e-5)
                    nn.grad_buffer[k] = np.zeros_like(v)

                for k,v in nn.model2.items():
                    g2 = nn.grad_buffer2[k]
                    nn.rmsprop_cache2[k] = nn.decay_rate * nn.rmsprop_cache2[k] + (1-nn.decay_rate) * g2**2
                    nn.model2[k] += nn.learning_rate * g2/(np.sqrt(nn.rmsprop_cache2[k]) + 1e-5)
                    nn.grad_buffer2[k] = np.zeros_like(v)

            running_reward = reward_sum if running_reward is None else running_reward * 0.99 + reward_sum * 0.01
            running_reward2 = reward_sum2 if running_reward2 is None else running_reward2 * 0.99 + reward_sum2 * 0.01
            #print(f'resetting env. episode reward total FOR P1 was {reward_sum}, {running_reward}')
            if episode_number % 1000 == 0:
                with open('weights1.json', 'w') as f:
                    json.dump(nn.model, f, default=serialize_numpy)
                with open('weights2.json', 'w') as f:
                    json.dump(nn.model2, f, default=serialize_numpy)

            reward_sum = 0
            reward_sum2 = 0
            game.reset()
            #obsertation = game.get_state()
            prev_x = None
            prev_x2 = None

    with open('weights1.json', 'w') as f:
        json.dump(nn.model, f, default=serialize_numpy)
    
    with open('weights2.json', 'w') as f:
        json.dump(nn.model2, f, default=serialize_numpy)

    write_game(game_history)

if __name__ == '__main__':
    nn = NN()
    pong = Pong()
    run(pong, nn)
