# Shadow System Specification

## Overview

The Shadow System is responsible for creating and managing shadow effects beneath game objects, enhancing visual depth and providing spatial cues to the player. Shadows help players perceive the relative positions of objects and contribute significantly to the game's overall visual appeal.

This specification outlines the design and implementation of the Shadow System for the C/Raylib port, translating the existing Python/Pygame implementation while enhancing it with additional features and optimizations possible in C and Raylib.

## Core Architecture

### Shadow Structure

```c
typedef struct Shadow {
    // Reference to parent object
    void* parent;                // Parent object this shadow is attached to
    Rectangle* parent_rect;      // Pointer to parent's rectangle for positioning
    
    // Shadow properties
    Vector2 position;            // Position of the shadow
    Vector2 size;                // Width and height of the shadow
    Rectangle rect;              // Rectangle for drawing the shadow
    
    // Visual properties
    Color color;                 // Color of the shadow (including alpha)
    float alpha;                 // Alpha value (0-255)
    
    // Offset from parent
    float offset_x;              // Horizontal offset from parent
    float offset_y;              // Vertical offset from parent
    
    // Lingering properties for fading shadows
    bool linger;                 // Whether the shadow lingers after parent is gone
    float linger_time_left;      // Time left before shadow starts fading (if lingering)
    float alpha_step;            // Rate at which alpha decreases when fading
    
    // Rendering method
    bool use_fill;               // Whether to use fill method (true) or texture (false)
    Texture2D* texture;          // Texture to use if not using fill method
    Texture2D* original_texture; // Original texture copy (used for rotation)
    
    // Active state
    bool active;                 // Whether the shadow is active
} Shadow;
```

### Shadow Manager Structure

```c
typedef struct ShadowManager {
    Shadow* shadows;             // Array of shadows
    int capacity;                // Maximum number of shadows
    int count;                   // Current number of active shadows
    
    // Settings
    bool shadows_enabled;        // Whether shadows are globally enabled
    
    // Shared resources
    Shader shadow_shader;        // Optional shader for advanced shadow effects
} ShadowManager;
```

### Core Functions

```c
// Initialization and cleanup
ShadowManager* InitShadowManager(int max_shadows);
void DestroyShadowManager(ShadowManager* manager);

// Shadow creation
Shadow* CreateShadow(
    ShadowManager* manager,
    void* parent,
    Rectangle* parent_rect,
    Color color,
    bool linger,
    bool use_fill
);

// Batch operations
void UpdateShadows(ShadowManager* manager, float delta_time);
void DrawShadows(ShadowManager* manager, Camera2D camera);

// Individual shadow operations
void UpdateShadowPosition(Shadow* shadow);
void SetShadowColor(Shadow* shadow, Color color);
void SetShadowOffset(Shadow* shadow, float offset_x, float offset_y);
void SetShadowLinger(Shadow* shadow, bool linger, float linger_time, float alpha_step);
void DestroyShadow(ShadowManager* manager, int index);
```

## Shadow Types and Variations

The Shadow System supports different types of shadows to accommodate various game objects:

### Standard Shadow

Simple shadow for most game objects, positioned with a slight offset from the parent:

```c
Shadow* CreateStandardShadow(ShadowManager* manager, void* parent, Rectangle* parent_rect);
```

This is the most common shadow type used by most game objects including balls, paddles, blocks, and powerups.

### Particle Shadow

Smaller, more transparent shadow for particles, designed to fade away:

```c
Shadow* CreateParticleShadow(ShadowManager* manager, void* parent, Rectangle* parent_rect, Color color);
```

Particle shadows have custom colors and are set to linger and fade out when the particle is destroyed.

### Trace Shadow

Shadow for trace effects, which may linger after the trace is gone:

```c
Shadow* CreateTraceShadow(ShadowManager* manager, void* parent, Rectangle* parent_rect, Color color);
```

Trace shadows are attached to trace objects and have custom colors to match the trace effect.

### Dynamic Shadow

Shadow that adjusts based on object movement, simulating rudimentary lighting:

```c
Shadow* CreateDynamicShadow(ShadowManager* manager, void* parent, Rectangle* parent_rect, float max_offset);
void UpdateDynamicShadow(Shadow* shadow, Vector2 light_source);
```

## Rendering Techniques

The Shadow System supports multiple rendering techniques as implemented in the original codebase:

### Basic Fill Method

The simplest and most efficient rendering method, using a colored rectangle:

```c
void DrawShadowFill(Shadow* shadow, Camera2D camera);
```

When `use_fill` is set to true, the shadow is rendered as a solid colored rectangle with the specified alpha value.

### Texture-Based Method

Using a texture derived from the parent object for more detailed shadows:

```c
void DrawShadowTexture(Shadow* shadow, Camera2D camera);
```

When `use_fill` is set to false, the shadow uses a copy of the parent's texture, colorized to the shadow color.

### Colorization Process

```c
// Function to colorize an image to create shadow effect
void ColorizeTexture(Texture2D* texture, Color color, bool blend_alpha);
```

