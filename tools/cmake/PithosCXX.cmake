# tools/cmake/PithosCXX.cmake
# Standard Configuration for all Pithos C++ Projects

# 1. Standard Settings
set(CMAKE_CXX_STANDARD 20)
set(CMAKE_CXX_STANDARD_REQUIRED ON)
set(CMAKE_EXPORT_COMPILE_COMMANDS ON)

# 2. MacOS SDK Fix (The "Cleaner" detection)
if(APPLE AND NOT CMAKE_OSX_SYSROOT)
    execute_process(COMMAND xcrun --show-sdk-path 
                    OUTPUT_VARIABLE CMAKE_OSX_SYSROOT 
                    OUTPUT_STRIP_TRAILING_WHITESPACE)
    message(STATUS "Auto-detected macOS SDK: ${CMAKE_OSX_SYSROOT}")
    set(CMAKE_OSX_SYSROOT ${CMAKE_OSX_SYSROOT} CACHE PATH "Sysroot" FORCE)
endif()

# 3. Hermetic Dependencies (FetchContent)
# This removes the need for 'brew install protobuf'
include(FetchContent)

# Helper to load Protobuf/Abseil only if needed
macro(pithos_load_protobuf)
    if(NOT TARGET protobuf::libprotobuf)
        message(STATUS "Fetching Protobuf (Hermetic)...")
        set(protobuf_BUILD_TESTS OFF CACHE BOOL "" FORCE)
        set(protobuf_BUILD_PROTOC_BINARIES ON CACHE BOOL "" FORCE)
        set(ABSL_PROPAGATE_CXX_STD ON)
        
        FetchContent_Declare(
            protobuf
            GIT_REPOSITORY https://github.com/protocolbuffers/protobuf.git
            GIT_TAG        v25.1
        )
        FetchContent_MakeAvailable(protobuf)
    endif()
endmacro()
