# Attack System

## Overview

The attack system in mBreak provides offensive capabilities to players, allowing them to launch special attacks against opponents. These attacks add strategic depth to the gameplay and create opportunities for comebacks or aggressive plays. This specification details how attacks are implemented in the Python codebase and how they should be ported to C with Raylib.

## Current Implementation (Python + Pygame)

### Core Components

#### Attack Base Class

The base attack class (`objects/attacks/attack.py`) provides a foundation for all attack types with:
- Common properties (position, velocity, damage, etc.)
- Lifecycle management (creation, update, destruction)
- Collision detection with game entities
- Visual representation

#### Attack Types

The game implements several attack types:

1. **Laser** (`objects/attacks/laser.py`): A direct beam attack that travels in a straight line
2. **Missile Storm** (`objects/attacks/missilestorm.py`): Multiple projectiles that seek or rain down on targets
3. **Missile** (`objects/missile.py`): Single guided projectile
4. **Laser Beam** (`objects/laserbeam.py`): Sustained beam attack

#### Attack Integration

Attacks are integrated with:
- Player objects for ownership and targeting
- Collision system for hit detection
- Effect system for visual feedback
- Sound system for audio feedback

### Implementation Details

#### Attack Creation

Attacks are instantiated by player actions or power-ups:

```python
# Example simplified attack creation
laser_attack = Laser(position, direction, owner)
attacks_group.add(laser_attack)
```

#### Attack Update Cycle

Attacks follow a standard update cycle:

1. Update position based on velocity/trajectory
2. Check for collisions with game objects
3. Apply effects/damage on collision
4. Update visual representation
5. Check lifetime/expiration conditions

#### Collision Handling

Attacks use Pygame's sprite collision system:

```python
# Example collision detection
hit_targets = pygame.sprite.spritecollide(self, target_group, False)
for target in hit_targets:
    self.apply_effect(target)
```

## Port Implementation (C + Raylib)

### Core Attack Structs

```c
// Attack types
typedef enum AttackType {
    ATTACK_LASER,
    ATTACK_MISSILE,
    ATTACK_MISSILESTORM,
    ATTACK_LASERBEAM
} AttackType;

// Base attack structure
typedef struct Attack {
    AttackType type;        // Type of attack
    Vector2 position;       // Current position
    Vector2 velocity;       // Movement velocity
    float rotation;         // Rotation angle in degrees
    float lifetime;         // Remaining lifetime in seconds
    float maxLifetime;      // Maximum lifetime
    float damage;           // Damage value
    int ownerId;            // ID of the player who created the attack
    Rectangle hitbox;       // Collision rectangle
    Texture2D texture;      // Visual representation
    Color tint;             // Color tint
    bool active;            // Whether the attack is active
} Attack;

// Specialized attack structures
typedef struct LaserAttack {
    Attack base;
    float length;           // Beam length
    float width;            // Beam width
    bool piercing;          // Whether it can hit multiple targets
} LaserAttack;

typedef struct MissileAttack {
    Attack base;
    Vector2 targetPosition; // Homing target position
    float turnSpeed;        // How quickly it can change direction
    float acceleration;     // Acceleration rate
    float maxSpeed;         // Maximum speed
    bool homing;            // Whether it homes in on targets
} MissileAttack;

typedef struct MissileStormAttack {
    Attack base;
    int missileCount;       // Number of missiles in the storm
    MissileAttack* missiles; // Array of individual missiles
    float spreadAngle;      // Angle of spread for the missiles
    float launchDelay;      // Delay between missile launches
} MissileStormAttack;

typedef struct LaserBeamAttack {
    Attack base;
    float width;            // Beam width
    float maxLength;        // Maximum beam length
    float currentLength;    // Current beam length
    float growthRate;       // How fast the beam extends
    float sustainTime;      // How long the beam is sustained at full length
    bool sustaining;        // Whether the beam is in sustain phase
} LaserBeamAttack;
```

### Attack Management System