This process handles different types of textures, with or without alpha channels.

## Shadow Lifecycle Management

### Creation and Initialization

```c
Shadow* CreateShadow(ShadowManager* manager, void* parent, Rectangle* parent_rect, Color color, bool linger, bool use_fill);
```

This function creates a new shadow and initializes all its properties based on the parent object.

### Update Logic

```c
void UpdateShadow(Shadow* shadow, float delta_time);
```

The update function handles:
1. Lingering behavior and alpha fading
2. Position updates based on parent movement
3. Checks for shadow visibility

### Destruction

```c
void DestroyShadow(ShadowManager* manager, int index);
```

Properly removes and cleans up shadow resources.

## Performance Optimization

### Batch Rendering

```c
// Enable batch rendering for shadows
void EnableShadowBatchRendering(ShadowManager* manager);
void DisableShadowBatchRendering(ShadowManager* manager);

// Internal batch drawing function
void DrawShadowsBatch(ShadowManager* manager, Camera2D camera);
```

### Culling

```c
// Only update and draw shadows that are visible on screen
bool IsShadowVisible(Shadow* shadow, Camera2D camera);
```

### Level of Detail

```c
// Adjust shadow detail based on distance from camera or game settings
void SetShadowDetailLevel(ShadowManager* manager, int level);
```

## Integration with Settings System

The Shadow System will be integrated with the Settings System to allow users to enable/disable shadows or adjust their quality:

```c
// Apply settings to shadow system
void ApplyShadowSettings(ShadowManager* manager, SettingsManager* settings_manager);

// Toggle shadows on/off
void SetShadowsEnabled(ShadowManager* manager, bool enabled);

// Set shadow quality (affects rendering method and detail)
void SetShadowQuality(ShadowManager* manager, int quality);
```

## Game Object Integration

Functions to simplify the integration of shadows with various game objects:

```c
// Helper functions for common game objects
void AddShadowToBlock(ShadowManager* manager, Block* block);
void AddShadowToBall(ShadowManager* manager, Ball* ball);
void AddShadowToPaddle(ShadowManager* manager, Paddle* paddle);
void AddShadowToPowerup(ShadowManager* manager, Powerup* powerup);
void AddShadowToParticle(ShadowManager* manager, Particle* particle);
void AddShadowToMissile(ShadowManager* manager, Missile* missile);
void AddShadowToTrace(ShadowManager* manager, Trace* trace);
void AddShadowToArrowIndicator(ShadowManager* manager, ArrowIndicator* arrow);
```

## Camera Integration

The Shadow System interacts with the camera system to properly position shadows relative to the camera view:

```c
// Apply camera offset to shadow position when rendering
void ApplyCameraOffset(Shadow* shadow, Camera2D camera, Vector2* result_position);
```

## Advanced Features

### Shadow Layering

Manage shadow depth by specifying z-order:

```c
void SetShadowLayer(Shadow* shadow, int layer);
```

### Shadow Animations

Animate shadow properties for special effects:

```c
void AnimateShadowAlpha(Shadow* shadow, float target_alpha, float duration);
void AnimateShadowOffset(Shadow* shadow, float target_offset_x, float target_offset_y, float duration);
void AnimateShadowSize(Shadow* shadow, float target_width, float target_height, float duration);
```

### Shadow Effects

Special effects for dramatic situations:

```c
void CreateShadowLiftEffect(ShadowManager* manager, void* parent, Rectangle* parent_rect, float duration);
void CreateShadowExplosionEffect(ShadowManager* manager, Vector2 position, float radius, float duration);
```

## Debugging Support

```c
// Debug visualization
void DrawShadowDebug(ShadowManager* manager, Camera2D camera);

// Performance metrics
void LogShadowSystemMetrics(ShadowManager* manager);
```

## Implementation Notes

1. The Shadow System is primarily visual and does not affect game physics.
2. Shadows should be updated after their parent objects have been updated.
3. The system should be optimized to handle many shadows simultaneously.
4. Shadow alpha fading should be framerate-independent, using delta time for consistent results.
5. Texture-based shadows might be more resource-intensive but provide better visual fidelity.
6. Fill-based shadows are more efficient and suitable for lower-end systems.
7. The shadow's position is determined by the parent's position plus an offset, which can be adjusted for different visual effects.
8. The lingering behavior allows for shadows to persist and fade out after their parent object is destroyed, useful for effects like explosions or disappearing objects.

## Integration with Game Loop

```c
// In the main game loop:
void GameLoop() {
    // Update game objects
    UpdateGameObjects(delta_time);
    
    // Update shadows after game objects
    UpdateShadows(shadow_manager, delta_time);
    
    // Draw game scene
    BeginDrawing();
    ClearBackground(RAYWHITE);
    
    // Draw shadows first (under game objects)
    DrawShadows(shadow_manager, camera);
    
    // Draw game objects
    DrawGameObjects(camera);
    
    EndDrawing();
}
``` 