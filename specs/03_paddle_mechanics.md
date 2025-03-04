# Paddle Mechanics and AI Specification

## Core Paddle Properties

### Physical Properties
- Width: Dynamic, based on middle image width
- Height: 22 pixels (default)
- Maximum height: 33 pixels
- Minimum height: 11 pixels
- Maximum/minimum width: Equal to default width

### Movement Properties
- Acceleration: 1.0 * FPS
- Retardation: 2.5 * FPS
- Maximum speed: 2.5 * FPS
- Vertical movement only
- Position tracked with float precision

## Visual Components

### Paddle Graphics
- Three-part segmented design:
  - Top segment
  - Middle segment (repeatable)
  - Bottom segment
- Player color tinting
- Shadow effect
- Hit effect animation
  - Start color: White (160 alpha)
  - End color: Transparent
  - Duration: 22 frames * FPS

### Visual Effects
- Size change visualization
- Hit feedback effects
- Shadow system
- Debug visualization (when enabled)

## Gameplay Mechanics

### Size Modification
- Dynamic size adjustment system
- Maintains position during resizing
- Enforces minimum/maximum constraints
- Supports both width and height changes

### Energy System
- Energy gain on ball hits
- Multiplier for consecutive hits
  - Base multiplier: 1.0
  - Increases by 0.5 per consecutive hit
  - Maximum multiplier: 3.0
- Different energy gains for:
  - Enemy ball hits (full gain)
  - Own ball hits (half gain)
- Energy capped at maximum value

## AI System

### Target Selection
- Tracks multiple potential targets
- Prioritizes based on:
  - Distance to target
  - Target speed
  - Target trajectory
  - Previous success/failure

### Movement AI

#### Trajectory Prediction
- Calculates ball trajectories
- Predicts intersection points
- Accounts for:
  - Ball velocity
  - Ball position
  - Paddle position
  - Level boundaries

#### Strategic Positioning
- Adaptive positioning system
- Maintains optimal defensive position
- Considers multiple threats
- Adjusts based on game state

#### Performance Optimization
- Decision cooldown: 0.08 seconds
- Movement buffer: 3 pixels
- Direction change cooldown: 0.1 seconds
- Prediction confidence tracking

### Learning Mechanisms
- Tracks missed balls
- Adjusts strategy based on success rate
- Adapts to opponent patterns
- Self-correcting behavior

### Advanced Features

#### Priority System
- Dynamic priority calculation
- Special handling for slow balls
- Distance-based prioritization
- Threat level assessment

#### Energy Management
- Strategic energy usage
- Charge/attack decision making
- Defensive energy conservation
- Offensive opportunity recognition

## Technical Implementation

### Collision System
- Rect-based collision detection
- Precise float position tracking
- Edge collision handling
- Hit effect triggering

### Performance Considerations
- Image conversion optimization
- Sprite group management
- Effect group handling
- Debug mode support

### State Management
- Key press tracking
- Movement state
- Size state
- Effect states
- Energy level

## Integration Points

### Player Integration
- Owner reference system
- Color inheritance
- Group membership
- Energy management

### Game System Integration
- Camera system awareness
- Group system participation
- Settings system compliance
- Debug system hooks

This specification details the paddle mechanics and AI behavior implementation, covering both the basic gameplay elements and the sophisticated AI decision-making system. 