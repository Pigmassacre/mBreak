# Animation System

## Overview

The animation system in mBreak is built around the third-party Pyganim library, which provides a convenient wrapper around Pygame's sprite and animation capabilities. This specification details how animations are implemented in the current Python codebase and how they should be ported to C with Raylib.

## Current Implementation (Python + Pygame + Pyganim)

### Core Components

#### Pyganim Library

The game uses Al Sweigart's Pyganim library (`libs/pyganim/__init__.py`), which provides:

- Sprite animation from individual frames or spritesheets
- Animation control (play, pause, stop)
- Animation states (PLAYING, PAUSED, STOPPED)
- Duration control for each frame
- Looping/non-looping animations
- Anchor point positioning
- Frame-based control and manipulation

#### Animation Usage Areas

Animations are used in several key areas of the game:

1. **Logo Animation** (`gui/logo.py`): The game logo uses animated frames
2. **Effect Animations** (`objects/effects/explosion.py`): Visual effects like explosions
3. **Powerup Animations** (`objects/powerups/frost.py` and others): Visual indicators for powerups

### Implementation Details

#### Animation Creation

Animations are created by defining frame sequences with corresponding durations:

```python
# Example from explosion.py
frames = []
for i in range(1, 17):
    frames.append(("res/effect/explosion/explosion_" + str(i) + ".png", 50))
self.animation = pyganim.PygAnimation(frames, False)
```

#### Animation Control

The Pyganim API provides methods for controlling animations:

- `play()`: Start the animation
- `pause()`: Pause the animation
- `stop()`: Stop the animation and reset to the first frame
- `loop`: Boolean property to enable/disable looping
- `reverse()`: Reverse the animation

#### Drawing Animations

Animations are rendered using Pyganim's integration with Pygame:

```python
# Drawing an animation to a surface
animation.blit(surface, (x, y))
```

#### Anchor Points

Pyganim supports positioning animations using anchor points (NW, N, NE, W, C, E, SW, S, SE), allowing precise placement of animated elements.

#### Spritesheet Support

The library can extract animations from sprite sheets using `getImagesFromSpriteSheet()` with parameters for width, height, rows, columns, or explicit rectangles.

## Port Implementation (C + Raylib)

### Core Animation Structs

```c
// Animation state constants
#define ANIMATION_PLAYING 0
#define ANIMATION_PAUSED 1
#define ANIMATION_STOPPED 2

// Animation frame
typedef struct AnimationFrame {
    Texture2D texture;     // Texture for this frame
    float duration;        // Duration in milliseconds
    Rectangle sourceRect;  // Source rectangle in the texture
} AnimationFrame;

// Animation
typedef struct Animation {
    AnimationFrame* frames;    // Array of frames
    int frameCount;            // Number of frames
    int currentFrame;          // Current frame index
    float timeCounter;         // Time accumulator
    int state;                 // PLAYING, PAUSED, STOPPED
    bool loop;                 // Whether animation should loop
    Vector2 position;          // Position to draw at
    Vector2 origin;            // Origin point for rotation/scaling
    float rotation;            // Rotation angle (degrees)
    float scale;               // Scale factor
    Color tint;                // Color tint
} Animation;
```

### Key Functions

```c
// Create a new animation from individual files
Animation* CreateAnimation(const char** filePaths, float* durations, int frameCount, bool loop);

// Create animation from spritesheet
Animation* CreateAnimationFromSpritesheet(
    Texture2D spritesheet, 
    int frameWidth, 
    int frameHeight, 
    int framesPerRow, 
    int frameCount, 
    float frameDuration, 
    bool loop);

// Free animation resources
void UnloadAnimation(Animation* animation);

// Update animation state
void UpdateAnimation(Animation* animation, float deltaTime);

// Draw animation
void DrawAnimation(Animation* animation);

// Animation control
void PlayAnimation(Animation* animation);
void PauseAnimation(Animation* animation);
void StopAnimation(Animation* animation);
void ResetAnimation(Animation* animation);
bool IsAnimationFinished(Animation* animation);
```

