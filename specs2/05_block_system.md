# Block System

This document details the block system for the mBreak game, based on the current implementation in `objects/block.py` and related files.

## Block Entity Structure

```c
typedef struct Block {
    // Core properties
    Vector2 position;        // Float precision position
    Rectangle rect;          // Collision rectangle
    Color color;             // Block color
    
    // Health and damage
    int health;              // Current health
    int max_health;          // Maximum health
    float damage_taken;      // Accumulated damage (for visual effects)
    
    // Visual properties
    Texture2D texture;       // Block texture
    float alpha;             // Transparency (0.0-1.0)
    float scale;             // Size scale (1.0 = normal)
    float rotation;          // Rotation in degrees
    Shadow* shadow;          // Shadow effect
    
    // Effects
    SpriteList* effectList;  // List of active effects
    bool is_burning;         // Whether block is burning
    bool is_frozen;          // Whether block is frozen
    bool is_stunned;         // Whether block is stunned
    
    // Block type
    BlockType type;          // Type of block (normal, indestructible, etc.)
    
    // Animation properties
    float shake_amount;      // Current shake intensity
    float shake_decay;       // How quickly shake decreases
    Vector2 shake_offset;    // Current visual offset from shaking
    
    // Destruction properties
    bool is_destroyed;       // Whether block is marked for destruction
    bool is_exploding;       // Whether block is in explosion animation
    float explosion_time;    // Time since explosion started
    float explosion_duration; // Total explosion animation duration
    
    // Powerup properties
    PowerupType powerup;     // Powerup contained in this block (if any)
} Block;

typedef enum BlockType {
    BLOCK_NORMAL,
    BLOCK_INDESTRUCTIBLE,
    BLOCK_EXPLOSIVE,
    BLOCK_HEALTH,
    BLOCK_ENERGY
} BlockType;
```

## Initialization

```c
Block* CreateBlock(float x, float y, BlockType type) {
    Block* block = (Block*)MemAlloc(sizeof(Block));
    
    // Set position
    block->position.x = x;
    block->position.y = y;
    
    // Create rect
    block->rect = (Rectangle){ x, y, BLOCK_WIDTH, BLOCK_HEIGHT };
    
    // Set type
    block->type = type;
    
    // Set health based on type
    switch (type) {
        case BLOCK_INDESTRUCTIBLE:
            block->health = 999999;
            block->max_health = 999999;
            break;
        case BLOCK_EXPLOSIVE:
            block->health = 1;
            block->max_health = 1;
            break;
        case BLOCK_HEALTH:
        case BLOCK_ENERGY:
            block->health = 1;
            block->max_health = 1;
            break;
        case BLOCK_NORMAL:
        default:
            block->health = GetRandomValue(1, 3); // Random health between 1-3
            block->max_health = block->health;
            break;
    }
    
    // Set visual properties
    block->damage_taken = 0;
    block->alpha = 1.0f;
    block->scale = 1.0f;
    block->rotation = 0.0f;
    
    // Set texture based on type
    switch (type) {
        case BLOCK_INDESTRUCTIBLE:
            block->texture = indestructibleBlockTexture;
            block->color = GRAY;
            break;
        case BLOCK_EXPLOSIVE:
            block->texture = explosiveBlockTexture;
            block->color = RED;
            break;
        case BLOCK_HEALTH:
            block->texture = healthBlockTexture;
            block->color = GREEN;
            break;
        case BLOCK_ENERGY:
            block->texture = energyBlockTexture;
            block->color = BLUE;
            break;
        case BLOCK_NORMAL:
        default:
            block->texture = normalBlockTexture;
            // Set random color for normal blocks
            block->color = GetRandomBlockColor();
            break;
    }
    
    // Create shadow
    block->shadow = CreateShadow(block);
    
    // Initialize effect list
    block->effectList = CreateSpriteList();
    
    // Initialize status effects
    block->is_burning = false;
    block->is_frozen = false;
    block->is_stunned = false;
    
    // Initialize animation properties
    block->shake_amount = 0.0f;
    block->shake_decay = BLOCK_SHAKE_DECAY;
    block->shake_offset = (Vector2){ 0, 0 };
    
    // Initialize destruction properties
    block->is_destroyed = false;
    block->is_exploding = false;
    block->explosion_time = 0.0f;
    block->explosion_duration = BLOCK_EXPLOSION_DURATION;
    
    // Determine if block contains a powerup (only for normal blocks)
    if (type == BLOCK_NORMAL) {
        if (GetRandomValue(1, 100) <= POWERUP_SPAWN_CHANCE) {
            block->powerup = GetRandomPowerupType();
        } else {
            block->powerup = POWERUP_NONE;
        }
    } else {
        block->powerup = POWERUP_NONE;
    }
    
    // Add to main block group
    AddBlockToGroup(block, mainBlockGroup);
    
    return block;
}
```

