# Combat Mechanics Overview

## System Components

### Damage System
```c
typedef struct DamageInfo {
    float amount;
    DamageType type;
    Entity* source;
    Entity* target;
    bool isCritical;
    float multiplier;
} DamageInfo;

typedef enum DamageType {
    DAMAGE_NORMAL,
    DAMAGE_FIRE,
    DAMAGE_FROST,
    DAMAGE_ELECTRIC,
    DAMAGE_EXPLOSIVE
} DamageType;
```

### Combat Effects
```c
typedef struct CombatEffect {
    EffectType type;
    float duration;
    float strength;
    Entity* source;
    bool isStacking;
    
    // Effect-specific data
    union {
        BurningData burning;
        FreezingData freezing;
        StunData stun;
        // Other effect data
    } data;
} CombatEffect;
```

### Collision System
```c
typedef struct CollisionInfo {
    Entity* entityA;
    Entity* entityB;
    Vector2 point;
    Vector2 normal;
    float penetration;
    bool isResolved;
} CollisionInfo;
```

## Core Mechanics

### Damage Application
```c
void ApplyDamage(Entity* target, DamageInfo damage) {
    // Calculate final damage
    float finalDamage = CalculateDamage(damage);
    
    // Apply damage modifiers
    finalDamage = ApplyResistances(target, finalDamage, damage.type);
    finalDamage = ApplyBuffs(target, finalDamage);
    
    // Apply damage to target
    target->health -= finalDamage;
    
    // Trigger effects
    TriggerDamageEffects(target, damage);
    
    // Check for destruction
    if (target->health <= 0) {
        DestroyEntity(target);
    }
}
```

### Effect Application
```c
void ApplyCombatEffect(Entity* target, CombatEffect effect) {
    // Check for immunity
    if (IsImmune(target, effect.type)) {
        return;
    }
    
    // Check for existing effect
    CombatEffect* existing = FindEffect(target, effect.type);
    if (existing) {
        if (effect.isStacking) {
            StackEffect(existing, effect);
        } else {
            RefreshEffect(existing, effect);
        }
    } else {
        AddNewEffect(target, effect);
    }
}
```

### Collision Resolution
```c
void ResolveCollision(CollisionInfo collision) {
    // Separate entities
    SeparateEntities(collision);
    
    // Calculate collision response
    Vector2 response = CalculateResponse(collision);
    
    // Apply response forces
    ApplyCollisionForce(collision.entityA, response);
    ApplyCollisionForce(collision.entityB, Vector2Negate(response));
    
    // Trigger collision effects
    TriggerCollisionEffects(collision);
}
```

## Effect Types

### Burning Effect
```c
typedef struct BurningData {
    float damagePerSecond;
    float spreadChance;
    float spreadRadius;
    Color flameColor;
} BurningData;

void UpdateBurningEffect(Entity* entity, BurningData* data, float deltaTime) {
    // Apply damage over time
    DamageInfo damage = {
        .amount = data->damagePerSecond * deltaTime,
        .type = DAMAGE_FIRE,
        .source = entity
    };
    ApplyDamage(entity, damage);
    
    // Try to spread
    if (RandomFloat() < data->spreadChance) {
        SpreadBurningEffect(entity, data);
    }
    
    // Update visual effects
    UpdateFireParticles(entity, data);
}
```

### Freezing Effect
```c
typedef struct FreezingData {
    float slowFactor;
    float freezeDuration;
    bool isFullyFrozen;
} FreezingData;

void UpdateFreezingEffect(Entity* entity, FreezingData* data) {
    // Apply movement reduction
    entity->velocity = Vector2Scale(entity->velocity, data->slowFactor);
    
    // Check for full freeze
    if (data->isFullyFrozen) {
        entity->velocity = VECTOR2_ZERO;
        entity->canMove = false;
    }
    
    // Update visual effects
    UpdateFrostParticles(entity, data);
}
```

## Combat Feedback

### Visual Feedback
```c
void CreateCombatFeedback(Entity* entity, DamageInfo damage) {
    // Create hit flash
    CreateHitFlash(entity, damage.type);
    
    // Spawn damage numbers
    SpawnDamageNumber(damage.amount, entity->position, damage.isCritical);
    
    // Create particle effects
    CreateHitParticles(entity, damage);
    
    // Add screen shake if significant damage
    if (damage.amount > SCREEN_SHAKE_THRESHOLD) {
        AddScreenShake(damage.amount * 0.1f);
    }
}
```

### Audio Feedback
```c
void PlayCombatSounds(Entity* entity, DamageInfo damage) {
    // Play hit sound
    PlayHitSound(damage.type);
    
    // Play damage variation
    if (damage.isCritical) {
        PlayCriticalHitSound();
    }
    
    // Play entity-specific sound
    PlayEntityHitSound(entity);
}
```

## Special Attacks

### Attack Definition
```c
typedef struct SpecialAttack {
    AttackType type;
    float energyCost;
    float cooldown;
    float duration;
    
    // Attack properties
    struct {
        float damage;
        float radius;
        float speed;
        // Other properties
    } properties;
    
    // Visual effects
    struct {
        const char* particleEffect;
        const char* soundEffect;
        Color effectColor;
    } effects;
} SpecialAttack;
```

### Attack Execution
```c
void ExecuteSpecialAttack(Entity* source, SpecialAttack* attack) {
    // Check requirements
    if (!CanUseSpecialAttack(source, attack)) {
        return;
    }
    
    // Consume resources
    source->energy -= attack->energyCost;
    
    // Create attack entity
    Entity* attackEntity = CreateAttackEntity(attack);
    
    // Setup attack properties
    SetupAttackProperties(attackEntity, attack);
    
    // Create visual effects
    CreateAttackEffects(attackEntity, attack);
    
    // Start attack behavior
    StartAttackBehavior(attackEntity);
}
```

## Memory Management

### Effect Pool
```c
typedef struct EffectPool {
    CombatEffect* effects;
    int capacity;
    int count;
} EffectPool;

CombatEffect* GetEffectFromPool(EffectPool* pool) {
    if (pool->count >= pool->capacity) {
        ExpandEffectPool(pool);
    }
    return &pool->effects[pool->count++];
}
```

### Particle Management
```c
typedef struct ParticleManager {
    Particle* particles;
    int capacity;
    int count;
    float updateInterval;
} ParticleManager;

void UpdateCombatParticles(ParticleManager* manager, float deltaTime) {
    for (int i = 0; i < manager->count; i++) {
        UpdateParticle(&manager->particles[i], deltaTime);
        if (IsParticleDead(&manager->particles[i])) {
            RemoveParticle(manager, i--);
        }
    }
}
```

## Debug Features

### Combat Visualization
```c
void DrawCombatDebug(void) {
    if (!IsDebugMode()) return;
    
    // Draw damage numbers
    DrawDamageNumbers();
    
    // Draw effect areas
    DrawEffectAreas();
    
    // Draw collision info
    DrawCollisionInfo();
    
    // Draw attack ranges
    DrawAttackRanges();
}
``` 