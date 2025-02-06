import math
import numpy as np
import random

BALLSPEED = 20.0
PADDLE_HEIGHT=200.0
MOVE_SIZE = 10.0
BALL_SIZE = 30.0
MAX_BOUNCE_ANGLE = math.pi / 4.0

WIDTH = 1200.0
HEIGHT = 1000.0
PADDING = 20.0
MID_X = 590.0
MID_Y = 490.0
MIN_Y = 20.0
MAX_Y =980.0
PADDLE_WIDTH = 20.0
PADDLE_HEIGHT = 200.0
BORDER_X = 20.0
BORDER_Y = 20.0
BORDER_WIDTH = 1160.0
BORDER_HEIGHT = 960.0

class Ball:
    def __init__(self):
        self.x = MID_X-10
        self.y = MID_Y-10
        self.v_x = self.get_dir() 
        self.v_y = 0.0

    def get_dir(self):
        if random.randint(0, 1) == 0:
            return -BALLSPEED
        else:
            return BALLSPEED

    def reset(self):
        self.x = MID_X-10
        self.y = MID_Y-10
        self.v_x = self.get_dir()
        self.v_y = 0
    
    def move(self):
        self.x+=self.v_x
        self.y +=self.v_y


class Paddle:
    def __init__(self):
        self.x = 0
        self.y = 0
    
    def set_one(self):
        self.x = 70 
        self.y = 400

    def set_two(self):
        self.x = 1110
        self.y = 400

    def move(self, action):
        #up
        if action == 2:
            if (self.y - MOVE_SIZE >= MIN_Y):
                self.y-=MOVE_SIZE
            else:
                self.y = MIN_Y
        #DOWN
        elif action == 3:
            if (self.y + PADDLE_HEIGHT + MOVE_SIZE <= MAX_Y):
                self.y += MOVE_SIZE
            else:
                self.y = MAX_Y
        elif action ==0:
            return
        else:
            print("ERROR")


#order goes 
# 1.check collision
# 2. move 
# 3. update
class Pong:
    def __init__(self):
        self.p1 = Paddle()
        self.p2 = Paddle()
        self.p1.set_one()
        self.p2.set_two()
        self.ball = Ball()

    def col_recs(self, paddle):
        collision = False
        if ((self.ball.x < paddle.x + PADDLE_WIDTH) and (self.ball.x + BALL_SIZE) > paddle.x) and(self.ball.y < (paddle.y + PADDLE_HEIGHT) and (self.ball.y + BALL_SIZE) > paddle.y):
            collision = True
        return collision 

    def check_col(self):
        if (self.ball.x <= BORDER_X or self.ball.x + BALL_SIZE >= BORDER_X + BORDER_WIDTH):
            return True
        if (self.ball.y + BALL_SIZE >= BORDER_Y + BORDER_HEIGHT or self.ball.y <= BORDER_Y):
            self.ball.v_y*=-1
            return False
        if self.col_recs(self.p1):
            relative_intersect_y = (self.p1.y + (PADDLE_HEIGHT / 2)) - (self.ball.y + (BALL_SIZE / 2))
            normalized_relative_intersect_y = relative_intersect_y / (PADDLE_HEIGHT / 2)
            bounceAngle = normalized_relative_intersect_y * MAX_BOUNCE_ANGLE
            speed = math.sqrt(self.ball.v_x * self.ball.v_x + self.ball.v_y * self.ball.v_y) 
            self.ball.v_x = speed * math.cos(bounceAngle)
            self.ball.v_y = speed * -math.sin(bounceAngle)
            return False
        if (self.col_recs(self.p2)):
            relative_intersect_y = (self.p2.y + (PADDLE_HEIGHT / 2)) - (self.ball.y + (BALL_SIZE / 2))
            normalized_relative_intersect_y = relative_intersect_y / (PADDLE_HEIGHT / 2)
            bounceAngle = normalized_relative_intersect_y * MAX_BOUNCE_ANGLE
            speed = math.sqrt(self.ball.v_x * self.ball.v_x + self.ball.v_y * self.ball.v_y) 
            self.ball.v_x = -speed * math.cos(bounceAngle)
            self.ball.v_y = speed * -math.sin(bounceAngle)
            return False
        return False

    def move(self, action1, action2):
        over = self.check_col()
        self.p1.move(action1)
        self.p2.move(action2)
        self.ball.move()
        #observation, reward, done, info
        return over

    def get_state1(self):
        return np.array([self.ball.x, self.ball.y, self.p1.x,self.p1.y,self.p2.x,self.p2.y]).astype(np.float32)
    
    def get_state2(self):
        return np.array([self.ball.x, self.ball.y, self.p2.x,self.p2.y,self.p1.x,self.p1.y]).astype(np.float32)

    def get_reward1(self):
        if self.ball.x < MID_X:
            return -1
        return 1
    def get_reward2(self):
        if self.ball.x < MID_X:
            return 1
        return -1

    def reset(self):
        self.p1.set_one()
        self.p2.set_two()
        self.ball.reset()