## Damage and Health System

```c
bool DamageBlock(Block* block, int damage, Player* source) {
    // Check if block can be damaged
    if (block->is_destroyed || block->type == BLOCK_INDESTRUCTIBLE) {
        return false;
    }
    
    // Apply damage
    block->health -= damage;
    block->damage_taken += damage;
    
    // Apply visual effects
    block->shake_amount = BLOCK_HIT_SHAKE_AMOUNT;
    
    // Add hit effect
    AddBlockHitEffect(block);
    
    // Check if block is destroyed
    if (block->health <= 0) {
        DestroyBlock(block, source);
        return true;
    }
    
    return false;
}

void DestroyBlock(Block* block, Player* source) {
    // Mark as destroyed
    block->is_destroyed = true;
    
    // Award points to player if source is provided
    if (source != NULL) {
        AddPlayerPoints(source, BLOCK_DESTROY_POINTS);
        
        // Award energy based on block type
        switch (block->type) {
            case BLOCK_ENERGY:
                AddPlayerEnergy(source, ENERGY_BLOCK_BONUS);
                break;
            case BLOCK_HEALTH:
                AddPlayerHealth(source, HEALTH_BLOCK_BONUS);
                break;
            default:
                AddPlayerEnergy(source, BLOCK_DESTROY_ENERGY);
                break;
        }
    }
    
    // Handle special block types
    switch (block->type) {
        case BLOCK_EXPLOSIVE:
            // Start explosion animation
            block->is_exploding = true;
            block->explosion_time = 0.0f;
            
            // Create explosion effect
            CreateExplosionEffect(block->position.x + block->rect.width/2, 
                                 block->position.y + block->rect.height/2,
                                 EXPLOSIVE_BLOCK_RADIUS);
            
            // Damage nearby blocks
            DamageNearbyBlocks(block, EXPLOSIVE_BLOCK_RADIUS, EXPLOSIVE_BLOCK_DAMAGE, source);
            
            // Play explosion sound
            PlaySound(explosionSound);
            break;
            
        default:
            // Create destruction particles
            CreateBlockDestructionParticles(block);
            
            // Spawn powerup if block contained one
            if (block->powerup != POWERUP_NONE) {
                SpawnPowerup(block->position.x + block->rect.width/2, 
                            block->position.y + block->rect.height/2,
                            block->powerup);
            }
            
            // Remove from block group
            RemoveBlockFromGroup(block, mainBlockGroup);
            
            // Free memory
            DestroyBlockResources(block);
            break;
    }
}

void DamageNearbyBlocks(Block* source, float radius, int damage, Player* damageSource) {
    // Get all blocks
    int blockCount = GetBlockCount();
    
    for (int i = 0; i < blockCount; i++) {
        Block* block = GetBlockAt(i);
        
        // Skip the source block and already destroyed blocks
        if (block == source || block->is_destroyed) {
            continue;
        }
        
        // Calculate distance between block centers
        float sourceX = source->position.x + source->rect.width/2;
        float sourceY = source->position.y + source->rect.height/2;
        float targetX = block->position.x + block->rect.width/2;
        float targetY = block->position.y + block->rect.height/2;
        
        float distance = sqrtf(powf(targetX - sourceX, 2) + powf(targetY - sourceY, 2));
        
        // If within radius, apply damage
        if (distance <= radius) {
            // Calculate damage falloff based on distance
            float damageMultiplier = 1.0f - (distance / radius);
            int actualDamage = (int)(damage * damageMultiplier);
            
            if (actualDamage > 0) {
                DamageBlock(block, actualDamage, damageSource);
            }
        }
    }
}
```

## Update and Animation