```c
typedef struct AttackSystem {
    Attack** attacks;       // Array of all active attacks
    int count;              // Number of active attacks
    int capacity;           // Maximum capacity
    Texture2D* textures;    // Attack textures
    int textureCount;       // Number of textures
} AttackSystem;

// System initialization and cleanup
AttackSystem* InitAttackSystem(int maxAttacks);
void FreeAttackSystem(AttackSystem* system);

// Attack creation
int CreateLaserAttack(AttackSystem* system, Vector2 position, Vector2 direction, float damage, int ownerId);
int CreateMissileAttack(AttackSystem* system, Vector2 position, Vector2 targetPosition, float damage, int ownerId);
int CreateMissileStormAttack(AttackSystem* system, Vector2 position, Vector2 targetPosition, int missileCount, float damage, int ownerId);
int CreateLaserBeamAttack(AttackSystem* system, Vector2 position, Vector2 direction, float damage, int ownerId);

// Attack management
void UpdateAttacks(AttackSystem* system, float deltaTime);
void DrawAttacks(AttackSystem* system);
void DeactivateAttack(AttackSystem* system, int attackId);
void ClearAllAttacks(AttackSystem* system);
```

### Collision Detection

```c
// Check collision between an attack and game entities
bool CheckAttackCollision(Attack* attack, Rectangle entityHitbox, int entityId, int entityType);

// Process collision effects
void ProcessAttackCollision(Attack* attack, int entityId, int entityType, Vector2 collisionPoint);

// Get targets in attack area (for area attacks)
int GetTargetsInArea(Attack* attack, Rectangle* entityHitboxes, int* entityIds, int entityCount, int* hitEntityIds);
```

## Attack Update and Rendering

### Laser Attack

```c
void UpdateLaserAttack(LaserAttack* laser, float deltaTime) {
    // Update position based on velocity
    laser->base.position.x += laser->base.velocity.x * deltaTime;
    laser->base.position.y += laser->base.velocity.y * deltaTime;
    
    // Update lifetime
    laser->base.lifetime -= deltaTime;
    if (laser->base.lifetime <= 0) {
        laser->base.active = false;
    }
    
    // Update hitbox
    UpdateLaserHitbox(laser);
}

void DrawLaserAttack(LaserAttack* laser) {
    // Draw laser beam
    DrawLineEx(
        laser->base.position,
        (Vector2){
            laser->base.position.x + cosf(laser->base.rotation) * laser->length,
            laser->base.position.y + sinf(laser->base.rotation) * laser->length
        },
        laser->width,
        laser->base.tint
    );
}
```

### Missile Attack

```c
void UpdateMissileAttack(MissileAttack* missile, float deltaTime) {
    if (missile->homing) {
        // Calculate direction to target
        Vector2 direction = {
            missile->targetPosition.x - missile->base.position.x,
            missile->targetPosition.y - missile->base.position.y
        };
        
        // Normalize direction
        float length = sqrtf(direction.x * direction.x + direction.y * direction.y);
        if (length > 0) {
            direction.x /= length;
            direction.y /= length;
        }
        
        // Adjust velocity towards target
        missile->base.velocity.x += direction.x * missile->acceleration * deltaTime;
        missile->base.velocity.y += direction.y * missile->acceleration * deltaTime;
        
        // Limit speed
        float speed = sqrtf(missile->base.velocity.x * missile->base.velocity.x + 
                            missile->base.velocity.y * missile->base.velocity.y);
        if (speed > missile->maxSpeed) {
            missile->base.velocity.x = (missile->base.velocity.x / speed) * missile->maxSpeed;
            missile->base.velocity.y = (missile->base.velocity.y / speed) * missile->maxSpeed;
        }
        
        // Update rotation to match velocity
        missile->base.rotation = atan2f(missile->base.velocity.y, missile->base.velocity.x);
    }
    
    // Update position
    missile->base.position.x += missile->base.velocity.x * deltaTime;
    missile->base.position.y += missile->base.velocity.y * deltaTime;
    
    // Update lifetime
    missile->base.lifetime -= deltaTime;
    if (missile->base.lifetime <= 0) {
        missile->base.active = false;
    }
    
    // Update hitbox
    UpdateMissileHitbox(missile);
}

void DrawMissileAttack(MissileAttack* missile) {
    // Draw missile with rotation
    DrawTexturePro(
        missile->base.texture,
        (Rectangle){ 0, 0, missile->base.texture.width, missile->base.texture.height },
        (Rectangle){ 
            missile->base.position.x, 
            missile->base.position.y, 
            missile->base.texture.width, 
            missile->base.texture.height 
        },
        (Vector2){ missile->base.texture.width / 2, missile->base.texture.height / 2 },
        missile->base.rotation * RAD2DEG,
        missile->base.tint
    );
}
```