### Animation Management System

The port should include an animation manager to handle loading, unloading, and caching animations:

```c
typedef struct AnimationManager {
    Animation** animations;
    int count;
    int capacity;
} AnimationManager;

AnimationManager* InitAnimationManager(int initialCapacity);
void FreeAnimationManager(AnimationManager* manager);
int RegisterAnimation(AnimationManager* manager, Animation* animation);
Animation* GetAnimation(AnimationManager* manager, int id);
void UpdateAllAnimations(AnimationManager* manager, float deltaTime);
```

### Implementation Strategy

1. **Texture Management**:
   - Use Raylib's `LoadTexture` for loading frame images
   - Implement a texture cache to avoid duplicate loading of the same images
   - Use Raylib's `UnloadTexture` for proper cleanup

2. **Animation Updates**:
   - Update animations in the game loop based on delta time
   - Handle frame transitions with proper timing
   - Support variable frame durations

3. **Drawing**:
   - Use Raylib's `DrawTextureRec` or `DrawTexturePro` for rendering frames
   - Support transformations (position, rotation, scale)
   - Support tinting and alpha blending

4. **Spritesheet Handling**:
   - Implement helper functions to extract frames from spritesheets
   - Support automatic frame extraction from uniform grids
   - Support custom frame rectangles for non-uniform spritesheets

## Example Usage (Raylib)

### Creating an Animation

```c
// Create an explosion animation
const char* explosionFiles[] = {
    "res/effect/explosion/explosion_1.png",
    "res/effect/explosion/explosion_2.png",
    // ... more frames
};
float durations[] = {50.0f, 50.0f, /* ... more durations */};
Animation* explosionAnim = CreateAnimation(explosionFiles, durations, 16, false);
```

### Using an Animation in Game

```c
// In the update function
UpdateAnimation(explosionAnim, GetFrameTime());

// In the draw function
DrawAnimation(explosionAnim);

// When explosion starts
PlayAnimation(explosionAnim);

// Check if animation finished
if (IsAnimationFinished(explosionAnim)) {
    // Handle explosion completed
}
```

### Creating Animation from Spritesheet

```c
// Load spritesheet texture
Texture2D spritesheet = LoadTexture("res/spritesheets/effects.png");

// Create animation with 8 frames, 100ms per frame
Animation* effectAnim = CreateAnimationFromSpritesheet(
    spritesheet, 64, 64, 4, 8, 0.1f, true);
    
// Set position
effectAnim->position = (Vector2){ 100.0f, 200.0f };
```

## Conversion Notes

### From Pyganim to Raylib

| Pyganim Concept | Raylib Equivalent |
|-----------------|-------------------|
| `PygAnimation` | `Animation` struct |
| `play()` | `PlayAnimation()` |
| `pause()` | `PauseAnimation()` |
| `stop()` | `StopAnimation()` |
| Image sequence | Array of Texture2D |
| `blit()` | `DrawAnimation()` |
| Anchor points | `origin` Vector2 |
| `loop` property | `loop` boolean |

### Key Differences

1. Pyganim uses Pygame's event loop timing, while Raylib uses `GetFrameTime()` for timing
2. Pyganim loads images directly from files for each frame, Raylib should use texture caching
3. Pyganim can animate on any surface, Raylib draws directly to the screen or render textures
4. Raylib has built-in support for 2D transformations that should be leveraged

## Memory Management

1. **Texture Loading**:
   - Load textures once and share references
   - Implement reference counting or caching
   - Properly unload textures when animations are destroyed

2. **Frame Management**:
   - Allocate frame arrays with proper memory management
   - Support dynamic frame creation and destruction
   - Clean up all resources when animations are no longer needed

## Performance Considerations

1. **Batch Processing**:
   - Group animations when possible for batch rendering
   - Minimize texture binding changes

2. **Caching**:
   - Cache animations and textures to reduce load times
   - Share texture references between animations when possible
   
3. **Culling**:
   - Skip updating animations that are not visible
   - Implement visibility checks before rendering 