```c
void UpdateBlock(Block* block, GameClock* clock) {
    float delta = GetDeltaTime(clock);
    
    // Skip if destroyed (unless exploding)
    if (block->is_destroyed && !block->is_exploding) {
        return;
    }
    
    // Handle explosion animation
    if (block->is_exploding) {
        block->explosion_time += delta;
        
        // Calculate explosion progress
        float progress = block->explosion_time / block->explosion_duration;
        
        // Update visual properties based on explosion progress
        block->scale = 1.0f + progress * 0.5f;
        block->alpha = 1.0f - progress;
        
        // Check if explosion animation is complete
        if (block->explosion_time >= block->explosion_duration) {
            // Remove from block group
            RemoveBlockFromGroup(block, mainBlockGroup);
            
            // Free memory
            DestroyBlockResources(block);
            return;
        }
    }
    
    // Update shake effect
    if (block->shake_amount > 0) {
        // Generate random shake offset
        block->shake_offset.x = GetRandomValue(-100, 100) / 100.0f * block->shake_amount;
        block->shake_offset.y = GetRandomValue(-100, 100) / 100.0f * block->shake_amount;
        
        // Decay shake amount
        block->shake_amount -= block->shake_decay * delta;
        if (block->shake_amount < 0) {
            block->shake_amount = 0;
            block->shake_offset = (Vector2){ 0, 0 };
        }
    }
    
    // Update effects
    UpdateSpriteList(block->effectList, clock);
    
    // Apply burning damage if block is burning
    if (block->is_burning) {
        block->burn_time += delta;
        
        // Apply damage every burn tick
        if (block->burn_time >= BLOCK_BURN_TICK_TIME) {
            block->burn_time -= BLOCK_BURN_TICK_TIME;
            DamageBlock(block, BLOCK_BURN_DAMAGE, block->burn_source);
        }
    }
}
```

## Drawing

```c
void DrawBlock(Block* block) {
    // Skip if destroyed (unless exploding)
    if (block->is_destroyed && !block->is_exploding) {
        return;
    }
    
    // Calculate draw position with shake offset
    Vector2 drawPos = GetWorldToScreen(
        (Vector2){ 
            block->position.x + block->shake_offset.x, 
            block->position.y + block->shake_offset.y 
        }
    );
    
    // Draw shadow
    DrawShadow(block->shadow);
    
    // Calculate color with damage and effects
    Color drawColor = block->color;
    
    // Apply damage tint (redder as damage increases)
    if (block->damage_taken > 0 && block->max_health > 1) {
        float damageFactor = block->damage_taken / block->max_health;
        drawColor.r = (unsigned char)Clamp(drawColor.r + (255 - drawColor.r) * damageFactor, 0, 255);
    }
    
    // Apply frozen effect (blue tint)
    if (block->is_frozen) {
        drawColor.r = (unsigned char)(drawColor.r * 0.5f);
        drawColor.g = (unsigned char)(drawColor.g * 0.7f);
        drawColor.b = (unsigned char)Clamp(drawColor.b + 50, 0, 255);
    }
    
    // Apply stunned effect (yellow tint)
    if (block->is_stunned) {
        drawColor.r = (unsigned char)Clamp(drawColor.r + 50, 0, 255);
        drawColor.g = (unsigned char)Clamp(drawColor.g + 50, 0, 255);
        drawColor.b = (unsigned char)(drawColor.b * 0.5f);
    }
    
    // Apply alpha
    drawColor.a = (unsigned char)(255 * block->alpha);
    
    // Draw block with scaling and rotation
    if (block->scale != 1.0f || block->rotation != 0.0f) {
        // Calculate center for rotation
        Vector2 origin = { block->texture.width / 2.0f, block->texture.height / 2.0f };
        
        // Calculate destination rectangle
        Rectangle destRect = {
            drawPos.x + origin.x, 
            drawPos.y + origin.y,
            block->texture.width * block->scale,
            block->texture.height * block->scale
        };
        
        // Draw texture with rotation and scaling
        DrawTexturePro(
            block->texture,
            (Rectangle){ 0, 0, block->texture.width, block->texture.height },
            destRect,
            origin,
            block->rotation,
            drawColor
        );
    } else {
        // Simple draw without rotation or scaling
        DrawTexture(block->texture, drawPos.x, drawPos.y, drawColor);
    }
    
    // Draw powerup indicator if block contains a powerup
    if (block->powerup != POWERUP_NONE && !block->is_exploding) {
        DrawPowerupIndicator(block);
    }
    
    // Draw effects
    DrawSpriteList(block->effectList);
    
    // Draw health indicator for multi-health blocks
    if (block->max_health > 1 && block->health > 0) {
        DrawBlockHealthIndicator(block, drawPos);
    }
    
    // Debug visualization
    if (IsDebugMode()) {
        DrawRectangleLines(
            drawPos.x, drawPos.y,
            block->rect.width, block->rect.height,
            RED
        );
    }
}

void DrawBlockHealthIndicator(Block* block, Vector2 drawPos) {
    // Draw small health pips at the bottom of the block
    float pipWidth = 2.0f;
    float pipHeight = 2.0f;
    float pipSpacing = 1.0f;
    float totalWidth = (pipWidth * block->max_health) + (pipSpacing * (block->max_health - 1));
    float startX = drawPos.x + (block->rect.width - totalWidth) / 2;
    float y = drawPos.y + block->rect.height - pipHeight - 1;
    
    for (int i = 0; i < block->max_health; i++) {
        Color pipColor = (i < block->health) ? WHITE : DARKGRAY;
        DrawRectangle(startX + (pipWidth + pipSpacing) * i, y, pipWidth, pipHeight, pipColor);
    }
}

void DrawPowerupIndicator(Block* block) {
    // Get draw position
    Vector2 drawPos = GetWorldToScreen(block->position);
    
    // Draw small powerup icon in the center of the block
    Texture2D powerupIcon = GetPowerupIcon(block->powerup);
    float scale = 0.5f; // Smaller than normal powerup
    
    DrawTexture(
        powerupIcon,
        drawPos.x + (block->rect.width - powerupIcon.width * scale) / 2,
        drawPos.y + (block->rect.height - powerupIcon.height * scale) / 2,
        WHITE
    );
}
```

