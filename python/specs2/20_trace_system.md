# Trace System Specification

## Overview

The Trace System is responsible for creating and managing visual trails behind moving objects, particularly balls, in the game. These traces create a visual effect that enhances the perception of movement and speed, leaving a fading trail that follows the object's path. The trace effect adds visual polish to the game while providing players with a better sense of object trajectory and momentum.

Each trace is the same size as its parent object, inherits its color, and gradually fades away over time until it becomes invisible. Traces also include shadow effects that enhance their visual appearance. The system is designed to be efficient, with traces automatically being destroyed once they are no longer visible or move outside the game boundaries.

## Core Architecture

```c
// Main trace structure
typedef struct Trace {
    int id;                     // Unique identifier
    Vector2 position;           // Position of the trace
    Vector2 size;               // Size of the trace (matches parent object)
    Color color;                // Color of the trace (inherited from parent)
    float alpha;                // Current alpha value (for fading)
    Shadow* shadow;             // Associated shadow
    Rectangle rect;             // Rectangle used for drawing and bounds checking
    Texture2D texture;          // Optional texture (can be null if using simple fill)
    bool isActive;              // Whether the trace is active
} Trace;

// Trace system that manages all traces
typedef struct TraceSystem {
    Trace* traces;              // Array of all traces
    int count;                  // Number of active traces
    int capacity;               // Maximum capacity
    float alphaStep;            // Rate at which traces fade (alpha units per second)
    bool enabled;               // Whether the system is enabled globally
} TraceSystem;
```

## System Initialization

```c
// Initialize the trace system
TraceSystem* InitTraceSystem(int maxTraces, float alphaStep) {
    TraceSystem* system = MemAlloc(sizeof(TraceSystem));
    
    system->traces = MemAlloc(sizeof(Trace) * maxTraces);
    system->count = 0;
    system->capacity = maxTraces;
    system->alphaStep = alphaStep;
    system->enabled = true;
    
    return system;
}

// Free trace system resources
void FreeTraceSystem(TraceSystem* system) {
    // Free all active traces
    for (int i = 0; i < system->count; i++) {
        FreeTrace(&system->traces[i]);
    }
    
    // Free the system itself
    MemFree(system->traces);
    MemFree(system);
}

// Free a trace's resources
void FreeTrace(Trace* trace) {
    if (trace->shadow) {
        FreeShadow(trace->shadow);
        trace->shadow = NULL;
    }
    
    if (trace->texture.id > 0) {
        UnloadTexture(trace->texture);
    }
}
```

## Core Functionality

### Trace Creation

```c
// Create a new trace for an object (typically a ball)
int CreateTrace(TraceSystem* system, Vector2 position, Vector2 size, Color color) {
    if (system->count >= system->capacity || !system->enabled) {
        return -1; // System is full or disabled
    }
    
    int index = system->count++;
    Trace* trace = &system->traces[index];
    
    trace->id = GetNextTraceId();
    trace->position = position;
    trace->size = size;
    trace->color = color;
    trace->alpha = color.a; // Start with parent's alpha
    trace->isActive = true;
    
    // Set up rectangle for drawing
    trace->rect = (Rectangle){
        trace->position.x,
        trace->position.y,
        trace->size.x,
        trace->size.y
    };
    
    // Create shadow
    Color shadowColor = BlendColors(color, SHADOW_BLEND_COLOR);
    trace->shadow = CreateShadow(trace, shadowColor, false);
    
    return trace->id;
}

// Create a trace from a parent object
int CreateTraceFromParent(TraceSystem* system, GameObject* parent) {
    if (!system->enabled) {
        return -1;
    }
    
    return CreateTrace(
        system, 
        parent->position, 
        parent->size, 
        parent->color
    );
}
```

### Trace Update and Rendering

```c
// Update all traces in the system
void UpdateTraceSystem(TraceSystem* system, float deltaTime) {
    if (!system->enabled) {
        return;
    }
    
    for (int i = 0; i < system->count; i++) {
        Trace* trace = &system->traces[i];
        
        if (!trace->isActive) {
            continue;
        }
        
        // Update alpha value - fade out over time
        float newAlpha = trace->alpha - (system->alphaStep * deltaTime);
        
        if (newAlpha <= 0) {
            // Trace has faded completely, mark for removal
            DestroyTrace(system, i);
            i--; // Adjust index after removal
            continue;
        }
        
        // Update alpha
        trace->alpha = newAlpha;
        trace->color.a = (unsigned char)newAlpha;
        
        // Update shadow alpha too
        if (trace->shadow) {
            trace->shadow->color.a = (unsigned char)newAlpha;
        }
        
        // Check if trace is outside game boundaries
        if (IsTraceOutsideBounds(trace)) {
            DestroyTrace(system, i);
            i--; // Adjust index after removal
        }
    }
}

// Draw all traces
void DrawTraceSystem(TraceSystem* system) {
    if (!system->enabled) {
        return;
    }
    
    // Draw shadows first (to appear behind traces)
    for (int i = 0; i < system->count; i++) {
        Trace* trace = &system->traces[i];
        if (trace->isActive && trace->shadow) {
            DrawShadow(trace->shadow);
        }
    }
    
    // Draw traces
    for (int i = 0; i < system->count; i++) {
        Trace* trace = &system->traces[i];
        if (trace->isActive) {
            DrawRectangleRec(trace->rect, trace->color);
        }
    }
}
```

