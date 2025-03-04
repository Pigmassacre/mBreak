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

Each screen is a Python class that inherits from `scene.py`, which provides:
- A standardized game loop implementation
- Common event handling
- Update and draw method structure
- Transition management between screens
- Music playback control

Screens transition between each other using the `on_exit()` method, where the current screen instantiates the next screen before terminating its own game loop. This creates a stack-like progression through the game states.

### Game Objects
Core game entities (`objects/`) include:
- `player.py`: Player management and state
- `ball.py`: Ball physics and behavior
- `paddle.py`: Paddle mechanics and controls
- `blocks/`: Various block types and behaviors
- `attacks/`: Combat and special move systems
- `effects/`: Visual effects and particles
- `powerups/`: Power-up items and mechanics

Objects inherit from `pygame.sprite.Sprite` and use Pygame's sprite groups for management and collision detection. The sprite groups are managed through a centralized system in `objects/groups.py`, which maintains collections of:
- Active balls
- Paddles for each player
- Blocks for each player
- Various effect elements
- Powerups

### GUI System
The GUI system (`gui/`) is built using custom classes:
- `menu.py`: Base menu class that handles items and selections
- `item.py`: Base class for menu items
- `textitem.py`: Text-based menu items
- `imageitem.py`: Image-based menu items
- `choiceitem.py`: Selection items
- `transition.py`: Screen transition effects
- Other specialized menu types (gridmenu, listmenu, etc.)

The menu system uses a registration system where menus can be made aware of each other to ensure only one menu has a selected item at any time. Menu traversal is managed by the `traversal.py` module, which provides keyboard and gamepad navigation between menu items.

### Input System
- Keyboard support with configurable controls
- Joystick/gamepad integration with button mapping
- Event filtering for performance via `pygame.event.set_allowed()`
- Event handling per screen or object
- Centralized traversal system for navigating menus

### Physics System
The game implements custom physics with several key features:

#### Ball Physics (`ball.py`)
- Float-precision position tracking for smooth movement
- Velocity-based updates scaled by delta time for framerate independence
- Minimum bounce angles to prevent horizontal/vertical "stuck" scenarios
- Stuck detection system that monitors if a ball hasn't moved sufficiently in a time period
- Random angle variation on bounces to increase gameplay variety
- Smash mechanics with speed and damage multipliers
- Trace effects that visualize ball movement paths

#### Collision Detection
- Primary collision detection using Pygame's rect-based system
- Custom collision response handling in each object type
- Edge detection to keep objects within the game area
- Layered collision priorities (paddle vs. ball vs. block)
- Damage calculation based on collision velocity and modifiers

#### Particle System
- Simple particle physics for visual effects
- Time-based lifespan for temporary effects
- Scale and alpha modifications over time
- Velocity and directional control

### Resource Management
Resources are managed through several specialized systems:

#### Graphics Management (`settings/graphics.py`)
- Handles loading and scaling of images
- Manages screen dimensions and scaling
- Controls rendering settings like FPS limits
- Configures fullscreen/windowed modes

#### Sound Management (`settings/sounds.py`)
- Loads and initializes sound effects
- Manages music playback and track selection
- Controls volume settings
- Provides centralized sound playback functions

#### Settings Management (`settings/settings.py`)
- Loads configuration from external files
- Stores game constants and variables
- Manages input mappings and controls
- Provides save/load functionality for user preferences

## Game Flow
1. Game initializes through `mBreak.py`
2. Loads configuration from `settings/`
3. Displays splash screen
4. Transitions to main menu
5. Player can navigate to various game modes or options
6. Main gameplay loop runs in `game.py`
7. Game state transitions handled by screen manager

### Camera System
The camera system (`objects/camera.py`) provides:
- Viewport management for the game world
- Translation between world and screen coordinates
- Shaking effects for impact feedback
- Scaling capabilities for zoom effects
- Screen boundaries to constrain rendering to visible areas

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
| Scene system | State machine with draw/update functions |

### Core Components to Implement
1. **Entity Component System**
   - Create base structs for game entities
   - Implement entity management and lifecycle
   - Port the sprite group functionality of `objects/groups.py`
   - Design memory-efficient containers for entities

2. **Screen Management System**
   - Design a screen stack or state machine
   - Implement screen transitions
   - Port the Scene base class functionality
   - Create a standardized update/draw/event interface

3. **Resource Management**
   - Asset loading and unloading
   - Texture management system
   - Sound management with equivalent functions
   - Settings persistence using file I/O

4. **UI Framework**
   - Implement menu and item system
   - Create event handling for UI elements
   - Port the traversal system for menu navigation
   - Develop equivalent transition effects

5. **Physics and Collision**
   - Port the collision detection system
   - Implement movement and physics calculations
   - Recreate the ball bounce mechanics with angle constraints
   - Design efficient collision group management

6. **Delta Time System**
   - Implement an equivalent to GameClock for frame-independent movement
   - Ensure consistent physics regardless of frame rate
   - Create timing utilities for animations and effects

### Memory Management
The Python implementation benefits from automatic garbage collection. In C:
- Explicitly manage memory allocation and deallocation
- Create pool allocators for frequently created/destroyed objects (particles)
- Implement clear ownership hierarchies for objects
- Design data structures with careful consideration of memory layout

### Threading Considerations
The current implementation is single-threaded. When porting:
- Consider asset loading on background threads
- Keep game logic on main thread for simplicity
- Use Raylib's threading utilities where appropriate
- Implement resource locking if using threads

## Implementation Strategy
1. Start with core engine components (rendering, input, resources)
2. Implement basic screens and transitions
3. Add entity system and game objects
4. Implement physics and collision
5. Add effects and particles
6. Implement UI system
7. Add audio and polish

This document provides a high-level overview of the game's architecture. Detailed specifications for each component are provided in separate documents. 