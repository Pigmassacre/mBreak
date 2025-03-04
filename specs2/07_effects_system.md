# Effects System Specification

## Overview

The Effects System provides a flexible framework for applying temporary visual, gameplay, and state modifications to game entities such as balls, blocks, and paddles. Effects are duration-based, parent-bound objects that encapsulate both visual feedback and gameplay mechanics changes.

## Core Architecture

### Effect Base Class

```c
typedef struct Effect {
    // Core properties
    GameObject* parent;          // Entity this effect is attached to
    Player* realOwner;           // The "real" owner of this effect (typically parent's owner)
    float duration;              // Total lifetime of effect in milliseconds
    float timePassed;            // Time accumulated since creation
    bool active;                 // Whether effect is currently active
    
    // Visual properties
    Texture2D* texture;          // Optional visual representation
    Rectangle srcRect;           // Source rectangle for texture
    Rectangle destRect;          // Destination rectangle (synced with parent)
    Color tint;                  // Color tint applied to visual
    
    // Management
    List* displayedPowerups;     // Powerups connected to this effect
    
    // Virtual methods (function pointers)
    void (*update)(struct Effect* self, float deltaTime);
    void (*draw)(struct Effect* self);
    void (*destroy)(struct Effect* self);
    void (*onKill)(struct Effect* self);
    
    // Event callbacks
    void (*onHitBall)(struct Effect* self, struct Ball* hitBall);
    void (*onHitBlock)(struct Effect* self, struct Block* hitBlock);
    void (*onHitPaddle)(struct Effect* self, struct Paddle* hitPaddle);
    void (*onHitWall)(struct Effect* self);
    
    // Effect-specific data (union for different effect types)
    union {
        struct BurningData* burning;
        struct FreezingData* freezing;
        struct StunData* stun;
        struct SpeedData* speed;
        struct ChargedData* charged;
        struct GravitationalPullData* gravitationalPull;
        struct SizeChangeData* sizeChange;
        struct FlashData* flash;
        struct ExplosionData* explosion;
        struct TransitionData* transition;
        struct TimeoutData* timeout;
    } data;
} Effect;
```

### Core Functions

```c
// Initialize a new effect attached to parent with specified duration
Effect* EffectInit(GameObject* parent, float duration);

// Update effect position, time tracking, and custom behavior
void EffectUpdate(Effect* effect, float deltaTime);

// Draw the effect's visual representation
void EffectDraw(Effect* effect);

// Clean up resources and remove effect from groups
void EffectDestroy(Effect* effect);

// Handle entity collisions
void EffectOnHitEntity(Effect* effect, GameObject* entity);
```

### Effect Group Management

```c
typedef struct EffectGroup {
    List* effects;           // List of active effects
    int count;               // Number of effects in group
} EffectGroup;

// Initialize a new effect group
EffectGroup* EffectGroupInit(void);

// Add effect to group
void EffectGroupAdd(EffectGroup* group, Effect* effect);

// Remove effect from group
void EffectGroupRemove(EffectGroup* group, Effect* effect);

// Update all effects in group
void EffectGroupUpdate(EffectGroup* group, float deltaTime);

// Draw all effects in group
void EffectGroupDraw(EffectGroup* group);

// Clean up all effects and resources
void EffectGroupDestroy(EffectGroup* group);
```

## Effect Types

### Burning Effect

The Burning effect applies damage over time to affected entities and can spread to nearby blocks.

```c
typedef struct BurningData {
    // Core properties
    float damagePerSecond;       // Damage applied per second (default: 2.0)
    
    // Particle system
    float particleSpawnTime;     // Time accumulator for particle spawning
    float particleSpawnRate;     // How often particles spawn (default: 75ms)
    int minParticlesPerSpawn;    // Minimum particles per spawn event (default: 3)
    int maxParticlesPerSpawn;    // Maximum particles per spawn event (default: 5)
    
    // Spreading mechanics
    float spreadCheckTime;       // Time accumulator for spread checking
    float spreadCheckRate;       // How often to check for spread (default: 500ms)
    float spreadRange;           // Maximum spread distance (default: 15px)
    float spreadChance;          // Probability of spreading (default: 0.2)
    float spreadDurationFactor;  // Duration reduction factor (default: 0.8)
} BurningData;

// Create a new burning effect
Effect* BurningEffectCreate(GameObject* parent, float duration);

// Find neighboring blocks that can catch fire
Block** BurningEffectFindNeighbors(BurningEffect* effect);

// Attempt to spread fire to neighboring blocks
void BurningEffectSpread(BurningEffect* effect);

// Custom update function
void BurningEffectUpdate(BurningEffect* effect, float deltaTime);

// Handle hitting a block
void BurningEffectOnHitBlock(BurningEffect* effect, Block* hitBlock);
```

