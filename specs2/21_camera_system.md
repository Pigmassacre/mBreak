# Camera System Specification

## Overview

The Camera System serves as the visual viewport for the game, controlling what the player sees on screen. It manages the offset between world coordinates and screen coordinates, enabling features such as screen shake effects, smooth scrolling, and boundary constraints. The camera enhances gameplay by providing responsive visual feedback and maintaining focus on relevant game elements.

This specification outlines the design and implementation of the Camera System for the C/Raylib port, translating the existing Python/Pygame implementation while enhancing it with additional features and optimizations possible in C and Raylib.

## Core Architecture

### Camera Structure

```c
typedef struct GameCamera {
    // Raylib camera
    Camera2D camera;             // The underlying Raylib Camera2D instance
    
    // Position and dimensions
    Vector2 origin;              // Original/base position of the camera
    Rectangle bounds;            // Boundary rectangle for the camera
    float width;                 // Width of the camera view
    float height;                // Height of the camera view
    
    // Camera behavior
    Vector2 target;              // Target position to follow
    bool follow_target;          // Whether the camera should follow a target
    
    // Shake effect management
    bool is_shaking;             // Flag to indicate if camera is currently shaking
    float shake_time_left;       // Time remaining for current shake effect
    float shake_intensity;       // Current shake intensity
    float shake_time_passed;     // Time passed since last shake update
    Vector2 shake_offset;        // Current shake offset (x, y)
    
    // Advanced features
    float zoom;                  // Camera zoom level
    float rotation;              // Camera rotation in degrees
} GameCamera;
```

### Camera Manager Structure

```c
typedef struct CameraManager {
    GameCamera* active_camera;   // Currently active camera
    GameCamera* cameras;         // Array of cameras
    int capacity;                // Maximum number of cameras
    int count;                   // Current number of cameras
} CameraManager;
```

## Core Functions

### Initialization and Cleanup

```c
// Create and initialize the camera system
CameraManager* InitCameraManager(int max_cameras);
void DestroyCameraManager(CameraManager* manager);

// Create a camera with specified dimensions and position
GameCamera* CreateCamera(CameraManager* manager, float x, float y, float width, float height);

// Set the active camera
void SetActiveCamera(CameraManager* manager, int camera_index);
```

### Camera Position and Movement

```c
// Set camera position
void SetCameraPosition(GameCamera* camera, float x, float y);

// Move camera by specified offset
void MoveCamera(GameCamera* camera, float dx, float dy);

// Set camera target to follow
void SetCameraTarget(GameCamera* camera, Vector2 target);

// Enable/disable target following
void SetCameraFollowTarget(GameCamera* camera, bool follow);

// Set camera boundaries (level limits)
void SetCameraBounds(GameCamera* camera, Rectangle bounds);
```

### Camera Effects

```c
// Shake the camera with given duration and intensity
void ShakeCamera(GameCamera* camera, float duration_ms, float intensity);

// Zoom the camera
void SetCameraZoom(GameCamera* camera, float zoom);

// Smoothly transition to a zoom level
void ZoomCameraTo(GameCamera* camera, float target_zoom, float duration_ms);

// Rotate the camera
void SetCameraRotation(GameCamera* camera, float rotation_degrees);
```

### Update and Rendering

```c
// Update camera state (called every frame)
void UpdateCamera(GameCamera* camera, float delta_time);

// Setup camera for rendering
void BeginCameraMode(GameCamera* camera);

// End camera rendering
void EndCameraMode(void);

// Convert world coordinates to screen coordinates
Vector2 WorldToScreen(GameCamera* camera, Vector2 world_pos);

// Convert screen coordinates to world coordinates
Vector2 ScreenToWorld(GameCamera* camera, Vector2 screen_pos);
```

## Camera Shake System

The Camera Shake system provides visual feedback for game events like explosions, impacts, or powerful actions.

### Shake Behavior

```c
// Internal function to update camera shake
void UpdateCameraShake(GameCamera* camera, float delta_time);

// Calculate random shake offset
Vector2 CalculateShakeOffset(float intensity);
```

### Implementation Details

The shake effect is implemented as follows:

1. When `ShakeCamera` is called, the camera enters a shaking state with given parameters
2. During updates, a random offset is applied to the camera position
3. The offset changes several times per second based on game FPS settings
4. The shake intensity can be constant or can decrease over time
5. Once the shake duration expires, the camera returns to its original position

## Advanced Camera Controls

### Smooth Following

```c
// Enable smooth following of target (with damping)
void SetCameraSmoothFollow(GameCamera* camera, bool smooth_follow, float damping);

// Internal update for smooth following
void UpdateCameraSmoothFollow(GameCamera* camera, float delta_time);
```

