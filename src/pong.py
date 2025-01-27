import random
import numpy as np


class Ball:
    def __init__(self, mid_y,mid_x):
        self.x = random.randint(mid_x-200, mid_x+200)
        self.y = random.randint(mid_y-200, mid_y+200)
        self.v_x = 4
        self.v_y = 4
        self.size = 20
        self.width = self.size
        self.height = self.size
        tmp = random.randint(0,1)
        if (tmp >0):
            self.vx = -4
        tmp = random.randint(0,1)
        if (tmp >0):
            self.vy = -4
    def move(self):
        self.x+=self.v_x
        self.y += self.v_y
    def hit_paddle(self):
        self.v_x *=-1
    def hit_wall(self):
        self.v_y *=-1

class Paddle:
    def __init__(self, border_x,border_width, border_y, border_height, p1):
        x_offset = 20
        y_offset = (border_y+border_height)/2
        self.height = 100
        self.width = 10

        if (p1):
            self.x = border_x+ x_offset
            self.y = y_offset
        else:
            self.x = border_x + border_width - x_offset - self.width
            self.y = y_offset

        
class Pong:
    def __init__(self):
        self.b_w = 800
        self.b_h = 600
        self.border_size=10
        self.border_x = 50
        self.border_y = 60
        self.mid_x = (self.border_x+self.b_w)/2
        self.min_y = self.border_y
        self.max_y = self.border_y + self.b_h
        self.p1 = Paddle(self.border_x,self.b_w,self.border_y,self.b_h,True)
        self.p2 = Paddle(self.border_x,self.b_w,self.border_y,self.b_h,False)
        self.move_ammount = 4
        #def __init__(self, mid_y,mid_x):
        self.ball = Ball(self.max_y/2,self.mid_x)

    def get_state(self):
        #return np.array([[self.ball.x,self.ball.y],[self.p1.x,self.p1.y],[self.p2.x,self.p2.y]]) 
        return np.array([np.array([self.ball.x, self.ball.y]), 
                         np.array([self.p1.x, self.p1.y]), 
                         np.array([self.p2.x, self.p2.y])])


    '''
    HERE IS HOW RAYLIB IMPLIMENTS THE COLLISIONS:
    bool CheckCollisionRecs(Rectangle rec1, Rectangle rec2)
    {
        bool collision = false;

        if ((rec1.x < (rec2.x + rec2.width) && (rec1.x + rec1.width) > rec2.x) &&
            (rec1.y < (rec2.y + rec2.height) && (rec1.y + rec1.height) > rec2.y)) collision = true;

        return collision;
    }
    '''

    def CheckCollisionRecs(self, rec1, rec2):
        if rec1.x < rec2.x + rec2.width and (rec1.x + rec1.width) > rec2.x and rec1.y < (rec2.y + rec2.height) and (rec1.y + rec1.height) > rec2.y:
            return True

        return False

    def check_col(self):
        if self.ball.x <= self.border_x + self.border_size or self.ball.x + self.ball.size >= self.border_x + self.b_w:
            self.ball.hit_paddle()
            return True
        if self.ball.y + self.ball.size >= self.border_y + self.b_h - self.border_size or self.ball.y <= self.border_y + self.border_size:
            self.ball.hit_wall()
            return False
        #need to check now if it collides with 
        #the paddle which may be a bitch
        return False
    
    '''
    need to impliment checks to make sure you don't move out of range
    '''
    def move_p1(self, move):
        #nothing
        if move == 0:
            return
        if move == 1 and self.p1.y+4 <= self.max_y:
            self.p1.y +=self.move_ammount
        elif move == -1 and self.p1.y-4 >= self.border_y:
            self.p1.y-=self.move_ammount


    def move_p2(self, move):
        #nothing
        if move == 0:
            return
        if move == 1 and self.p2.y+4 <= self.max_y:
            self.p2.y +=self.move_ammount
        elif move == -1 and self.p2.y-4 >= self.border_y:
            self.p2.y-=self.move_ammount

    
    def run(self):
        pass

