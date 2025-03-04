# Gameplay Mechanics Specification

## Core Game Loop

The game implements a classic breakout-style gameplay with competitive multiplayer elements. The main gameplay loop is managed by the `Game` class in `screens/game.py`.

## Game States

### Initialization
1. Players and scores are initialized
2. Level is created with blocks for both players
3. Countdown sequence starts before gameplay begins
4. Initial ball direction is randomly chosen with slight variation

### Active Gameplay
- Players control paddles to hit balls
- Blocks can be destroyed by balls
- Power-ups spawn periodically
- Score is tracked for multi-round matches
- Game can be paused

### Game Over Conditions
- Triggered when one player loses all their blocks
- Winner's score is incremented
- Music fades out
- Transitions to game over screen

## Power-up System

### Power-up Types
- Multiball: Adds additional balls
- SpeedBoost: Increases movement speed
- Fire: Adds fire effects
- Frost: Adds freezing effects
- Electricity: Adds electrical effects
- Rocket: Adds rocket projectiles
- Enlarger: Increases paddle size
- Reducer: Reduces paddle size

### Spawn Mechanics
- Base spawn rate: Every 4000ms
- Initial spawn chance: 37.5%
- Secondary spawn chance: 27.5%
- Third spawn chance: 17.5%
- Spawn chances increase over time
- Multiple power-ups can spawn simultaneously
- Predetermined spawn locations in the level

### Power-up Evolution
- Spawn chances increase every 3250ms
- Each increase adds 4.5% to all spawn probabilities
- Special handling for speed power-ups (20% chance for duplicates)

## Physics and Movement

### Ball Physics
- Initial angle randomized within bounds
- Collision detection with:
  - Paddles
  - Blocks
  - Level boundaries
- Multiple balls can be in play simultaneously

### Paddle Controls
- Player movement
- Collision response
- Power-up effects on paddle behavior

## Visual Effects

### Screen Elements
- Background system (currently "planks" theme)
- Score display
- Power-up indicators
- Transition effects
- Camera system for level view

### Special Effects
- Speed effects
- Flash effects
- Explosions
- Screen transitions
- Power-up visual feedback

## Audio System

### Music
- Game music playlist system
- Music fade out on game over
- Volume control integration

### Sound Effects
- Power-up sounds
- Collision sounds
- Game state change sounds

## Input Handling

### Controls
- Keyboard support
- Joystick/gamepad support
- Pause functionality (ESC key or START button)
- Debug keys for testing

## Performance Optimizations

### Graphics
- Sprite conversion for efficiency
- Double buffering
- Camera-based rendering
- Efficient background system

### Object Management
- Sprite groups for organized updates
- Efficient collision detection
- Time dilation calculations
- Memory management for power-ups

## Technical Details

### Screen Resolution
- Configurable screen dimensions
- Level boundaries
- UI element positioning
- Camera viewport management

### Frame Management
- Main clock system
- Time-based updates
- Frame rate independence
- Pause state handling

This specification outlines the core gameplay mechanics and systems implemented in the game. Each component is designed to work together to create a competitive and engaging multiplayer experience. 