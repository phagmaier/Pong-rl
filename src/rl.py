import numpy as np
class NN:
    def __init__(self):
        self.H = 128 # number of hidden layer neurons
        self.batch_size = 10 
        self.learning_rate = 1e-4
        self.gamma = 0.99 # discount factor for reward
        self.decay_rate = 0.99 # decay factor for RMSProp leaky sum of grad^2
        self.D = 3 * 2 # input dimensionality: 3X2 grid (3 rows 2 cols)
        
        # Initialize models for both players
        self.model = {}
        self.model2 = {}  # Add second model
        
        # Initialize weights for both models
        self.model['W1'] = np.random.randn(self.H,self.D) / np.sqrt(self.D)
        self.model['W2'] = np.random.randn(self.H) / np.sqrt(self.H)
        self.model2['W1'] = np.random.randn(self.H,self.D) / np.sqrt(self.D)
        self.model2['W2'] = np.random.randn(self.H) / np.sqrt(self.H)
        
        # Initialize gradient buffers for both models
        self.grad_buffer = { k : np.zeros_like(v) for k,v in self.model.items() }
        self.grad_buffer2 = { k : np.zeros_like(v) for k,v in self.model2.items() }
        
        # Initialize RMSprop caches for both models
        self.rmsprop_cache = { k : np.zeros_like(v) for k,v in self.model.items() }
        self.rmsprop_cache2 = { k : np.zeros_like(v) for k,v in self.model2.items() }


    def sigmoid(self, x): 
        return 1.0 / (1.0 + np.exp(-x)) # sigmoid "squashing" function to interval [0,1]

    def discount_rewards(self,r):
        """ take 1D float array of rewards and compute discounted reward """
        discounted_r = np.zeros_like(r)
        running_add = 0
        for t in reversed(range(0, r.size)):
            if r[t] != 0: 
                running_add = 0 # reset the sum, since this was a game boundary (pong specific!)
            running_add = running_add * self.gamma + r[t]
            discounted_r[t] = running_add
        return np.float32(discounted_r)


    def policy_forward(self, x, player1=True):
        # Use appropriate model based on player
        model = self.model if player1 else self.model2
        h = np.dot(model['W1'], x)
        h[h<0] = 0 # ReLU nonlinearity
        logp = np.dot(model['W2'], h)
        p = self.sigmoid(logp)
        return p, h
    
    def policy_backward(self, eph, epdlogp, epx, player1=True):
        # Use appropriate model based on player
        model = self.model if player1 else self.model2
        dW2 = np.dot(eph.T, epdlogp).ravel()
        dh = np.outer(epdlogp, model['W2'])
        dh[eph <= 0] = 0 # backpro prelu
        dW1 = np.dot(dh.T, epx)
        return {'W1':dW1, 'W2':dW2}

