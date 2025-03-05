#ifndef BLOCK_H
#define BLOCK_H

#include "entity.h"

// Block types
typedef enum BlockType {
    BLOCK_NORMAL = 0,
    BLOCK_HARD,
    BLOCK_INVINCIBLE,
    BLOCK_EXPLOSIVE,
    BLOCK_POWERUP
} BlockType;

// Block specific data
typedef struct BlockData {
    BlockType type;        // Type of block
    int health;            // Health points
    int maxHealth;         // Maximum health points
    int score;             // Score value
    bool damaged;          // Whether block is damaged
    float damageTimer;     // Timer for damage effect
    int powerUpType;       // Type of power-up when destroyed (if any)
    bool hasAnimation;     // Whether block has an animation
    int frameCount;        // Number of animation frames
    int currentFrame;      // Current animation frame
    float frameTime;       // Time for each animation frame
    float animationTimer;  // Timer for animation
    bool flipped;          // Whether block is flipped horizontally (for player 2)
} BlockData;

// Block functions
Entity* CreateBlock(float x, float y, float width, float height, BlockType type, Color color);
void UpdateBlock(Entity* entity, float deltaTime);
void DrawBlock(Entity* entity);
void OnBlockCollision(Entity* block, Entity* other);
void DestroyBlock(Entity* entity);

// Block action functions
void DamageBlock(Entity* block, int damage);
void AnimateBlock(Entity* block, float deltaTime);
void SetBlockPowerUp(Entity* block, int powerUpType);
void ExplodeBlock(Entity* block);

#endif // BLOCK_H 