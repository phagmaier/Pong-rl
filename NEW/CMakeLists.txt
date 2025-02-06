cmake_minimum_required(VERSION 3.5)
project(Project)

set(CMAKE_CXX_STANDARD 14)
set(CMAKE_CXX_STANDARD_REQUIRED ON)

find_package(raylib REQUIRED)

# Enable maximum optimization
set(CMAKE_CXX_FLAGS "${CMAKE_CXX_FLAGS} -O3 -march=native -flto -ffast-math -fno-math-errno")

set(SOURCES
    src/main.cpp
)

add_executable(runme ${SOURCES})
target_link_libraries(runme raylib)

