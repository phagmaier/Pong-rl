import numpy as np
class NN:
    def __init__(self):
        self.H=200
        self.batchSize = 10
        self.learning_rate = 1e-4
        self.gamma = 0.99
        self.decay_rate = 0.99
        self.D = 6
        self.model = {}
        self.model['w1'] = np.random.randn(self.H,self.D)/np.sqrt(self.D)
        self.model['w2'] = np.random.randn(self.H)/np.sqrt(self.H)
        self.grad_buffer =  { k : np.zeros_like(v) for k,v in self.model.items() }
        self.rmsprop_cache = { k : np.zeros_like(v) for k,v in self.model.items() } 

    def sigmoid(self,x):
        return 1.0/(1.0+np.exp(-x))

    def discount_rewards(self,r):
        discounted_r = np.zeros_like(r)
        running_add = 0
        for t in reversed((range(0,r.size))):
            if r[t] != 0: 
                running_add = 0
            running_add = running_add * self.gamma + r[t]
            discounted_r[t] = running_add
        return discounted_r
    
    def policy_backward(self, eph, epdlogp, epx):
        dw2 = np.dot(eph.T, epdlogp).ravel()
        dh = np.outer(epdlogp, self.model['w2'])
        dh = np.outer(epdlogp, self.model['w2'])
        dh[eph<=0] = 0
        dw1 = np.dot(dh.T, epx)
        return {"w1":dw1, "w2":dw2}

    def policy_forward(self,x):
      h = np.dot(self.model['w1'], x)
      h[h<0] = 0 # ReLU nonlinearity
      logp = np.dot(self.model['w2'], h)
      p = self.sigmoid(logp)
      return p, h