## Visual Effects

```c
void AddBlockHitEffect(Block* block) {
    // Create a flash effect on hit
    Color startColor = WHITE;
    startColor.a = 160;
    Color endColor = WHITE;
    endColor.a = 0;
    
    Flash* flash = CreateFlash(block, startColor, endColor, BLOCK_HIT_EFFECT_TICKS);
    AddToSpriteList(block->effectList, flash);
}

void CreateBlockDestructionParticles(Block* block) {
    // Create particle system at block position
    ParticleSystem* particles = CreateParticleSystem(
        block->position.x + block->rect.width/2,
        block->position.y + block->rect.height/2,
        10, // Number of particles
        block->color,
        0.5f, // Particle lifetime
        2.0f, // Particle speed
        360.0f // Spread (all directions)
    );
    
    // Add to global particle list
    AddParticleSystem(particles);
}
```

## Status Effects

```c
void SetBlockBurning(Block* block, bool burning, Player* source) {
    // Can't burn indestructible blocks
    if (block->type == BLOCK_INDESTRUCTIBLE) {
        return;
    }
    
    // Can't burn frozen blocks
    if (block->is_frozen) {
        return;
    }
    
    // Set burning state
    block->is_burning = burning;
    
    if (burning) {
        // Store damage source
        block->burn_source = source;
        
        // Reset burn timer
        block->burn_time = 0;
        
        // Add burning effect
        Burning* effect = CreateBurningEffect(block, BLOCK_BURN_DURATION);
        AddToSpriteList(block->effectList, effect);
    }
}

void SetBlockFrozen(Block* block, bool frozen) {
    // Set frozen state
    block->is_frozen = frozen;
    
    if (frozen) {
        // Cancel burning if frozen
        if (block->is_burning) {
            SetBlockBurning(block, false, NULL);
        }
        
        // Add freezing effect
        Freezing* effect = CreateFreezingEffect(block, BLOCK_FREEZE_DURATION);
        AddToSpriteList(block->effectList, effect);
    }
}

void SetBlockStunned(Block* block, bool stunned) {
    // Set stunned state
    block->is_stunned = stunned;
    
    if (stunned) {
        // Add stun effect
        Stun* effect = CreateStunEffect(block, BLOCK_STUN_DURATION);
        AddToSpriteList(block->effectList, effect);
    }
}
```

## Level Generation

