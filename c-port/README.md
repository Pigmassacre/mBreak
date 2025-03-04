# mBreak C Port

This is a C port of the mBreak game, originally written in Python using Pygame. The C port uses Raylib for rendering and game functionality.

## Features

- Breakout-style gameplay
- Multiple block types (normal, hard, invincible, explosive, power-up)
- Simple physics with ball bouncing mechanics
- Screen management system for different game states
- Entity component system for game objects
- User interface with keyboard and mouse controls
- Basic collision detection and handling

## Requirements

- C compiler (GCC recommended)
- Raylib library (https://www.raylib.com/)
- Windows OS (for the current Makefile, can be adapted for other platforms)

## Building

1. Install Raylib (https://github.com/raysan5/raylib/wiki/Working-on-Windows)
2. Update the `RAYLIB_PATH` in the Makefile to match your Raylib installation
3. Open a command prompt in the project directory
4. Run `make` to build the project

```
cd c-port
make
```

## Running

After building, you can run the game with:

```
make run
```

Or directly execute the binary:

```
bin/mbreak
```

## Controls

### Main Menu

- **Up/Down Arrow Keys**: Navigate menu options
- **Enter/Space**: Select menu option
- **Mouse**: Click on menu options

### Gameplay

- **A/D or Left/Right Arrow Keys**: Move paddle left/right
- **Space**: Launch ball from paddle
- **P**: Pause game
- **Esc**: Exit to main menu

## Project Structure

- `include/`: Header files
  - `screens.h`: Screen management
  - `entity.h`: Entity system
  - `paddle.h`: Paddle entity
  - `ball.h`: Ball entity
  - `block.h`: Block entity
- `src/`: Source files
  - `main.c`: Main entry point
  - `screens.c`: Screen management implementation
  - `entity.c`: Entity system implementation
  - `paddle.c`: Paddle implementation
  - `ball.c`: Ball implementation
  - `block.c`: Block implementation
  - `gameplay.c`: Gameplay screen
  - `mainmenu.c`: Main menu screen
  - `splash.c`: Splash screen
- `resources/`: Game resources (to be added)

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgments

- Original mBreak game developers
- Raylib library (https://www.raylib.com/) 