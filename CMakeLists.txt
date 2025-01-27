cmake_minimum_required(VERSION 3.5)
project(Project)
set(CMAKE_CXX_STANDARD 17)
find_package(raylib REQUIRED)
set(CMAKE_CXX_STANDARD_REQUIRED ON)
set(SOURCES
src/main.cpp
)
add_executable(runme ${SOURCES})
target_link_libraries(runme raylib)
