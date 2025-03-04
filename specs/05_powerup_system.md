# Power-up System Specification

## Core Power-up Framework

### Base Power-up Properties
- Standard dimensions: 8x8 pixels
- Sprite-based rendering
- Collision detection
- Sound effect system
- Visual effects system

### Common Features
- Floating animation (bob effect)
- Spawn effect animation
- Sound on spawn/collection
- Shadow effects
- Group management

## Power-up Types

### Multiball
- Spawns additional ball
- Duration: 10000ms
- Copies active effects to new ball
- Position-aware spawning
- Excludes certain effects from copying

### SpeedBoost
- Increases movement speed
- Temporary duration
- Stackable effects
- Visual feedback

### Fire
- Adds fire effects
- Damage modification
- Visual effects
- Duration-based

### Frost
- Freezing effects
- Movement modification
- Visual feedback
- Temporary duration

### Electricity
- Electrical effects
- Chain reaction potential
- Visual animation
- Duration-based

### Rocket
- Projectile enhancement
- Movement modification
- Visual effects
- Temporary boost

### Enlarger
- Increases paddle size
- Size modification system
- Visual scaling
- Duration-based

### Reducer
- Decreases paddle size
- Size modification system
- Visual scaling
- Duration-based

### Gravity
- Gravity field effects
- Movement modification
- Area of effect
- Duration-based

## Technical Implementation

### Base Power-up Class
- Sprite inheritance
- Position management
- Effect group handling
- Sound management
- Destruction handling

### Effect System
- Effect sharing mechanism
- Timeout system
- Effect stacking
- Visual feedback
- Sound integration

### Visual Components
- Sprite management
- Animation system
- Shadow effects
- Flash effects
- Bob animation

## Gameplay Integration

### Spawn System
- Random spawn locations
- Spawn rate control
- Multiple spawn handling
- Position validation

### Collection Mechanics
- Ball collision detection
- Effect application
- Owner management
- Sound triggering
- Visual feedback

### Effect Management
- Duration tracking
- Effect stacking
- Effect sharing
- Effect cleanup
- Owner tracking

## Technical Features

### Performance Optimization
- Image conversion
- Sprite management
- Effect group handling
- Sound management
- Memory management

### State Management
- Position tracking
- Effect states
- Duration tracking
- Owner states
- Display states

## Visual Effects

### Spawn Effects
- Initial flash:
  - Start color: White (255 alpha)
  - End color: Transparent
  - Duration: 18 frames * FPS

### Animation
- Bob effect:
  - Factor: 0.5
  - Smooth sine wave
  - Position update rate
- Shadow system
- Collection effects

## Sound System

### Sound Effects
- Spawn sounds
- Collection sounds
- Volume control
- Random selection
- Multiple sound support

## Integration Points

### Player Integration
- Effect inheritance
- Power-up display
- Owner tracking
- Group management

### Game System Integration
- Sprite group system
- Sound system
- Settings system
- Graphics system

### Effect System Integration
- Effect sharing
- Duration management
- Visual effects
- Sound effects

This specification details the power-up system implementation, covering both the base framework and specific power-up types. 