## Integration with Game Systems

### Player Attack Creation

```c
void PlayerFireAttack(Player* player, AttackSystem* attackSystem, AttackType type) {
    Vector2 position = player->position;
    Vector2 direction = player->aimDirection;
    float damage = player->attackDamage;
    
    switch (type) {
        case ATTACK_LASER:
            CreateLaserAttack(attackSystem, position, direction, damage, player->id);
            break;
        case ATTACK_MISSILE:
            CreateMissileAttack(attackSystem, position, GetTargetPosition(), damage, player->id);
            break;
        case ATTACK_MISSILESTORM:
            CreateMissileStormAttack(attackSystem, position, GetTargetPosition(), 
                                     player->missileCount, damage, player->id);
            break;
        case ATTACK_LASERBEAM:
            CreateLaserBeamAttack(attackSystem, position, direction, damage, player->id);
            break;
    }
    
    // Play sound effect
    PlayAttackSound(type);
    
    // Apply recoil to player
    ApplyRecoil(player, direction, type);
}
```

### Main Game Loop Integration

```c
void UpdateGameplay(Game* game, float deltaTime) {
    // Update other game elements...
    
    // Update attack system
    UpdateAttacks(game->attackSystem, deltaTime);
    
    // Check attack collisions with game entities
    CheckAttackCollisions(game);
    
    // Other game updates...
}

void RenderGameplay(Game* game) {
    // Draw background and other elements...
    
    // Draw attacks
    DrawAttacks(game->attackSystem);
    
    // Draw other game elements...
}
```

## Memory Management

1. **Attack Pooling**:
   - Implement an object pool for attacks to avoid frequent allocation/deallocation
   - Recycle inactive attacks when new ones are created
   - Pre-allocate memory for maximum number of simultaneous attacks

2. **Resource Management**:
   - Share textures between attacks of the same type
   - Load attack-related resources at game initialization
   - Unload all resources when transitioning out of gameplay

## Special Effects Integration

1. **Visual Effects**:
   - Create particle effects on attack creation and impact
   - Add trail effects for missiles
   - Use screen shake for powerful attacks
   - Apply visual distortion or glow effects for energy attacks

2. **Sound Effects**:
   - Play appropriate sounds on attack creation
   - Play impact sounds on collision
   - Apply spatial audio based on attack position

## Performance Considerations

1. **Limiting Active Attacks**:
   - Set a maximum number of active attacks to maintain performance
   - When limit is reached, prioritize newer attacks or more damaging ones

2. **Simplified Physics**:
   - Use simplified physics for large numbers of projectiles
   - Consider using grid-based collision detection for better performance

3. **Level of Detail**:
   - Reduce visual complexity when many attacks are active
   - Simplify collision shapes for distant attacks

## Gameplay Balancing Notes

1. **Attack Power**:
   - Laser: Fast, direct, moderate damage
   - Missile: Slower, homing, high damage
   - Missile Storm: Area effect, moderate individual damage, high total damage
   - Laser Beam: Continuous damage, high total damage over time

2. **Attack Limitations**:
   - Cooldown timers between attacks
   - Energy/ammo consumption
   - Limited attack count per player 