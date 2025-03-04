cmake_minimum_required(VERSION 3.10)
project(mBreak C)

# Set C standard
set(CMAKE_C_STANDARD 99)
set(CMAKE_C_STANDARD_REQUIRED ON)

# Output directories
set(CMAKE_RUNTIME_OUTPUT_DIRECTORY ${CMAKE_BINARY_DIR}/bin)
set(CMAKE_LIBRARY_OUTPUT_DIRECTORY ${CMAKE_BINARY_DIR}/lib)
set(CMAKE_ARCHIVE_OUTPUT_DIRECTORY ${CMAKE_BINARY_DIR}/lib)

# Add source files
file(GLOB_RECURSE SOURCES "src/*.c")
file(GLOB_RECURSE HEADERS "include/*.h")

# Create executable
add_executable(mbreak ${SOURCES} ${HEADERS})

# Include directories
target_include_directories(mbreak PRIVATE include)

# Find and link Raylib
# Option 1: Using find_package if you have Raylib installed system-wide or with a proper CMake config
option(USE_SYSTEM_RAYLIB "Use system-installed Raylib" OFF)

if(USE_SYSTEM_RAYLIB)
    find_package(raylib REQUIRED)
    target_link_libraries(mbreak raylib)
else()
    # Option 2: Using a local Raylib installation
    # Define Raylib path (change this to match your Raylib installation)
    set(RAYLIB_PATH "${CMAKE_CURRENT_SOURCE_DIR}/raylib-5.5_win64_msvc16" CACHE PATH "Path to Raylib installation")
    
    # Include Raylib headers
    target_include_directories(mbreak PRIVATE ${RAYLIB_PATH}/include)
    
    # Link with Raylib
    if(WIN32)
        target_link_directories(mbreak PRIVATE ${RAYLIB_PATH}/lib)
        target_link_libraries(mbreak raylib opengl32 gdi32 winmm)
    else()
        target_link_directories(mbreak PRIVATE ${RAYLIB_PATH}/lib)
        target_link_libraries(mbreak raylib GL m pthread dl rt X11)
    endif()
endif()

# Install rule
install(TARGETS mbreak DESTINATION bin)

# Custom targets
add_custom_target(run
    COMMAND ${CMAKE_RUNTIME_OUTPUT_DIRECTORY}/mbreak
    DEPENDS mbreak
    WORKING_DIRECTORY ${CMAKE_RUNTIME_OUTPUT_DIRECTORY}
)

# Copy resources to build directory
if(MSVC)
    # For multi-configuration generators like Visual Studio, we need to copy to both Debug and Release directories
    add_custom_command(TARGET mbreak POST_BUILD
        COMMAND ${CMAKE_COMMAND} -E copy_directory
        ${CMAKE_CURRENT_SOURCE_DIR}/resources
        $<TARGET_FILE_DIR:mbreak>/resources
        COMMENT "Copying resources to output directory")
else()
    # For single-configuration generators
    file(COPY resources DESTINATION ${CMAKE_RUNTIME_OUTPUT_DIRECTORY})
endif() 