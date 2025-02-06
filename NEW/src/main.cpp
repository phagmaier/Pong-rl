#include "raylib.h"
#include <iostream>
#include <vector>
#include <math.h>
#include <random>

constexpr float ballSpeed = 20;
constexpr float paddle_height=200;
constexpr int move_size = 10;
constexpr float ball_size = 30;
constexpr float max_bounce_angle = M_PI / 4.0f;
//constexpr float max_bounce_angle = 5*M_PI/12;

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

void move_paddle(Rectangle &paddle, int move, Rectangle &border){
  if (!move){
    return;
  }
  if (move == 1){
    if ((paddle.y - move_size) >= border.y){
      paddle.y-=move_size;
    }
    return;
  }
  else if(move == -1){
    if ((paddle.y + move_size) >= (border.y+border.height)){
      paddle.y+=move_size;
    }
  }
  else{
    std::cerr << "THIS SHOULD NEVER PRINT ENTERED INVALID MOVE\n";
  }
}

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

void reset_paddles(Rectangle &p1, Rectangle &p2, const Rectangle &border, float mid_y){
  const int x_padding = 50;
  const int width = 20;
  mid_y -= (paddle_height/2.0f)-10;
  p1 = {border.x+x_padding,mid_y,width,paddle_height};
  float p2_x = border.x + border.width - width - x_padding;
  p2 = {p2_x,mid_y,width,paddle_height};
}

void draw_paddles(const Rectangle &p1, const Rectangle &p2){
  DrawRectangleRec(p1,WHITE);
  DrawRectangleRec(p2,WHITE);
}




void paddle_hit(const Rectangle &paddle, Ball &ball) {
    float relative_intersect_y = (paddle.y + (paddle_height / 2)) - (ball.rec.y + (ball_size / 2));
    float normalized_relative_intersect_y = relative_intersect_y / (paddle_height / 2);
    //float max_bounce_angle = M_PI / 4.0f; // 45 degrees

    float bounceAngle = normalized_relative_intersect_y * max_bounce_angle;
    
    float speed = sqrt(ball.v_x * ball.v_x + ball.v_y * ball.v_y); // Maintain ball speed
    float direction = (ball.rec.x < paddle.x) ? 1.0f : -1.0f; // Left paddle sends it right, right paddle sends it left

    ball.v_x = direction * speed * cos(bounceAngle);
    ball.v_y = speed * -sin(bounceAngle);
}


bool check_coll(Ball &ball, const Rectangle &p1, const Rectangle &p2, const Rectangle &border){
  float x = ball.rec.x;
  float y = ball.rec.y;
 
  if (x <= border.x || x+ball_size >= border.x+border.width){
    //ball.v_x*=-1;//temp
    return true;
  }
  if (y+ball.rec.height >= border.y + border.height || y <= border.y){
    ball.v_y*=-1;
    return false;
  }

//if (x <= p1.x+p1.width && x>= p1.x && y >= p1.y && y <= p1.y+p1.height){
  if (CheckCollisionRecs(p1,ball.rec)){
    float relative_intersect_y = (p1.y + (paddle_height / 2)) - (ball.rec.y + (ball_size / 2));
    float normalized_relative_intersect_y = relative_intersect_y / (paddle_height / 2);
    float bounceAngle = normalized_relative_intersect_y * max_bounce_angle;
    float speed = sqrt(ball.v_x * ball.v_x + ball.v_y * ball.v_y); // Maintain ball speed
    ball.v_x = speed * cos(bounceAngle);
    ball.v_y = speed * -sin(bounceAngle);
    return false;
  }
//  if (x + ball.rec.width >= p2.x && x<=p2.x-p2.width && y >= p2.y && y <= p2.y+p2.height){
  if (CheckCollisionRecs(p2,ball.rec)){
    float relative_intersect_y = (p2.y + (paddle_height / 2)) - (ball.rec.y + (ball_size / 2));
    float normalized_relative_intersect_y = relative_intersect_y / (paddle_height / 2);
    float bounceAngle = normalized_relative_intersect_y * max_bounce_angle;
    float speed = sqrt(ball.v_x * ball.v_x + ball.v_y * ball.v_y); // Maintain ball speed
    ball.v_x = -1*speed * cos(bounceAngle);
    ball.v_y = speed * -sin(bounceAngle);

    return false;
  }
  return false;
}

void print_border(const Rectangle &border){
  std::cout << "BORDER\n";
  std::cout << "-----------------\n";
  std::cout <<"X "<<border.x << " Y: " << border.y;
  std::cout << " WIDTH: " << border.width;
  std::cout << " HEIGHT: " << border.height << "\n";
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
  Ball ball(MID_X,MID_Y);
  int score1 =0;
  int score2 =0;
  std::string str_score1 = "0";
  std::string str_score2 = "0";
  constexpr int score1_x = MID_X-100;
  constexpr int score2_x = MID_X+100;
  constexpr int score_y= Border.y + 50;
  reset_paddles(p1,p2,Border,MID_Y);
  print_border(Border);
  InitWindow(WIDTH, HEIGHT, "PONG (REINFORCEMENT LEARNING)");
  SetTargetFPS(60); 

  while (!WindowShouldClose()){
    if (IsKeyDown(KEY_UP)) p2.y = p2.y -move_size >= MIN_Y ? p2.y-move_size : MIN_Y;
    
    if (IsKeyDown(KEY_DOWN)) p2.y = p2.y + paddle_height + move_size <= MAX_Y ? p2.y+move_size : MAX_Y - paddle_height;

    BeginDrawing();

    ClearBackground(LIGHTGRAY);
    

    //DrawText("Congrats! You created your first window!", 190, 200, 20, LIGHTGRAY);
    DrawRectangleRec(Border,BLACK);
    draw_midlines(midLines);
    draw_paddles(p1,p2);
    //Ball &ball, const Rectangle &p1, const Rectangle &p2, const Rectangle &border){
    game_over = check_coll(ball,p1,p2,Border);
    ball.move();
    DrawRectangleRec(ball.rec,RED);
    DrawText(str_score1.c_str(), score1_x,score_y,50,GOLD);
    DrawText(str_score2.c_str(), score2_x,score_y,50,GOLD);

    EndDrawing();

    if (game_over){
      if (ball.rec.x < MID_X){
        ++score2;
        str_score2 = std::to_string(score2);
      }
      else{
        ++score1;
        str_score1 = std::to_string(score1);
      }
      if (score1 == 10 || score2 == 10){
        bool stop = false;
        while(!stop){
          BeginDrawing();
          ClearBackground(BLACK);
          DrawRectangleLinesEx(RESET,10,WHITE);
          DrawText("RESET", RESET.x+75,RESET.y+100,100,RED);
          EndDrawing();
          if (IsMouseButtonPressed(MOUSE_BUTTON_LEFT)){
            Vector2 mouse = GetMousePosition();
            stop = (CheckCollisionPointRec(mouse, RESET));
          }
        }
        score1=0;
        score2=0;
        str_score1="0";
        str_score2="0";
      }
      ball.reset();
      reset_paddles(p1,p2,Border,MID_Y);
      
      game_over=false;
    } 
  }
  CloseWindow(); 

  return 0;
} 
        
