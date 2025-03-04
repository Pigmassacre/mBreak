# mBreak Game Architecture Overview

## Project Structure

The game is organized into several key directories:

- `screens/`: Contains all game screens and menus
- `objects/`: Contains game entities and mechanics
- `res/`: Resource files
- `settings/`: Configuration and settings management
- `fonts/`: Font resources
- `libs/`: Library dependencies
- `gui/`: GUI components

## Core Components

### Main Game (mBreak.py)
The entry point of the game that handles:
- PyGame initialization
- Display setup and configuration
- Input device initialization (keyboard, joystick)
- Camera system setup
- Game flow initialization (starting with splash screen)

### Screen Management
The game uses a screen-based architecture where each screen (`screens/`) represents a different game state:
- `splash.py`: Initial loading screen
- `mainmenu.py`: Main menu interface
- `game.py`: Main gameplay screen
- `preparemenu.py`: Pre-game setup
- `gameover.py`: Game over state
- Multiple menu screens (options, graphics, sound, help, etc.)

### Game Objects
Core game entities (`objects/`) include:
- `player.py`: Player management and state
- `ball.py`: Ball physics and behavior
- `paddle.py`: Paddle mechanics and controls
- `blocks/`: Various block types and behaviors
- `attacks/`: Combat and special move systems
- `effects/`: Visual effects and particles
- `powerups/`: Power-up items and mechanics

### Technical Features
- Double buffering for smooth rendering
- Hardware acceleration support
- Fullscreen and windowed mode support
- Joystick/gamepad support
- Configurable settings system
- Camera system for level management

## Game Flow
1. Game initializes through `mBreak.py`
2. Loads configuration from `settings/`
3. Displays splash screen
4. Transitions to main menu
5. Player can navigate to various game modes or options
6. Main gameplay loop runs in `game.py`
7. Game state transitions handled by screen manager

## Key Systems

### Input System
- Keyboard support
- Joystick/gamepad integration
- Event filtering for performance
- Configurable controls

### Graphics System
- Resolution management
- Scaling support
- Fullscreen/windowed modes
- Hardware acceleration
- Particle effects
- Visual feedback systems

### Physics
- Ball movement and collision
- Paddle physics
- Projectile systems
- Trajectory calculations

### Audio
- Sound effect management
- Music system
- Volume controls
- Audio settings

This document provides a high-level overview of the game's architecture. Detailed specifications for each component are provided in separate documents. 