### Freezing Effect

The Freezing effect reduces movement speed and applies visual feedback to affected entities.

```c
typedef struct FreezingData {
    // Movement modification
    float maxSpeedReduction;     // How much to reduce speed (default: 0.5)
    bool parentIsPaddle;         // Quick access flag for paddle-specific behavior
    
    // Visual properties
    float particleSpawnTime;     // Time accumulator for particle spawning
    float particleSpawnRate;     // How often particles spawn (default: 100ms)
    
    // Auto-reposition timer for visual effect
    float repositionTime;        // Time accumulator for repositioning visual
    float repositionRate;        // How often to reposition (default: 200ms)
} FreezingData;

// Create a new freezing effect
Effect* FreezingEffectCreate(GameObject* parent, float duration);

// Create final image for visual representation
void FreezingEffectCreateFinalImage(FreezingEffect* effect);

// Custom update function
void FreezingEffectUpdate(FreezingEffect* effect, float deltaTime);

// Handle cleanup when effect ends
void FreezingEffectOnKill(FreezingEffect* effect);
```

### Charged Effect

The Charged effect implements chain lightning that jumps between blocks, dealing chain damage.

```c
typedef struct ChargedData {
    // Chain lightning properties
    float baseDamage;            // Base damage amount (default: 10.0)
    float currentDamage;         // Current damage (reduces with each jump)
    float damageReduction;       // Damage reduction per jump (default: 0.7)
    int chainJumps;              // Maximum number of jumps (default: 3)
    int jumpsRemaining;          // Jumps left in current chain
    
    // Chain state
    bool chaining;               // Whether chain is active
    float chainTime;             // Time accumulator for chain timing
    float chainDelay;            // Delay between jumps (default: 150ms)
    
    // Chain visualization
    Vector2* lightningPath;      // Points in lightning path
    int pathPointCount;          // Number of points in path
    float lightningFade;         // Fade factor for lightning visual
    
    // Targeting
    Block* currentBlock;         // Current block in chain
    List* hitBlocks;             // Blocks already hit in this chain
    float searchRadius;          // Search radius for next block (default: 120px)
} ChargedData;

// Create a new charged effect
Effect* ChargedEffectCreate(GameObject* parent, float duration);

// Find next block to chain to
Block* ChargedEffectFindNextTarget(ChargedEffect* effect, Block* currentBlock);

// Start chain lightning sequence
void ChargedEffectStartChain(ChargedEffect* effect, Block* startBlock);

// Spawn lightning particles
void ChargedEffectSpawnParticles(ChargedEffect* effect, Block* block);

// Custom update function
void ChargedEffectUpdate(ChargedEffect* effect, float deltaTime);

// Custom draw function for lightning path
void ChargedEffectDraw(ChargedEffect* effect);

// Handle hitting a block
void ChargedEffectOnHitBlock(ChargedEffect* effect, Block* hitBlock);
```

### Gravitational Pull Effect

The Gravitational Pull effect creates a force field that attracts or repels entities.