### Camera Transitions

```c
// Start a smooth transition to a new position
void MoveCameraTo(GameCamera* camera, Vector2 position, float duration_ms);

// Start a smooth transition to a new zoom level
void ZoomCameraTo(GameCamera* camera, float target_zoom, float duration_ms);

// Internal update for camera transitions
void UpdateCameraTransitions(GameCamera* camera, float delta_time);
```

## Coordinate Transformations

The Camera System handles transformations between different coordinate spaces:

### World to Screen Conversion

```c
// Convert world coordinates to screen coordinates
Vector2 WorldToScreen(GameCamera* camera, Vector2 world_pos);

// Convert screen coordinates to world coordinates
Vector2 ScreenToWorld(GameCamera* camera, Vector2 screen_pos);

// Check if a world position is visible on screen
bool IsOnScreen(GameCamera* camera, Vector2 world_pos);

// Check if a rectangle in world space is visible on screen
bool IsRectVisible(GameCamera* camera, Rectangle world_rect);
```

## Integration with Game Loop

```c
// In the main game loop:
void GameLoop() {
    // Update game time
    UpdateGameClock(&game_clock);
    float delta_time = GetDeltaTime(&game_clock);
    
    // Process input (could affect camera target)
    ProcessInput();
    
    // Update game objects
    UpdateGameObjects(delta_time);
    
    // Update camera after game objects
    UpdateCamera(camera_manager->active_camera, delta_time);
    
    // Render the scene with camera
    BeginDrawing();
    ClearBackground(RAYWHITE);
    
    BeginCameraMode(camera_manager->active_camera);
    DrawGameWorld();  // Draw all elements in world coordinates
    EndCameraMode();
    
    DrawUI();  // Draw UI elements in screen coordinates
    
    EndDrawing();
}
```

## Camera Settings and Configuration

```c
// Apply settings to camera system
void ApplyCameraSettings(GameCamera* camera, SettingsManager* settings);

// Configure camera defaults
void ConfigureCamera(GameCamera* camera, CameraConfig config);
```

### Camera Configuration Options

```c
typedef struct CameraConfig {
    bool enable_shake;           // Whether shake effects are enabled
    float max_shake_intensity;   // Maximum allowed shake intensity
    bool enable_smooth_follow;   // Whether smooth following is enabled
    float follow_damping;        // Damping factor for smooth following
    float default_zoom;          // Default zoom level
    float min_zoom;              // Minimum zoom level
    float max_zoom;              // Maximum zoom level
} CameraConfig;
```

## Debug Support

```c
// Draw camera debug information
void DrawCameraDebug(GameCamera* camera);

// Log camera metrics
void LogCameraMetrics(GameCamera* camera);

// Draw camera bounds
void DrawCameraBounds(GameCamera* camera, Color color);
```

## Implementation Notes

1. **Offset Calculation**: When rendering, all game elements must have their positions adjusted by the camera offset to appear in the correct screen position.

2. **Frame Rate Independence**: Camera movement, shake effects, and transitions must use delta time for consistency across different frame rates.

3. **Boundary Constraints**: The camera position should be constrained within the level boundaries to prevent showing areas outside the game world.

4. **Integration with Raylib**: The implementation leverages Raylib's existing Camera2D system, extending it with additional features specific to the game.

5. **Performance Considerations**: Camera calculations are relatively lightweight but should be optimized, particularly for mobile platforms.

6. **Camera System Usage**: Most game elements should not need to interact directly with the camera system beyond adjusting their rendering positions.

7. **Shake Effect Limitations**: Excessive camera shake can cause motion sickness, so intensity should be kept at reasonable levels and be configurable by the player.

8. **Multiple Camera Support**: While the game primarily uses a single main camera, the architecture supports multiple cameras for features like split-screen or picture-in-picture effects.

## Current Usage in the Codebase

The Camera System is used throughout the codebase for:

1. **Rendering**: All game elements use the camera offset when blitting to the screen
2. **Visual Feedback**: The shake effect is triggered by collisions, explosions, and special attacks
3. **Level Boundaries**: The camera maintains positioning within the level boundaries
4. **Following**: In certain gameplay modes, the camera may follow specific targets

## Port Considerations

When porting the Camera System to C/Raylib:

1. **Coordinate System**: Ensure the coordinate system conventions match between Pygame and Raylib
2. **Camera API**: Leverage Raylib's built-in Camera2D functionality while extending it with game-specific features
3. **Performance**: Optimize camera calculations for C implementation
4. **Enhanced Features**: Consider adding additional features like zoom transitions and rotation that weren't in the original implementation
5. **Consistency**: Maintain the same behavior and feel as the original game 