cmake_minimum_required(VERSION 3.15)
project(EmotionPlaylist VERSION 1.0.0 LANGUAGES CXX)

# Set C++ standard
set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)
set(CMAKE_CXX_EXTENSIONS OFF)

# Add compile options
if(MSVC)
    add_compile_options(/W4)
else()
    add_compile_options(-Wall -Wextra -Wpedantic)
endif()

# Include directories
include_directories(${CMAKE_SOURCE_DIR}/include)

# Source files
set(SOURCES
    src/playlist.cpp
    src/main.cpp
)

# Create executable
add_executable(emotion_playlist ${SOURCES})

# Optional: Enable testing
option(BUILD_TESTS "Build tests" OFF)

if(BUILD_TESTS)
    enable_testing()
    find_package(GTest REQUIRED)
    
    add_executable(run_tests
        tests/test_playlist.cpp
        src/playlist.cpp
    )
    
    target_link_libraries(run_tests GTest::GTest GTest::Main)
    
    add_test(NAME PlaylistTests COMMAND run_tests)
endif()

# Installation
install(TARGETS emotion_playlist
    RUNTIME DESTINATION bin
)

# Print configuration
message(STATUS "C++ Standard: ${CMAKE_CXX_STANDARD}")
message(STATUS "Build Type: ${CMAKE_BUILD_TYPE}")
message(STATUS "Build Tests: ${BUILD_TESTS}")