### System Management

```c
// Destroy a trace and compact the array
void DestroyTrace(TraceSystem* system, int index) {
    if (index < 0 || index >= system->count) {
        return;
    }
    
    Trace* trace = &system->traces[index];
    
    // Free resources
    FreeTrace(trace);
    
    // Move the last trace to this position (if not the last one)
    if (index < system->count - 1) {
        system->traces[index] = system->traces[system->count - 1];
    }
    
    // Decrease count
    system->count--;
}

// Check if a trace is outside game boundaries
bool IsTraceOutsideBounds(Trace* trace) {
    return (trace->rect.x + trace->rect.width <= LEVEL_X ||
            trace->rect.x >= LEVEL_MAX_X ||
            trace->rect.y + trace->rect.height <= LEVEL_Y ||
            trace->rect.y >= LEVEL_MAX_Y);
}

// Enable or disable the entire trace system
void SetTraceSystemEnabled(TraceSystem* system, bool enabled) {
    system->enabled = enabled;
    
    // If disabling, you might want to clear all traces
    if (!enabled) {
        ClearAllTraces(system);
    }
}

// Clear all traces from the system
void ClearAllTraces(TraceSystem* system) {
    for (int i = 0; i < system->count; i++) {
        FreeTrace(&system->traces[i]);
    }
    system->count = 0;
}
```

## Integration

### Integration with Ball Update Cycle

The Trace System is primarily integrated with ball objects, creating traces at regular intervals as balls move through the game space. This integration is handled within the ball update cycle:

```c
// Example of integrating with ball update cycle
void UpdateBall(Ball* ball, float deltaTime) {
    // Update ball position, physics, etc.
    // ...
    
    // Handle trace creation
    ball->traceSpawnTimer += deltaTime;
    if (ball->traceSpawnTimer >= ball->traceSpawnRate) {
        // Reset timer
        ball->traceSpawnTimer = 0.0f;
        
        // Create a trace if enabled in graphics settings
        if (game->settings.graphicsSettings.tracesEnabled) {
            CreateTraceFromParent(game->traceSystem, (GameObject*)ball);
        }
    }
}
```

### Integration with Game Loop

The Trace System should be updated and drawn within the main game loop:

```c
// During game update
void UpdateGame(Game* game, float deltaTime) {
    // Update other systems
    // ...
    
    // Update trace system
    UpdateTraceSystem(game->traceSystem, deltaTime);
}

// During game rendering
void DrawGame(Game* game) {
    // Draw other elements
    // ...
    
    // Draw trace system (generally before drawing the actual objects)
    DrawTraceSystem(game->traceSystem);
    
    // Draw balls, paddles, etc.
    // ...
}
```

## Settings Integration

The Trace System should be configurable through game settings:

```c
// Apply settings to trace system
void ApplyTraceSettings(TraceSystem* system, GameSettings* settings) {
    // Enable/disable based on user preferences
    system->enabled = settings->graphicsSettings.tracesEnabled;
    
    // Update alpha step rate if needed
    system->alphaStep = settings->graphicsSettings.traceDecayRate;
}
```

## Performance Considerations

1. **Trace Count Management**: The number of active traces should be limited to prevent performance issues. Consider adding a max traces per object type setting.

2. **Alpha Decay Rate**: The rate at which traces fade away affects both visual quality and performance. A faster decay rate means fewer active traces at any time.

3. **Conditional Creation**: Only create traces when necessary, such as for fast-moving objects, and when the feature is enabled in graphics settings.

4. **Batch Rendering**: For optimal performance, implement batch rendering for traces of similar types.

5. **Culling**: Remove traces that are no longer visible or have moved outside the game area.

## Implementation Notes

1. The Trace System is purely visual and does not affect game physics or logic.

2. Traces inherit their visual properties from their parent objects, maintaining visual consistency.

3. Each trace has its own shadow, adding depth to the visual effect.

4. The system automatically manages the lifecycle of traces, creating them when requested and destroying them when they fade out or move out of bounds.

5. The system is designed to be toggleable, allowing players to disable traces for performance reasons or personal preference.

## Conclusion

The Trace System provides a visually appealing motion effect that enhances the game's aesthetic quality while giving players better visual feedback about object movement. Its implementation is efficient, automatically managing the lifecycle of trace objects, and integrates seamlessly with the ball update cycle and rendering pipeline. 