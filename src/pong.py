import random
import numpy as np

class Ball:
    def __init__(self, mid_y, mid_x):
        self.x = random.randint(int(mid_x-200), int(mid_x+200))
        self.y = random.randint(int(mid_y-200), int(mid_y+200))
        self.v_x = 4  # Use only v_x, not vx
        self.v_y = 4  # Use only v_y, not vy
        self.size = 20
        self.width = self.size
        self.height = self.size
        
    def move(self):
        self.x += self.v_x
        self.y += self.v_y
        
    def hit_paddle(self):
        self.v_x *= -1
        
    def hit_wall(self):
        self.v_y *= -1

class Paddle:
    def __init__(self, border_x, border_width, border_y, border_height, p1):
        x_offset = 20
        y_offset = (border_y + border_height)/2
        self.height = 100
        self.width = 10

        if p1:
            self.x = border_x + x_offset
            self.y = y_offset
        else:
            self.x = border_x + border_width - x_offset - self.width
            self.y = y_offset

class Pong:
    def __init__(self):
        self.W = 900  # Match C++ window size
        self.H = 700
        self.b_w = self.W - 100  # Match C++ border size
        self.b_h = self.H - 100
        self.border_size = 10
        self.border_x = 50
        self.border_y = 60
        self.mid_x = (self.border_x + self.b_w)/2
        self.min_y = self.border_y
        self.max_y = self.border_y + self.b_h
        self.p1 = Paddle(self.border_x, self.b_w, self.border_y, self.b_h, True)
        self.p2 = Paddle(self.border_x, self.b_w, self.border_y, self.b_h, False)
        self.move_ammount = 4
        self.ball = Ball(self.max_y/2, self.mid_x)
        self.balls = []
        
    def update_arrs(self):
        self.balls.append((self.ball.x, self.ball.y))

    def write_to_file(self):
        with open('pythonOutputs.txt', 'w') as file:
            for ball_pos in self.balls:
                file.write(f"{ball_pos[0]} {ball_pos[1]}\n")

    def get_state(self):
        return np.array([np.array([self.ball.x, self.ball.y]), 
                        np.array([self.p1.x, self.p1.y]), 
                        np.array([self.p2.x, self.p2.y])])

    def CheckCollisionRecs(self, rec1, rec2):
        if (rec1.x < rec2.x + rec2.width and 
            (rec1.x + rec1.width) > rec2.x and 
            rec1.y < (rec2.y + rec2.height) and 
            (rec1.y + rec1.height) > rec2.y):
            return True
        return False

    def check_col(self):
        if self.ball.x <= self.border_x + self.border_size or self.ball.x + self.ball.size >= self.border_x + self.b_w:
            self.ball.hit_paddle()
            return False
            
        if self.ball.y + self.ball.size >= self.border_y + self.b_h - self.border_size or self.ball.y <= self.border_y + self.border_size:
            self.ball.hit_wall()
            return False
            
        if self.CheckCollisionRecs(self.ball, self.p1):
            if self.ball.v_x < 0:  # Use v_x instead of vx
                self.ball.hit_paddle()
                self.ball.x = self.p1.x + self.p1.width
            return False

        if self.CheckCollisionRecs(self.ball, self.p2):
            if self.ball.v_x > 0:  # Use v_x instead of vx
                self.ball.hit_paddle()
                self.ball.x = self.p2.x - self.ball.size
            return False
        return False
    
    def move_p1(self, move):
        if move == 0:
            return
        if move == 1 and self.p1.y + 4 <= self.max_y:
            self.p1.y += self.move_ammount
        elif move == -1 and self.p1.y - 4 >= self.border_y:
            self.p1.y -= self.move_ammount

    def move_p2(self, move):
        if move == 0:
            return
        if move == 1 and self.p2.y + 4 <= self.max_y:
            self.p2.y += self.move_ammount
        elif move == -1 and self.p2.y - 4 >= self.border_y:
            self.p2.y -= self.move_ammount
    
    def run(self):
        iterations = 250
        print(f"BALL INITIAL POS: {self.ball.x} {self.ball.y}")
        print(f"BALL INITIAL VS's: {self.ball.v_x} {self.ball.v_y}")
        
        # Match C++ initial conditions exactly
        self.ball.x = 319
        self.ball.y = 324
        self.ball.v_x = 4
        self.ball.v_y = 4
        
        for _ in range(iterations):
            self.update_arrs()
            self.check_col()
            self.ball.move()
            
        print(f"BALL END: {self.ball.x} {self.ball.y}")
        self.write_to_file()

if __name__ == '__main__':
    pong = Pong()
    pong.run()
