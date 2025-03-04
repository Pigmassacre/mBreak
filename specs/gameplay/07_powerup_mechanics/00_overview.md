# Power-up Mechanics Overview

## System Components

### Power-up Definition
```c
typedef struct PowerUp {
    PowerUpType type;
    float duration;
    float strength;
    bool isActive;
    Entity* owner;
    
    // Visual properties
    struct {
        const char* sprite;
        Color tint;
        float scale;
        float rotationSpeed;
    } visual;
    
    // Effect properties
    struct {
        const char* particleEffect;
        const char* activationSound;
        const char* deactivationSound;
    } effects;
} PowerUp;

typedef enum PowerUpType {
    POWERUP_SPEED,
    POWERUP_STRENGTH,
    POWERUP_SHIELD,
    POWERUP_MULTIBALL,
    POWERUP_LASER,
    POWERUP_MAGNET,
    POWERUP_EXPAND,
    POWERUP_SHRINK
} PowerUpType;
```

### Power-up Manager
```c
typedef struct PowerUpManager {
    PowerUp* activePowerUps;
    int activeCount;
    int capacity;
    
    // Spawn settings
    struct {
        float spawnInterval;
        float spawnChance;
        Vector2 spawnArea;
    } spawn;
    
    // Global settings
    struct {
        float defaultDuration;
        float maxActivePowerUps;
        bool allowStacking;
    } settings;
} PowerUpManager;
```

## Core Mechanics

### Power-up Spawning
```c
void SpawnPowerUp(PowerUpManager* manager, Vector2 position) {
    // Select random power-up type
    PowerUpType type = GetRandomPowerUpType();
    
    // Create power-up entity
    PowerUp* powerUp = CreatePowerUp(type);
    
    // Set position and initialize
    powerUp->position = position;
    InitializePowerUp(powerUp);
    
    // Add to manager
    AddPowerUpToManager(manager, powerUp);
    
    // Create spawn effects
    CreateSpawnEffects(powerUp);
}
```

### Power-up Collection
```c
void CollectPowerUp(Entity* collector, PowerUp* powerUp) {
    // Check if can collect
    if (!CanCollectPowerUp(collector, powerUp)) {
        return;
    }
    
    // Apply power-up effect
    ApplyPowerUpEffect(collector, powerUp);
    
    // Start duration timer
    StartPowerUpTimer(powerUp);
    
    // Create collection effects
    CreateCollectionEffects(powerUp);
    
    // Update collector state
    UpdateCollectorState(collector, powerUp);
}
```

### Power-up Effects

#### Speed Boost
```c
void ApplySpeedBoost(Entity* entity, PowerUp* powerUp) {
    // Calculate speed multiplier
    float speedMultiplier = 1.0f + powerUp->strength;
    
    // Apply to entity
    entity->speed *= speedMultiplier;
    
    // Create speed trail effect
    CreateSpeedTrail(entity, powerUp->strength);
}
```

#### Shield Effect
```c
void ApplyShieldEffect(Entity* entity, PowerUp* powerUp) {
    // Create shield component
    Shield* shield = CreateShield(powerUp->strength);
    
    // Attach to entity
    AttachShield(entity, shield);
    
    // Setup shield visuals
    SetupShieldVisuals(shield, powerUp->visual.tint);
}
```

#### Multiball Effect
```c
void ApplyMultiballEffect(Entity* entity, PowerUp* powerUp) {
    // Calculate number of extra balls
    int extraBalls = (int)(powerUp->strength);
    
    // Create additional balls
    for (int i = 0; i < extraBalls; i++) {
        Ball* newBall = CloneBall(GetMainBall());
        
        // Randomize direction
        newBall->direction = GetRandomDirection();
        
        // Add to game
        AddBallToGame(newBall);
    }
}
```

## Power-up Behaviors

### Movement Patterns
```c
void UpdatePowerUpMovement(PowerUp* powerUp, float deltaTime) {
    switch (powerUp->type) {
        case POWERUP_SPEED:
            UpdateFloatingMovement(powerUp, deltaTime);
            break;
        case POWERUP_MAGNET:
            UpdateMagneticMovement(powerUp, deltaTime);
            break;
        default:
            UpdateDefaultMovement(powerUp, deltaTime);
    }
}
```

### Visual Effects
```c
void UpdatePowerUpVisuals(PowerUp* powerUp, float deltaTime) {
    // Update rotation
    powerUp->rotation += powerUp->visual.rotationSpeed * deltaTime;
    
    // Update scale animation
    UpdateScalePulse(powerUp, deltaTime);
    
    // Update particle effects
    UpdatePowerUpParticles(powerUp, deltaTime);
    
    // Update glow effect
    UpdateGlowEffect(powerUp, deltaTime);
}
```

## Memory Management

### Power-up Pool
```c
typedef struct PowerUpPool {
    PowerUp* pool;
    int capacity;
    int count;
    bool* active;
} PowerUpPool;

PowerUp* GetPowerUpFromPool(PowerUpPool* pool) {
    for (int i = 0; i < pool->capacity; i++) {
        if (!pool->active[i]) {
            pool->active[i] = true;
            pool->count++;
            return &pool->pool[i];
        }
    }
    return NULL;
}
```

### Resource Management
```c
void LoadPowerUpResources(void) {
    // Load sprites
    LoadPowerUpSprites();
    
    // Load sound effects
    LoadPowerUpSounds();
    
    // Load particle effects
    LoadPowerUpParticles();
    
    // Initialize pools
    InitializePowerUpPool();
}
```

## Debug Features

### Power-up Debugging
```c
void DrawPowerUpDebug(void) {
    if (!IsDebugMode()) return;
    
    // Draw power-up spawn areas
    DrawSpawnAreas();
    
    // Draw power-up ranges
    DrawPowerUpRanges();
    
    // Draw active power-up info
    DrawActivePowerUpInfo();
    
    // Draw collection hitboxes
    DrawCollectionHitboxes();
}
```

### Testing Tools
```c
void DebugSpawnPowerUp(PowerUpType type, Vector2 position) {
    PowerUp* powerUp = CreatePowerUp(type);
    powerUp->position = position;
    
    // Override normal spawn rules
    powerUp->duration *= 2.0f;  // Double duration for testing
    powerUp->strength *= 1.5f;  // Increase strength for testing
    
    AddPowerUpToManager(GetPowerUpManager(), powerUp);
}
``` 