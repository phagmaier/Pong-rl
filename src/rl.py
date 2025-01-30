import numpy as np

class NN:
    def __init__(self):
        self.H = 20 # number of hidden layer neurons
        #self.H = 200 # number of hidden layer neurons
        #self.batch_size = 10 # every how many episodes to do a param update?
        self.batch_size = 10 
        self.learning_rate = 1e-4
        self.gamma = 0.99 # discount factor for reward
        self.decay_rate = 0.99 # decay factor for RMSProp leaky sum of grad^2
        #resume = False # resume from previous checkpoint?
        #render = False
        self.D = 3 * 2 # input dimensionality: 3X2 grid (3 rows 2 cols)
        self.file_str = "weights.txt"
        self.model = {}
        self.model['W1'] = np.random.randn(self.H,self.D) / np.sqrt(self.D) # "Xavier" initialization
        self.model['W2'] = np.random.randn(self.H) / np.sqrt(self.H)
        self.grad_buffer = { k : np.zeros_like(v) for k,v in self.model.items() } # update buffers that add up gradients over a batch
        self.rmsprop_cache = { k : np.zeros_like(v) for k,v in self.model.items() } # rmsprop memory


    def sigmoid(self, x): 
        return 1.0 / (1.0 + np.exp(-x)) # sigmoid "squashing" function to interval [0,1]

    def discount_rewards(self,r):
        """ take 1D float array of rewards and compute discounted reward """
        discounted_r = np.zeros_like(r)
        running_add = 0
        for t in reversed(range(0, r.size)):
            if r[t] != 0: running_add = 0 # reset the sum, since this was a game boundary (pong specific!)
            running_add = running_add * self.gamma + r[t]
            discounted_r[t] = running_add
        return np.float32(discounted_r)

    def policy_forward(self,x):
        h = np.dot(self.model['W1'], x)
        h[h<0] = 0 # ReLU nonlinearity
        logp = np.dot(self.model['W2'], h)
        p = self.sigmoid(logp)
        return p, h # return probability of taking action 2, and hidden state
    
    def policy_backward(self,eph, epdlogp, epx):
        """ backward pass. (eph is array of intermediate hidden states) """
        dW2 = np.dot(eph.T, epdlogp).ravel()
        dh = np.outer(epdlogp, self.model['W2'])
        dh[eph <= 0] = 0 # backpro prelu
        dW1 = np.dot(dh.T, epx)
        return {'W1':dW1, 'W2':dW2}

    ''' 
    def prepro(self,I):
      """ prepro 210x160x3 uint8 frame into 6400 (80x80) 1D float vector """
      I = I[35:195] # crop
      I = I[::2,::2,0] # downsample by factor of 2
      I[I == 144] = 0 # erase background (background type 1)
      I[I == 109] = 0 # erase background (background type 2)
      I[I != 0] = 1 # everything else (paddles, ball) just set to 1
      return I.astype(np.float32).ravel()
    '''

            




    

