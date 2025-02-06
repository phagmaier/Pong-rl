#include "raylib.h"
#include <iostream>
#include <vector>
#include <math.h>
#include <random>
#include <fstream>
#include <string>
#include <utility>


constexpr float ballSpeed = 20;
constexpr float paddle_height=200;
constexpr int move_size = 10;
constexpr float ball_size = 30;
constexpr float max_bounce_angle = M_PI / 4.0f;
//constexpr float max_bounce_angle = 5*M_PI/12;


void reset_paddles(Rectangle &p1, Rectangle &p2, const Rectangle &border, float mid_y){
  const int x_padding = 50;
  const int width = 20;
  mid_y -= (paddle_height/2.0f)-10;
  p1 = {border.x+x_padding,mid_y,width,paddle_height};
  float p2_x = border.x + border.width - width - x_padding;
  p2 = {p2_x,mid_y,width,paddle_height};
}

std::random_device rd;
std::mt19937 gen(rd());
int get_direction(){
  std::uniform_int_distribution<> distrib(0, 1);
  if (distrib(gen)){
    return ballSpeed;
  }
  else{
    return -ballSpeed;
  }
}

struct Ball{
  Ball(int x, int y){
    mid_x = x-10;
    mid_y = y-10;
    rec.x=x-10;
    rec.y = y-10;
    rec.width=ball_size;
    rec.height=ball_size;
    v_x =get_direction();
    v_y =0.0;
  }
  int mid_x;
  int mid_y;
  Rectangle rec;
  float v_x;
  float v_y;
  void reset(){rec.x=mid_x;rec.y=mid_y;v_x=get_direction();v_y=0.0;}
  void move(){rec.x+=v_x;rec.y+=v_y;}
};


std::vector<Rectangle>make_mid_lines(const int mid, const Rectangle Border){
  std::vector<Rectangle> vec;
  int y = Border.y+20;
  const int limit = (Border.y+Border.height) - 10;
  const int height= 50;
  const int padding = 20;
  const int width = 10;
  while (y+height< limit){
    vec.push_back({static_cast<float>(mid),static_cast<float>(y),width,height});
    y = y + height + padding;
  }
  return vec; 
}

void draw_midlines(const std::vector<Rectangle> &vec){
  for (const Rectangle &rec :vec){
    DrawRectangleRec(rec,WHITE);
  }
}


void draw_paddles(const Rectangle &p1, const Rectangle &p2){
  DrawRectangleRec(p1,WHITE);
  DrawRectangleRec(p2,WHITE);
}

void print_border(const Rectangle &border){
  std::cout << "BORDER\n";
  std::cout << "-----------------\n";
  std::cout <<"X "<<border.x << " Y: " << border.y;
  std::cout << " WIDTH: " << border.width;
  std::cout << " HEIGHT: " << border.height << "\n";
}

//return np.array([self.ball.x, self.ball.y, self.p1.x,self.p1.y,self.p2.x,self.p2.y]).astype(np.float32)
struct Six{
  Six(float *arr){
    ball = {arr[0],arr[1]};
    p1 = {arr[2],arr[3]};
    p2 = {arr[4],arr[5]};
  }
  std::pair<float,float> ball;
  std::pair<float,float> p1;
  std::pair<float,float> p2;
};

Six parse_line(std::string &str){
  float arr[6];
  int count =0;
  std::string tmp = "";
  for (char c: str){
    if (c == ' '){
      arr[count] = std::stof(tmp);
      ++count;
      tmp = "";
    }
    else{
      tmp +=c;
    }
  }
  arr[5] = std::stof(tmp);
  return Six(arr);
}

std::vector<Six> read_file(){
  std::vector<Six> vec;
  std::ifstream file("games.txt");
  std::string line;
  while (std::getline(file, line)) {
    vec.push_back(parse_line(line));
  }
  return vec;
}

int main(void){
  bool game_over = false;
  constexpr int WIDTH = 1200;
  constexpr int HEIGHT = 1000;
  constexpr int PADDING = 20;
  constexpr Rectangle Border = {PADDING,PADDING,WIDTH-(PADDING*2),HEIGHT-(PADDING*2)};
  constexpr int MID_X = (Border.x+Border.width)/2;
  std::cout << "MID X: " << MID_X << "\n";
  constexpr int MID_Y = (Border.y+Border.height)/2;
  std::cout << "MID Y: " << MID_Y << "\n";
  constexpr int MIN_Y = Border.y;
  std::cout << "MIN Y: " << MIN_Y << "\n";
  constexpr int MAX_Y = Border.y + Border.height;
  std::cout << "MAX Y: " << MAX_Y<< "\n";
  constexpr Rectangle RESET = {MID_X-200, MID_Y-150,500,300};
  const std::vector<Rectangle> midLines = make_mid_lines(MID_X, Border);
  Rectangle p1;
  Rectangle p2;
  reset_paddles(p1,p2,Border, MID_Y);
  Ball ball(MID_X,MID_Y);
  int score1 =0;
  int score2 =0;
  std::string str_score1 = "0";
  std::string str_score2 = "0";
  constexpr int score1_x = MID_X-100;
  constexpr int score2_x = MID_X+100;
  constexpr int score_y= Border.y + 50;
  std::vector<Six> vec = read_file();
  unsigned int count = 0;
  print_border(Border);
  InitWindow(WIDTH, HEIGHT, "PONG (REINFORCEMENT LEARNING)");
  SetTargetFPS(60); 
  
  for (Six six : vec){
    ball.rec.x = six.ball.first;
    ball.rec.y = six.ball.second;
    p1.x = six.p1.first;
    p1.y = six.p1.second;
    p2.x = six.p2.first;
    p2.y = six.p2.second;
    BeginDrawing();

    ClearBackground(LIGHTGRAY);
    DrawRectangleRec(Border,BLACK);
    draw_midlines(midLines);
    draw_paddles(p1,p2);
    DrawRectangleRec(ball.rec,RED);

    EndDrawing();
  }
  CloseWindow(); 

  return 0;
} 
        
