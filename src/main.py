import numpy as np
from pong import *
from rl import *
import json

def serialize_numpy(obj):
    if isinstance(obj, np.ndarray):
        return obj.tolist()  # Convert NumPy array to a list
    raise TypeError(f"Type {type(obj)} not serializable")

def run(game, nn):
    cur_x = game.get_state() 
    xs, hs, dlogps, drs = [], [], [], []
    while True:
        prev_x = None
        xs,hs,dlogps,drs = [],[],[],[]
        running_reward = None
        reward_sum = 0
        episode_number = 0
        while True:
            x = cur_x - prev_x if prev_x is not None else np.zeros(nn.D)
            prev_x = cur_x
            aprob, h = nn.policy_forward(x)
            action = 2 if np.random.uniform() < aprob else 3
            xs.append(x)
            hs.append(h)
            y = 1 if action == 2 else 0
            dlogps.append(y - aprob)
            
            #nned to impliment this in game and also output the outputs
            cur_x, reward, done = game.move(action, True)
            reward_sum += reward
            
            drs.append(reward)
            if done:
                episode_number +=1

                epx = np.vstack(xs)
                eph = np.vstack(hs)
                epdlogp = np.vstack(dlogps)
                epr = np.vstack(drs)
                xs,hs,dlogps,drs = [],[],[],[]

                discounted_epr = nn.discount_rewards(epr)
                discounted_epr -= np.mean(discounted_epr)
                discounted_epr /= np.std(discounted_epr)

                epdlogp *= discounted_epr
                grad = nn.policy_backward(eph,epdlogp,epx)

                for k in nn.model: 
                    nn.grad_buffer[k] += grad[k]

                if episode_number % nn.batch_size == 0:
                    for k,v in nn.model.items():
                        g = nn.grad_buffer[k]
                        nn.rmsprop_cache[k] = nn.decay_rate * nn.rmsprop_cache[k] + (1-nn.decay_rate) * g**2
                        nn.model[k] += nn.learning_rate * g/(np.sqrt(nn.rmsprop_cache[k]) + 1e-5)
                        nn.grad_buffer[k] = np.zeros_like(v)
                running_reward = reward_sum if running_reward is None else running_reward * 0.99 + reward_sum * 0.01
                print(f'resetting env. episode reward total was {reward_sum}, {running_reward}')
                if episode_number % 100 == 0:
                    with open('data.json', 'w') as f:
                        #print(type(nn.model))
                        #print(nn.model['W1'])

                        #json.dump(nn.model, f)
                        json.dump(nn.model, f, default=serialize_numpy)
                reward_sum = 0
                game.reset()
                obsertation = game.get_state()
                prev_x = None


if __name__ == '__main__':
    nn = NN()
    pong = Pong()
    run(pong, nn)


        
