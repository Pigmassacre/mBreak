# Particle System Specification

## Overview

The Particle System is a core visual component of the game, responsible for creating and managing particles that enhance visual feedback and effects. Particles are used as visual elements throughout the game to create effects like explosions, trails, smoke, sparks, and other visual enhancements that contribute to the game's visual appeal and feedback.

This specification outlines the design and implementation of the Particle System for the C/Raylib port, translating the existing Python/Pygame implementation while enhancing it with additional features and optimizations possible in C and Raylib.

## Core Architecture

### Particle Structure

```c
typedef struct Particle {
    // Position and size
    Vector2 position;        // Position (floating point for precise movement)
    Vector2 size;            // Width and height of the particle
    Rectangle rect;          // Rectangle used for drawing and collision detection
    
    // Movement properties
    float angle;             // Direction of movement in radians
    float speed;             // Current speed
    float retardation;       // Speed reduction per update
    float gravity;           // Gravity effect on the particle (0 for no gravity)
    float velocity_y;        // Vertical velocity for gravity calculations
    
    // Visual properties
    Color color;             // Color of the particle (including alpha)
    float alpha_step;        // Rate at which alpha decreases (0 for no fade)
    
    // Shadow properties
    Color shadow_color;      // Color of the particle's shadow
    struct Shadow* shadow;   // Pointer to the shadow object
    
    // Behavior flags
    bool kill_outside_level; // Whether to destroy the particle when it exits the level bounds
    bool kill_when_speed_reaches_zero; // Whether to destroy the particle when speed reaches zero
    
    // Lifecycle management
    bool active;             // Whether the particle is active
} Particle;
```

### Particle Manager Structure

```c
typedef struct ParticleManager {
    Particle* particles;     // Array of particles
    int capacity;            // Maximum number of particles
    int count;               // Current number of active particles
    
    // Performance optimization
    Texture2D particleTexture; // Optional texture for particles
    bool use_batch_rendering; // Whether to use batch rendering
} ParticleManager;
```

### Core Functions

```c
// Initialization and cleanup
ParticleManager* InitParticleManager(int max_particles);
void DestroyParticleManager(ParticleManager* manager);

// Particle creation
Particle* CreateParticle(
    ParticleManager* manager,
    float x, float y,
    float width, float height,
    float angle, float speed, float retardation,
    Color color, float alpha_step
);

// Batch operations
void UpdateParticles(ParticleManager* manager, float delta_time, float time_scale);
void DrawParticles(ParticleManager* manager, Camera2D camera);

// Individual particle operations
void DestroyParticle(ParticleManager* manager, int index);
```

## Particle Emitters

Enhancing the original implementation, the C/Raylib port will include a dedicated Particle Emitter system to simplify the creation of particle effects.

### Emitter Structure

```c
typedef enum EmitterShape {
    EMITTER_SHAPE_POINT,
    EMITTER_SHAPE_LINE,
    EMITTER_SHAPE_CIRCLE,
    EMITTER_SHAPE_RECTANGLE
} EmitterShape;

typedef struct ParticleEmitter {
    // Position and shape
    Vector2 position;        // Center position of the emitter
    EmitterShape shape;      // Shape of the emission area
    float shape_param1;      // Shape parameter 1 (e.g., radius for circle, width for rectangle)
    float shape_param2;      // Shape parameter 2 (e.g., height for rectangle)
    
    // Emission properties
    float emission_rate;     // Particles per second
    float emission_timer;    // Internal timer for emission
    bool emitting;           // Whether the emitter is currently active
    int burst_count;         // Number of particles to emit in a burst
    
    // Particle properties
    Vector2 size_range;      // Min and max particle size
    Vector2 speed_range;     // Min and max particle speed
    Vector2 life_range;      // Min and max particle lifetime
    Vector2 angle_range;     // Min and max emission angle (in radians)
    float gravity;           // Gravity effect on particles
    float retardation;       // Speed reduction per update
    
    // Color properties
    Color start_color;       // Starting color (including alpha)
    Color end_color;         // Ending color (for color transition)
    bool color_transition;   // Whether to transition between colors
    
    // Behavior
    bool one_shot;           // Emit once and then stop
    bool attached;           // Whether the emitter moves with its parent object
    void* parent;            // Parent object to follow if attached
    
    // Reference to particle manager
    ParticleManager* manager;
} ParticleEmitter;
```

### Emitter Functions