```c
void GenerateBlockLevel(int level) {
    // Clear any existing blocks
    ClearAllBlocks();
    
    // Determine level properties based on level number
    int rows = MIN_BLOCK_ROWS + (level / 2);
    if (rows > MAX_BLOCK_ROWS) {
        rows = MAX_BLOCK_ROWS;
    }
    
    int cols = MIN_BLOCK_COLS + (level / 3);
    if (cols > MAX_BLOCK_COLS) {
        cols = MAX_BLOCK_COLS;
    }
    
    // Calculate block size and spacing
    float blockWidth = BLOCK_WIDTH;
    float blockHeight = BLOCK_HEIGHT;
    float horizontalSpacing = (LEVEL_WIDTH - (cols * blockWidth)) / (cols + 1);
    float verticalSpacing = 10.0f;
    float startY = 50.0f;
    
    // Generate blocks
    for (int row = 0; row < rows; row++) {
        for (int col = 0; col < cols; col++) {
            float x = horizontalSpacing + col * (blockWidth + horizontalSpacing);
            float y = startY + row * (blockHeight + verticalSpacing);
            
            // Determine block type
            BlockType type = BLOCK_NORMAL;
            
            // Special blocks based on level and position
            int random = GetRandomValue(1, 100);
            
            // Indestructible blocks (more common at higher levels)
            if (random <= 5 + (level / 2)) {
                type = BLOCK_INDESTRUCTIBLE;
            }
            // Explosive blocks (more common at higher levels)
            else if (random <= 10 + level) {
                type = BLOCK_EXPLOSIVE;
            }
            // Health blocks (rare)
            else if (random <= 12 + (level / 5)) {
                type = BLOCK_HEALTH;
            }
            // Energy blocks (rare)
            else if (random <= 14 + (level / 5)) {
                type = BLOCK_ENERGY;
            }
            
            // Create the block
            CreateBlock(x, y, type);
        }
    }
}

void ClearAllBlocks() {
    // Get all blocks
    int blockCount = GetBlockCount();
    
    // Remove all blocks
    for (int i = blockCount - 1; i >= 0; i--) {
        Block* block = GetBlockAt(i);
        
        // Remove from block group
        RemoveBlockFromGroup(block, mainBlockGroup);
        
        // Free memory
        DestroyBlockResources(block);
    }
}
```

## Constants

```c
// Block dimensions
#define BLOCK_WIDTH 30.0f
#define BLOCK_HEIGHT 15.0f

// Level generation
#define MIN_BLOCK_ROWS 3
#define MAX_BLOCK_ROWS 8
#define MIN_BLOCK_COLS 8
#define MAX_BLOCK_COLS 15

// Points and rewards
#define BLOCK_DESTROY_POINTS 10
#define BLOCK_DESTROY_ENERGY 1
#define HEALTH_BLOCK_BONUS 10
#define ENERGY_BLOCK_BONUS 20

// Powerups
#define POWERUP_SPAWN_CHANCE 15  // 15% chance per block

// Explosive blocks
#define EXPLOSIVE_BLOCK_RADIUS 60.0f
#define EXPLOSIVE_BLOCK_DAMAGE 3

// Visual effects
#define BLOCK_HIT_SHAKE_AMOUNT 2.0f
#define BLOCK_SHAKE_DECAY 10.0f
#define BLOCK_HIT_EFFECT_TICKS 10
#define BLOCK_EXPLOSION_DURATION 0.3f

// Status effects
#define BLOCK_BURN_DAMAGE 1
#define BLOCK_BURN_TICK_TIME 0.5f
#define BLOCK_BURN_DURATION 3.0f
#define BLOCK_FREEZE_DURATION 4.0f
#define BLOCK_STUN_DURATION 2.0f
```

## Memory Management

```c
void DestroyBlockResources(Block* block) {
    // Destroy effects
    for (int i = 0; i < block->effectList->count; i++) {
        Effect* effect = (Effect*)block->effectList->items[i];
        DestroyEffect(effect);
    }
    
    // Destroy effect list
    DestroySpriteList(block->effectList);
    
    // Destroy shadow
    DestroyShadow(block->shadow);
    
    // Free memory
    MemFree(block);
}
```

This specification details the block system implementation for the C + Raylib port, based on the actual implementation in the Python version. It covers all aspects of block behavior, health system, visual effects, and level generation. 