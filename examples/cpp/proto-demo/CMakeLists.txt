cmake_minimum_required(VERSION 3.14)
project(proto_demo CXX)

set(CMAKE_CXX_STANDARD 17)

# --- 1. Find Protobuf & Abseil ---
find_package(Protobuf REQUIRED)
find_package(absl REQUIRED)

# --- 2. Auto-Generate Protobuf Code (Bazel-like) ---
# This generates .pb.cc/.pb.h during build! No manual 'just gen-proto' needed.
# Note: We need to tell CMake where the .proto files are.
# We expect PITHOS_ROOT to be passed by the runner (or set manually)
if(NOT PITHOS_ROOT)
    # Fallback for manual IDE opening (assuming default location)
    get_filename_component(PITHOS_ROOT "${CMAKE_SOURCE_DIR}/../../.." ABSOLUTE)
endif()

include_directories(${CMAKE_CURRENT_BINARY_DIR}) # Where .pb.h will be generated
file(GLOB_RECURSE PROTO_FILES "${PITHOS_ROOT}/idl/*.proto")

protobuf_generate_cpp(PROTO_SRCS PROTO_HDRS ${PROTO_FILES})

# --- 3. Include Shared Lib ---
add_subdirectory(${PITHOS_ROOT}/libs/cpp/user_utils user_utils_build)

# --- 4. Main Target ---
add_executable(app main.cpp ${PROTO_SRCS} ${PROTO_HDRS})

# Link Protobuf, Shared Lib, and Generated Objects
target_link_libraries(app 
    PRIVATE 
    protobuf::libprotobuf
    absl::log_internal_message
    absl::log_internal_check_op
    user_utils
)
