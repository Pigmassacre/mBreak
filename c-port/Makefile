# Compiler and flags
CC = gcc
CFLAGS = -Wall -Wextra -O2
INCLUDES = -I./include -I$(RAYLIB_PATH)/include
LDFLAGS = -L$(RAYLIB_PATH)/lib
LDLIBS = -lraylib -lopengl32 -lgdi32 -lwinmm -pthread

# Directories
SRC_DIR = src
OBJ_DIR = obj
BIN_DIR = bin

# Files
SRC_FILES = $(wildcard $(SRC_DIR)/*.c)
OBJ_FILES = $(patsubst $(SRC_DIR)/%.c, $(OBJ_DIR)/%.o, $(SRC_FILES))
EXECUTABLE = $(BIN_DIR)/mbreak

# Raylib path (update this to match your Raylib installation)
RAYLIB_PATH = ./raylib-5.5_win64_msvc16

# Default target
all: directories $(EXECUTABLE)

# Create directories if they don't exist
directories:
	if not exist $(OBJ_DIR) mkdir $(OBJ_DIR)
	if not exist $(BIN_DIR) mkdir $(BIN_DIR)

# Link the executable
$(EXECUTABLE): $(OBJ_FILES)
	$(CC) $(CFLAGS) $^ -o $@ $(LDFLAGS) $(LDLIBS)

# Compile source files
$(OBJ_DIR)/%.o: $(SRC_DIR)/%.c
	$(CC) $(CFLAGS) $(INCLUDES) -c $< -o $@

# Run the game
run: all
	$(EXECUTABLE)

# Clean up
clean:
	if exist $(OBJ_DIR) rmdir /s /q $(OBJ_DIR)
	if exist $(BIN_DIR) rmdir /s /q $(BIN_DIR)

# Phony targets
.PHONY: all clean run directories 