```c
typedef struct GravitationalPullData {
    // Force properties
    float strength;              // Force strength (default: 15.0)
    float radiusOfEffect;        // Radius of force field (default: 150px)
    bool isRepulsive;            // Whether force repels (false = attractive)
    
    // Visual properties
    float particleSpawnTime;     // Time accumulator for particle spawning
    float particleSpawnRate;     // How often particles spawn (default: 50ms)
    int particlesPerSpawn;       // Particles per spawn event (default: 3)
    
    // Effect visualization
    float fieldOpacity;          // Opacity of force field visual (default: 0.2)
    float fieldPulsation;        // Field pulsation speed (default: 0.5)
} GravitationalPullData;

// Create a new gravitational pull effect
Effect* GravitationalPullEffectCreate(GameObject* parent, float duration, bool isRepulsive);

// Calculate force on a given entity
Vector2 GravitationalPullEffectCalculateForce(GravitationalPullEffect* effect, GameObject* entity);

// Apply force to all relevant entities
void GravitationalPullEffectApplyForces(GravitationalPullEffect* effect);

// Custom update function
void GravitationalPullEffectUpdate(GravitationalPullEffect* effect, float deltaTime);

// Custom draw function for force field visualization
void GravitationalPullEffectDraw(GravitationalPullEffect* effect);
```

### Speed Effect

The Speed effect modifies the speed of affected entities.

```c
typedef struct SpeedData {
    // Speed modification
    float speedMultiplier;       // Speed multiplier (default: 2.0)
    float originalSpeed;         // Original speed before effect
} SpeedData;

// Create a new speed effect
Effect* SpeedEffectCreate(GameObject* parent, float duration, float speedMultiplier);

// Custom update function
void SpeedEffectUpdate(SpeedEffect* effect, float deltaTime);

// Handle cleanup when effect ends
void SpeedEffectOnKill(SpeedEffect* effect);
```

### Stun Effect

The Stun effect temporarily disables movement and adds visual feedback.

```c
typedef struct StunData {
    // Movement modification
    float maxSpeedReduction;     // How much to reduce speed (default: 1.0 = full stop)
    float originalMaxSpeed;      // Original max speed before effect
    
    // Callback
    void (*onKillFunction)(void*); // Optional function to call when effect ends
    
    // Visual properties
    float particleSpawnTime;     // Time accumulator for particle spawning
    float particleSpawnRate;     // How often particles spawn (default: 100ms)
} StunData;

// Create a new stun effect
Effect* StunEffectCreate(GameObject* parent, float duration, void (*onKillFunction)(void*));

// Create final image for visual representation
void StunEffectCreateFinalImage(StunEffect* effect);

// Custom update function
void StunEffectUpdate(StunEffect* effect, float deltaTime);

// Handle cleanup when effect ends
void StunEffectOnKill(StunEffect* effect);
```

### Size Change Effect

The Size Change effect modifies the scale of affected entities.

```c
typedef struct SizeChangeData {
    // Size modification
    float scaleFactor;           // Scale multiplier (default: varies by entity)
    Vector2 originalSize;        // Original size before effect
    Vector2 targetSize;          // Target size with scale applied
    
    // Transition
    bool useTransition;          // Whether to transition smoothly
    float transitionSpeed;       // Transition speed (default: 0.1)
} SizeChangeData;

// Create a new size change effect
Effect* SizeChangeEffectCreate(GameObject* parent, float duration, float scaleFactor);

// Apply size change immediately
void SizeChangeEffectApplyImmediate(SizeChangeEffect* effect);

// Apply size change with transition
void SizeChangeEffectApplyTransition(SizeChangeEffect* effect, float deltaTime);

// Custom update function
void SizeChangeEffectUpdate(SizeChangeEffect* effect, float deltaTime);

// Handle cleanup when effect ends
void SizeChangeEffectOnKill(SizeChangeEffect* effect);
```

### Flash Effect

The Flash effect provides visual feedback through color transitions.

```c
typedef struct FlashData {
    // Color transition
    Color startColor;            // Initial flash color (default: white)
    Color endColor;              // Final color (default: transparent)
    Color currentColor;          // Current transition color
    float transitionSpeed;       // Color transition speed (default: 0.07)
} FlashData;

// Create a new flash effect
Effect* FlashEffectCreate(GameObject* parent, float duration);

// Custom update function
void FlashEffectUpdate(FlashEffect* effect, float deltaTime);

// Custom draw function
void FlashEffectDraw(FlashEffect* effect);
```

### Explosion Effect

The Explosion effect creates a visual explosion with optional area damage.