```c
// Initialization and cleanup
ParticleEmitter* InitParticleEmitter(ParticleManager* manager, Vector2 position);
void DestroyParticleEmitter(ParticleEmitter* emitter);

// Configuration
void SetEmitterShape(ParticleEmitter* emitter, EmitterShape shape, float param1, float param2);
void SetEmitterRate(ParticleEmitter* emitter, float rate);
void SetParticleProperties(
    ParticleEmitter* emitter,
    Vector2 size_range, Vector2 speed_range,
    Vector2 life_range, Vector2 angle_range,
    float gravity, float retardation
);
void SetColorProperties(ParticleEmitter* emitter, Color start_color, Color end_color, bool transition);

// Operation
void StartEmitter(ParticleEmitter* emitter);
void StopEmitter(ParticleEmitter* emitter);
void EmitBurst(ParticleEmitter* emitter, int count);
void UpdateEmitter(ParticleEmitter* emitter, float delta_time);
```

## Particle Effects

Building on the Particle Emitter, pre-configured Particle Effects will be provided for common game events.

### Effect Types

1. **Explosion Effect**: Radial particle burst with configurable size and color
2. **Trail Effect**: Continuous emission following an object
3. **Impact Effect**: Quick burst at a specific location with directional bias
4. **Sparkle Effect**: Glittering particles with varying alpha
5. **Smoke Effect**: Slow-moving particles that grow in size over time
6. **Debris Effect**: Physics-based particles affected by gravity

### Effect Functions

```c
// Pre-configured effect creators
ParticleEmitter* CreateExplosionEffect(ParticleManager* manager, Vector2 position, float size, Color color);
ParticleEmitter* CreateTrailEffect(ParticleManager* manager, void* parent, float rate, Color color);
ParticleEmitter* CreateImpactEffect(ParticleManager* manager, Vector2 position, float angle, Color color);
ParticleEmitter* CreateSparkleEffect(ParticleManager* manager, Vector2 position, float radius, Color color);
ParticleEmitter* CreateSmokeEffect(ParticleManager* manager, Vector2 position, Color color);
ParticleEmitter* CreateDebrisEffect(ParticleManager* manager, Vector2 position, int count, Color color);
```

## Shadow System Integration

Maintaining compatibility with the existing Shadow system:

```c
// Shadow handling for particles
Shadow* CreateParticleShadow(Particle* particle, Color shadow_color);
void UpdateParticleShadow(Particle* particle);
void DrawParticleShadow(Particle* particle, Camera2D camera);
```

## Performance Optimization

### Batch Rendering

```c
// Enable batch rendering for particles
void EnableParticleBatchRendering(ParticleManager* manager, Texture2D texture);
void DisableParticleBatchRendering(ParticleManager* manager);

// Internal batch drawing function
void DrawParticlesBatch(ParticleManager* manager, Camera2D camera);
```

### Memory Management

```c
// Particle pool pre-allocation and recycling
void ResizeParticlePool(ParticleManager* manager, int new_capacity);
int GetInactiveParticleIndex(ParticleManager* manager);
void RecycleParticle(ParticleManager* manager, int index);
```

## Integration Points

### Game Object Integration

```c
// Attach emitters to game objects
void AttachEmitterToObject(ParticleEmitter* emitter, void* object);
void DetachEmitterFromObject(ParticleEmitter* emitter);

// Helper functions for common game objects
void AddExplosionToBlock(Block* block, float size_multiplier);
void AddTrailToBall(Ball* ball, Color color);
void AddEffectToLaserbeam(LaserBeam* laser);
```

### Effects System Integration

```c
// Create particles for various effects
void CreateBurningParticles(Effect* effect, float delta_time);
void CreateFreezingParticles(Effect* effect, float delta_time);
void CreateElectricityParticles(Effect* effect, float delta_time);
void CreateStunParticles(Effect* effect, float delta_time);
void CreateGravitationalPullParticles(Effect* effect, float delta_time);
```

## Debugging Support

```c
// Debug visualization
void DrawParticleDebug(ParticleManager* manager, Camera2D camera);
void DrawEmitterDebug(ParticleEmitter* emitter, Camera2D camera);

// Performance metrics
void LogParticleSystemMetrics(ParticleManager* manager);
```

## Implementation Notes

1. The Particle System will leverage Raylib's drawing functions for efficient rendering.
2. Particles will be managed in pre-allocated arrays to minimize memory allocation during gameplay.
3. Batch rendering will be used when possible to reduce draw calls.
4. The system will support both CPU-based and GPU-based particle rendering depending on configuration.
5. Particle emitters will handle the generation of particles, simplifying the creation of effects.
6. Pre-configured effects will be provided for common game events to reduce code duplication.

## Conclusion

The Particle System specification for the C/Raylib port builds upon the existing Python/Pygame implementation while enhancing it with additional features and optimizations. By introducing structured Particle Emitters and pre-configured effects, the system simplifies the creation of rich visual feedback while maintaining flexibility. The optimization strategies ensure the system performs well even with a large number of particles on screen. 