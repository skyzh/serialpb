cmake_minimum_required(VERSION 3.15)
project(serialpb)

set(CMAKE_CXX_STANDARD 14)
find_package(GTest MODULE REQUIRED)
add_executable(main test.cpp BufferProtocol.cpp BufferProtocol.h)
target_link_libraries(main PRIVATE GTest::GTest GTest::Main)