```c
typedef struct ExplosionData {
    // Animation
    Texture2D* spriteSheet;      // Explosion sprite sheet
    int frameWidth;              // Width of each frame
    int frameHeight;             // Height of each frame
    int currentFrame;            // Current animation frame
    int totalFrames;             // Total animation frames
    float frameTime;             // Time per frame
    float frameTimer;            // Time accumulator for animation
    
    // Damage
    float damageAmount;          // Damage to apply to nearby entities
    float damageRadius;          // Radius of damage effect
    bool hasDamaged;             // Whether damage has been applied
} ExplosionData;

// Create a new explosion effect
Effect* ExplosionEffectCreate(GameObject* parent, float duration);

// Update animation frame
void ExplosionEffectUpdateAnimation(ExplosionEffect* effect, float deltaTime);

// Apply area damage
void ExplosionEffectApplyDamage(ExplosionEffect* effect);

// Custom update function
void ExplosionEffectUpdate(ExplosionEffect* effect, float deltaTime);

// Custom draw function
void ExplosionEffectDraw(ExplosionEffect* effect);
```

### Transition Effect

The Transition effect manages screen transitions between game states.

```c
typedef struct TransitionData {
    // Transition properties
    TransitionType type;         // Type of transition (fade, slide, etc.)
    GameState targetState;       // Game state to transition to
    float progress;              // Transition progress (0-1)
    
    // Visual properties
    Color startColor;            // Start color (default: transparent)
    Color endColor;              // End color (default: black)
    Color currentColor;          // Current transition color
} TransitionData;

// Create a new transition effect
Effect* TransitionEffectCreate(GameObject* parent, float duration, TransitionType type, GameState targetState);

// Custom update function
void TransitionEffectUpdate(TransitionEffect* effect, float deltaTime);

// Custom draw function
void TransitionEffectDraw(TransitionEffect* effect);

// Handle completion of transition
void TransitionEffectOnKill(TransitionEffect* effect);
```

### Timeout Effect

The Timeout effect manages entity lifetime and cleanup.

```c
typedef struct TimeoutData {
    bool hasTimedOut;            // Whether timeout has occurred
} TimeoutData;

// Create a new timeout effect
Effect* TimeoutEffectCreate(GameObject* parent, float duration);

// Custom update function
void TimeoutEffectUpdate(TimeoutEffect* effect, float deltaTime);

// Handle cleanup when effect ends
void TimeoutEffectOnKill(TimeoutEffect* effect);
```

## Powerup Integration

Effects are typically applied through powerups, which act as the delivery mechanism:

```c
void PowerupShareEffect(Powerup* powerup, GameObject* entity, EffectType effectType) {
    // Find all relevant entities to apply the effect to
    List* targets = PowerupFindTargets(powerup, entity);
    
    // Create and connect the effect to each target
    for (int i = 0; i < targets->count; i++) {
        GameObject* target = targets->items[i];
        
        // Skip entities with timeout effect
        if (EntityHasEffect(target, EFFECT_TIMEOUT)) {
            continue;
        }
        
        // Create appropriate effect
        Effect* effect = NULL;
        switch (effectType) {
            case EFFECT_BURNING:
                effect = BurningEffectCreate(target, BURNING_DURATION);
                break;
            case EFFECT_FREEZING:
                effect = FreezingEffectCreate(target, FREEZING_DURATION);
                break;
            // ... other effect types
        }
        
        // Connect effect to entity
        if (effect) {
            effect->realOwner = entity->owner;
            entity->owner->effectGroup->Add(effect);
            entity->owner->AddDisplayedPowerup(powerup->type, effect);
        }
    }
}
```

## Performance Considerations

### Memory Management

```c
// Efficient memory pool for effects
typedef struct EffectPool {
    Effect* effects;             // Pre-allocated array of effects
    int capacity;                // Total capacity
    int count;                   // Currently active count
    bool* active;                // Active flags for each slot
} EffectPool;

// Initialize a memory pool for effects
EffectPool* EffectPoolInit(int capacity);

// Get an effect from the pool
Effect* EffectPoolGet(EffectPool* pool);

// Return an effect to the pool
void EffectPoolReturn(EffectPool* pool, Effect* effect);
```

### Rendering Optimization

