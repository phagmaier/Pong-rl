#include "raylib.h"
#include <iostream>
#include <random>
#include <string>
#include <fstream>
#include <utility>
#include <vector>

std::random_device rd;
std::mt19937 gen(rd());

int get_random_num(const int min, const int max){
  std::uniform_int_distribution<int> distrib(min,max);
  return distrib(gen);
}

struct Ball{
  Ball(const int mid_y, const int mid_x){
    x = get_random_num(mid_x-200, mid_x+200);
    y = get_random_num(mid_y-200, mid_y+200);
    v_x = get_random_num(0,1) ? 4 : -4;
    v_y = get_random_num(0,1) ? 4 : -4;
    size = 20;
    rec = {(float)x,(float)y,(float)size,(float)size};
  }
  Ball(int x_pos, int y_pos, int v1, int v2){
    x = x_pos;
    y=y_pos;
    v_x = v1;
    v_y = v2;
    size = 20;
    rec = {(float)x,(float)y,(float)size,(float)size};
  }
  int x;
  int y;
  int v_x;
  int v_y;
  int size = 20;
  Rectangle rec;
  inline void hit_paddle(){v_x*=-1;}
  inline void hit_edge(){v_y*=-1;}
  inline void move(){x+=v_x;y+=v_y;rec.x=x;rec.y=y;}
  void reset(const int mid_y, const int mid_x){
    x = get_random_num(mid_x-200, mid_x+200);
    y = get_random_num(mid_y-200, mid_y+200);
    v_x = get_random_num(0,1) ? 2 : -2;
    v_y = get_random_num(0,1) ? 2 : -2;
    rec = {(float)x,(float)y,(float)size,(float)size};
  }
};


bool detect_edge(Ball &ball, Rectangle &p1, Rectangle &p2, const Rectangle &border, const int border_size) {
  // Left and right border collisions (scoring conditions)
  if (ball.x <= border.x + border_size || ball.x + ball.size >= border.x + border.width) {
    //ball.reset(border.y + border.height/2, border.x + border.width/2);
    ball.hit_paddle();
    //return true;
    return false;
  }

  // Top and bottom border bounces
  if (ball.y + ball.size >= border.y + border.height - border_size || ball.y <= border.y + border_size) {
    ball.hit_edge();
    return false;
  }

  // Left paddle collision with more nuanced handling
  if (CheckCollisionRecs(ball.rec, p1)) {
    // Determine collision type and adjust velocity/position
    if (ball.v_x < 0) {  // Ensure ball is moving towards paddle
      ball.hit_paddle();
      // Optional: Add angle variation based on where ball hits paddle
      ball.x = p1.x + p1.width;
    }
    return false;
  }

  // Right paddle collision with similar nuanced handling
  if (CheckCollisionRecs(ball.rec, p2)) {
    if (ball.v_x > 0) {  // Ensure ball is moving towards paddle
      ball.hit_paddle();
      // Optional: Add angle variation based on where ball hits paddle
      ball.x = p2.x - ball.size;
    }
    return false;
  }

  return false;
}
void init_paddles(Rectangle &p1, Rectangle &p2, const Rectangle &border){
  const int x_offset = 20;
  const int y_offset = (border.y+border.height)/2;
  const int paddle_size = 100;
  const int paddle_width = 10;

  p1.x = border.x + x_offset;
  p1.y = y_offset;
  p1.width = paddle_width;
  p1.height = paddle_size;

  p2.x = border.x + border.width - x_offset - paddle_width;
  p2.y = y_offset;
  p2.width = paddle_width;
  p2.height = paddle_size;
}

void draw_dashed_line(const int mid_x, int min_y, const int max_y){
  static const int length = 20;
  static const int offset = 10;
  while (min_y+length < max_y){
    DrawRectangle(mid_x,min_y,10,length, BLACK);
    min_y += length + offset;
  } 
}

void write_file(std::ofstream &outputFile, std::pair<int,int> *balls, int iterations){
  for (int i=0;i<iterations;++i){
    outputFile << balls[i].first << " " << balls[i].second << "\n";
  }
}

struct Six{
  Six(int one, int two, int three, int four, int five, int six) : one(one),two(two),three(three),four(four), five(five), six(six){}
  Six() : one(0),two(0),three(0),four(0), five(0), six(0){}
  Six(int *nums){
    one = nums[0];
    two = nums[1];
    three = nums[2];
    four = nums[3];
    five = nums[4];
    six = nums[5];
  }
  int one;
  int two;
  int three;
  int four;
  int five;
  int six;
};

std::vector<Six>read_file(){
  std::vector<Six> vec;
  std::ifstream file("sample_game.txt"); 
  if (file.is_open()) {
    std::string line;
    while (std::getline(file, line)) {
      //std::cout << "READING A LINE\n";
      int nums[6];
      int count =0;
      std::string str = "";
      for (char c: line){
        if (c == ' '){
          //std::cout << str << "\n";
          nums[count] = std::stoi(str);
          ++count;
          str = "";

        }
        else{
          str += c;
        }
      }
      if (count == 5){
        //std::cout << "THIS BETTER RUN\n";
        nums[count] = std::stoi(str);
        vec.emplace_back(Six(nums));
      }
      //vec.push_back({std::stoi(str1),std::stoi(str2)});
    }
    file.close();
  } 
  else {
    std::cerr << "Error: Unable to open file." << std::endl;
  }
  return vec;
}


int main(void){
  std::vector<Six> vec = read_file();
  const int W = 900;
  const int H =700; 
  const int B_W = W-100;
  const int B_H = H-100;
  const int border_size = 10;

  const Rectangle border = {50,60,B_W,B_H};

  const int mid_x = (border.x+border.width)/2;
  const int min_y = (border.y);
  const int max_y = border.y + border.height;
  Rectangle p1;
  Rectangle p2;
  Ball ball = Ball(mid_x,max_y/2);
  std::cout << "BALL INITIAL POS: " << ball.x << " " << ball.y << "\n";
  std::cout << "BALL INITIAL VS's: " << ball.v_x << " " << ball.v_y << "\n";
  //Ball ball = Ball(mid_x, max_y/2,1,0);
  init_paddles(p1,p2,border);

  int score;
  int score_x = 100;
  int score_y = 5;
  std::string str= "SCORE: ";
  InitWindow(W, H, "PONG");
  SetTargetFPS(60);
  
  int count = 0;
  while (!WindowShouldClose() && count < vec.size()){
    ball.x = vec[count].one;
    ball.y = vec[count].two;
    ball.rec.x = ball.x;
    ball.rec.y = ball.y;
    p1.x = vec[count].three;
    p1.y = vec[count].four;
    p2.x = vec[count].five;
    p2.y = vec[count].six;

    BeginDrawing();

    ClearBackground(RAYWHITE);
    DrawRectangleLinesEx(border,border_size,BLACK);
    DrawRectangleRec(p1,BLACK);
    DrawRectangleRec(p2,BLACK);
    draw_dashed_line(mid_x, min_y, max_y);
//Ball &ball, Rectangle &p1, Rectangle &p2, Rectangle &border, const int border_size){
    //detect_edge(ball, p1, p2,border,border_size);
    //ball.move();
    //DrawRectangle(ball.x,ball.y,ball.size,ball.size, RED);
    DrawRectangleRec(ball.rec,RED);
    std::string tmp = str + std::to_string(score);
    DrawText(tmp.c_str(), score_x,score_y, 50, RED);
    
    EndDrawing();
    ++count;
  }

  CloseWindow(); 

  return 0;
}
        
