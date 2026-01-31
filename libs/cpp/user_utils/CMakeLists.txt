cmake_minimum_required(VERSION 3.14)
project(user_utils CXX)

add_library(user_utils utils.cpp)
target_include_directories(user_utils PUBLIC .)
