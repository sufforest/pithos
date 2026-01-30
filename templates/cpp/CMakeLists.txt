cmake_minimum_required(VERSION 3.14)

# Project Name (change this!)
project(my_experiment CXX)

set(CMAKE_CXX_STANDARD 20)
set(CMAKE_CXX_STANDARD_REQUIRED ON)

# --- Dependencies (FetchContent) ---
include(FetchContent)

# Example: fmt library
# FetchContent_Declare(
#   fmt
#   GIT_REPOSITORY https://github.com/fmtlib/fmt.git
#   GIT_TAG        10.1.1
# )
# FetchContent_MakeAvailable(fmt)

# --- Targets ---
add_executable(app main.cpp)

# Link dependencies
# target_link_libraries(app PRIVATE fmt::fmt)
