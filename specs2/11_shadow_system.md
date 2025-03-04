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

The Shadow System will support different types of shadows to accommodate various game objects:

### Standard Shadow

Simple shadow for most game objects, positioned with a slight offset from the parent:

```c
Shadow* CreateStandardShadow(ShadowManager* manager, void* parent, Rectangle* parent_rect);
```

### Particle Shadow

Smaller, more transparent shadow for particles, designed to fade away:

```c
Shadow* CreateParticleShadow(ShadowManager* manager, void* parent, Rectangle* parent_rect, Color color);
```

### Trace Shadow

Shadow for trace effects, which may linger after the trace is gone:

```c
Shadow* CreateTraceShadow(ShadowManager* manager, void* parent, Rectangle* parent_rect, Color color);
```

### Dynamic Shadow

Shadow that adjusts based on object movement, simulating rudimentary lighting:

```c
Shadow* CreateDynamicShadow(ShadowManager* manager, void* parent, Rectangle* parent_rect, float max_offset);
void UpdateDynamicShadow(Shadow* shadow, Vector2 light_source);
```

## Rendering Techniques

The Shadow System will support multiple rendering techniques:

### Basic Fill Method

The simplest and most efficient rendering method, using a colored rectangle:

```c
void DrawShadowFill(Shadow* shadow, Camera2D camera);
```

### Texture-Based Method

Using a texture derived from the parent object for more detailed shadows:

```c
void DrawShadowTexture(Shadow* shadow, Camera2D camera);
```

### Shader-Based Method

Using a shader for advanced effects like soft shadows or multiple light sources:

```c
void InitShadowShader(ShadowManager* manager);
void DrawShadowShader(Shadow* shadow, Camera2D camera);
```

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

1. **Rendering Approach**: The shadow system will primarily use the basic fill method for efficiency, with options for texture-based or shader-based rendering for higher quality.

2. **Memory Management**: Shadows will be managed in pre-allocated arrays to minimize memory allocation during gameplay.

3. **Parent Object Tracking**: Shadows will be automatically positioned based on their parent object's position, with configurable offsets.

4. **Integration with Graphics Settings**: The shadow system will respect the user's graphics settings, adjusting quality or disabling shadows entirely based on preferences.

5. **Effect on Performance**: The shadow system is designed to have minimal impact on performance, with batch rendering and culling optimizations.

6. **Flexibility**: The system allows for various shadow types and effects, catering to different game objects and situations.

## Global Shadow Settings

Default values for shadow properties:

```c
// Default shadow properties
static const float DEFAULT_SHADOW_OFFSET_X = 1.0f;
static const float DEFAULT_SHADOW_OFFSET_Y = 2.0f;
static const float DEFAULT_LINGER_TIME = 1.5f;        // In seconds
static const float DEFAULT_ALPHA_STEP = 3.0f;         // Alpha reduction per second
static const Color DEFAULT_SHADOW_COLOR = { 0, 0, 0, 128 }; // Black with 50% transparency
```

## Conclusion

The Shadow System specification for the C/Raylib port builds upon the existing Python/Pygame implementation while enhancing it with additional features and optimizations. The design provides a flexible, efficient way to add visual depth to the game through shadows, with options for different rendering techniques and special effects. The integration with the Settings System ensures that players can adjust shadow quality based on their preferences and hardware capabilities. 