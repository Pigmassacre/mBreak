# mBreak Game Architecture Overview

## Project Structure

The game is organized into several key directories:

- `screens/`: Contains all game screens and menus
- `objects/`: Contains game entities and mechanics
- `res/`: Resource files and assets
- `settings/`: Configuration and settings management
- `fonts/`: Font resources
- `libs/`: Library dependencies
- `gui/`: GUI components and menu system

## Current Implementation (Python + Pygame)

### Main Game (mBreak.py)
The entry point of the game that handles:
- PyGame initialization
- Display setup and configuration
- Input device initialization (keyboard, joystick)
- Camera system setup
- Game flow initialization (starting with splash screen)

### Technical Features
- Double buffering for smooth rendering
- Hardware acceleration support
- Fullscreen and windowed mode support
- Joystick/gamepad support
- Configurable settings system
- Camera system for level management

## Core System Design

### Screen Management
The game uses a screen-based architecture where each screen (`screens/`) represents a different game state:
- `splash.py`: Initial loading screen
- `mainmenu.py`: Main menu interface
- `game.py`: Main gameplay screen
- `preparemenu.py`: Pre-game setup
- `gameover.py`: Game over state
- Multiple menu screens (options, graphics, sound, help, etc.)

Each screen is a Python class that handles its own initialization, update, and drawing. 
Screens manage transitions between each other and maintain their own state.

### Game Objects
Core game entities (`objects/`) include:
- `player.py`: Player management and state
- `ball.py`: Ball physics and behavior
- `paddle.py`: Paddle mechanics and controls
- `blocks/`: Various block types and behaviors
- `attacks/`: Combat and special move systems
- `effects/`: Visual effects and particles
- `powerups/`: Power-up items and mechanics

Objects inherit from `pygame.sprite.Sprite` and use Pygame's sprite groups for management and collision detection.

### GUI System
The GUI system (`gui/`) is built using custom classes:
- `menu.py`: Base menu class that handles items and selections
- `item.py`: Base class for menu items
- `textitem.py`: Text-based menu items
- `imageitem.py`: Image-based menu items
- `choiceitem.py`: Selection items
- `transition.py`: Screen transition effects
- Other specialized menu types (gridmenu, listmenu, etc.)

This system is currently tightly coupled with Pygame's rendering and event handling.

### Input System
- Keyboard support with configurable controls
- Joystick/gamepad integration
- Event filtering for performance
- Event handling per screen or object

### Physics System
- Collision detection using Pygame's rect-based system
- Movement using float-precision positions updated via velocity
- Custom collision response handling in each object type
- Simple particle physics

## Game Flow
1. Game initializes through `mBreak.py`
2. Loads configuration from `settings/`
3. Displays splash screen
4. Transitions to main menu
5. Player can navigate to various game modes or options
6. Main gameplay loop runs in `game.py`
7. Game state transitions handled by screen manager

## Port Considerations for C + Raylib

### Architectural Mapping
When porting to C + Raylib, consider these key mappings:

| Pygame Concept | Raylib Equivalent |
|----------------|-------------------|
| `pygame.Surface` | `Texture2D` or `RenderTexture2D` |
| `pygame.Rect` | Custom Rectangle struct with collision functions |
| `pygame.sprite.Sprite` | Custom entity structs with rendering and update functions |
| `pygame.sprite.Group` | Linked list or array of entity pointers |
| `pygame.display.set_mode` | `InitWindow` |
| Event handling | `IsKeyDown`, `IsKeyPressed`, etc. |
| Surface blitting | `DrawTexture`, `DrawTextureRec` |

### Core Components to Implement
1. **Entity Component System**
   - Create base structs for game entities
   - Implement entity management and lifecycle

2. **Screen Management System**
   - Design a screen stack or state machine
   - Implement screen transitions

3. **Resource Management**
   - Asset loading and unloading
   - Texture management system

4. **UI Framework**
   - Implement menu and item system
   - Create event handling for UI elements

5. **Physics and Collision**
   - Port the collision detection system
   - Implement movement and physics calculations

### Memory Management
The Python implementation benefits from automatic garbage collection. In C:
- Explicitly manage memory allocation and deallocation
- Create pool allocators for frequently created/destroyed objects (particles)
- Implement clear ownership hierarchies for objects

### Threading Considerations
The current implementation is single-threaded. When porting:
- Consider asset loading on background threads
- Keep game logic on main thread for simplicity
- Use Raylib's threading utilities where appropriate

## Implementation Strategy
1. Start with core engine components (rendering, input, resources)
2. Implement basic screens and transitions
3. Add entity system and game objects
4. Implement physics and collision
5. Add effects and particles
6. Implement UI system
7. Add audio and polish

This document provides a high-level overview of the game's architecture. Detailed specifications for each component are provided in separate documents. 