```c
// Batch rendering for effects
void EffectGroupBatchDraw(EffectGroup* group) {
    // Sort effects by texture to minimize texture binding
    SortEffectsByTexture(group->effects);
    
    // Begin batch drawing
    BeginDrawing();
    
    Texture2D currentTexture = { 0 };
    for (int i = 0; i < group->count; i++) {
        Effect* effect = group->effects->items[i];
        
        // Skip effects without visual representation
        if (!effect->texture) continue;
        
        // If texture changed, end previous batch and start new one
        if (effect->texture->id != currentTexture.id) {
            if (currentTexture.id != 0) EndDrawing();
            currentTexture = *effect->texture;
            BeginMode2D(camera);
        }
        
        // Draw effect
        DrawTexturePro(
            currentTexture,
            effect->srcRect,
            effect->destRect,
            (Vector2){ 0, 0 },
            0.0f,
            effect->tint
        );
    }
    
    // End final batch
    EndDrawing();
}
```

## Sound System Integration

```c
// Play effect sound with positional audio
void EffectPlaySound(Effect* effect, Sound sound) {
    // Calculate volume based on distance from camera
    Vector2 effectPos = (Vector2){ effect->destRect.x, effect->destRect.y };
    Vector2 cameraPos = GetCameraPosition();
    float distance = Vector2Distance(effectPos, cameraPos);
    
    // Apply distance attenuation model
    float volume = Clamp(1.0f - (distance / MAX_SOUND_DISTANCE), 0.0f, 1.0f);
    volume *= GetMasterVolume();
    
    // Play sound with calculated volume
    SetSoundVolume(sound, volume);
    PlaySound(sound);
}
```

## Event System

The effects system implements event listeners that respond to gameplay events:

```c
// Register event handlers for an effect
void EffectRegisterEvents(Effect* effect) {
    // Register collision callbacks
    if (effect->onHitBall)
        RegisterCollisionCallback(effect->parent, ENTITY_BALL, effect->onHitBall);
    
    if (effect->onHitBlock)
        RegisterCollisionCallback(effect->parent, ENTITY_BLOCK, effect->onHitBlock);
    
    if (effect->onHitPaddle)
        RegisterCollisionCallback(effect->parent, ENTITY_PADDLE, effect->onHitPaddle);
    
    if (effect->onHitWall)
        RegisterCollisionCallback(effect->parent, ENTITY_WALL, effect->onHitWall);
}

// Unregister event handlers for an effect
void EffectUnregisterEvents(Effect* effect) {
    // Unregister all collision callbacks
    UnregisterAllCollisionCallbacks(effect->parent);
}
```

## Particle System Integration

Effects frequently use particles for visual feedback. The particle system is tightly integrated:

```c
// Spawn effect particles
void EffectSpawnParticles(Effect* effect, int count, Color color, float speed, float size) {
    for (int i = 0; i < count; i++) {
        // Calculate random angle
        float angle = GetRandomFloat(0, 2 * PI);
        
        // Calculate random velocity vector
        Vector2 velocity = {
            cosf(angle) * speed * GetRandomFloat(0.8f, 1.2f),
            sinf(angle) * speed * GetRandomFloat(0.8f, 1.2f)
        };
        
        // Create particle
        Particle* particle = ParticleCreate(
            (Vector2){ effect->destRect.x + effect->destRect.width/2, 
                      effect->destRect.y + effect->destRect.height/2 },
            velocity,
            color,
            size,
            GetRandomFloat(0.5f, 1.0f)  // lifetime
        );
        
        // Add to particle system
        ParticleSystemAdd(particle);
    }
}
```

## Camera System Integration

```c
// Convert world position to screen position
Vector2 EffectWorldToScreen(Effect* effect) {
    Camera2D camera = GetCamera();
    Vector2 worldPos = { effect->destRect.x, effect->destRect.y };
    return GetWorldToScreen2D(worldPos, camera);
}

// Convert screen position to world position
Vector2 EffectScreenToWorld(Vector2 screenPos) {
    Camera2D camera = GetCamera();
    return GetScreenToWorld2D(screenPos, camera);
}
```

## Conclusion

The Effects System is a core gameplay mechanic that provides dynamic visual feedback and gameplay alterations. Through its modular design, it allows for easy addition of new effect types while maintaining consistent behavior through the base Effect class. The integration with other game systems such as particles, sound, and collision detection creates a cohesive and engaging player experience. 