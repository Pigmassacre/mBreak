#include "../include/block.h"
#include "../include/ball.h"
#include "../include/font.h"
#include <stdlib.h>
#include <stdio.h>

// Block constants
#define DAMAGE_EFFECT_TIME 0.2f // Time for damage visual effect
#define DEFAULT_BLOCK_SCORE 10  // Default score value

// Create a new block entity
Entity* CreateBlock(float x, float y, float width, float height, BlockType type, Color color) {
    // Create the entity with default values
    Rectangle rect = { x, y, width, height };
    Vector2 velocity = { 0.0f, 0.0f };
    
    Entity* block = CreateEntity(ENTITY_BLOCK, rect, velocity, color);
    if (!block) return NULL;
    
    // Set up block specific data
    BlockData* data = (BlockData*)malloc(sizeof(BlockData));
    if (!data) {
        DestroyEntity(block);
        printf("Error: Failed to allocate memory for block data\n");
        return NULL;
    }
    
    data->type = type;
    data->damaged = false;
    data->damageTimer = 0.0f;
    data->hasAnimation = false;
    data->frameCount = 1;
    data->currentFrame = 0;
    data->frameTime = 0.0f;
    data->animationTimer = 0.0f;
    data->powerUpType = -1; // No power-up by default
    data->flipped = false;  // Not flipped by default (player 1)
    
    // Set properties based on block type
    switch (type) {
        case BLOCK_NORMAL:
            data->health = 1;
            data->maxHealth = 1;
            data->score = DEFAULT_BLOCK_SCORE;
            break;
        case BLOCK_HARD:
            data->health = 2;
            data->maxHealth = 2;
            data->score = DEFAULT_BLOCK_SCORE * 2;
            break;
        case BLOCK_INVINCIBLE:
            data->health = -1; // -1 indicates invincible
            data->maxHealth = -1;
            data->score = 0;
            break;
        case BLOCK_EXPLOSIVE:
            data->health = 1;
            data->maxHealth = 1;
            data->score = DEFAULT_BLOCK_SCORE * 3;
            break;
        case BLOCK_POWERUP:
            data->health = 1;
            data->maxHealth = 1;
            data->score = DEFAULT_BLOCK_SCORE * 2;
            data->powerUpType = rand() % 5; // Random power-up type
            break;
        default:
            data->health = 1;
            data->maxHealth = 1;
            data->score = DEFAULT_BLOCK_SCORE;
            break;
    }
    
    // Set entity data
    block->data = data;
    
    // Set entity functions
    block->update = UpdateBlock;
    block->draw = DrawBlock;
    block->onCollision = OnBlockCollision;
    block->destroy = DestroyBlock;
    
    return block;
}

// Update block state
void UpdateBlock(Entity* entity, float deltaTime) {
    if (!entity || !entity->active || entity->type != ENTITY_BLOCK) return;
    
    BlockData* data = (BlockData*)entity->data;
    if (!data) return;
    
    // Update damage effect timer
    if (data->damaged) {
        data->damageTimer -= deltaTime;
        
        if (data->damageTimer <= 0.0f) {
            data->damaged = false;
            data->damageTimer = 0.0f;
        }
    }
    
    // Update animation if block has one
    if (data->hasAnimation) {
        AnimateBlock(entity, deltaTime);
    }
}

// Draw the block
void DrawBlock(Entity* entity) {
    if (!entity || !entity->active || entity->type != ENTITY_BLOCK) return;
    
    BlockData* data = (BlockData*)entity->data;
    if (!data) return;
    
    Color drawColor = entity->color;
    
    // If block is damaged, flash white
    if (data->damaged) {
        drawColor = WHITE;
    }
    
    // Calculate health percentage for tinting (darker when less health)
    float healthPercentage = (float)data->health / (float)data->maxHealth;
    Color tintedColor = drawColor;
    
    // Only apply tint for non-invincible blocks
    if (data->type != BLOCK_INVINCIBLE && data->health < data->maxHealth) {
        // Darken the color based on health (more damage = darker)
        tintedColor.r = (unsigned char)(drawColor.r * (0.5f + 0.5f * healthPercentage));
        tintedColor.g = (unsigned char)(drawColor.g * (0.5f + 0.5f * healthPercentage));
        tintedColor.b = (unsigned char)(drawColor.b * (0.5f + 0.5f * healthPercentage));
        drawColor = tintedColor;
    }
    
    // Draw differently based on block type
    switch (data->type) {
        case BLOCK_NORMAL:
            DrawRectangleRec(entity->rect, drawColor);
            break;
        case BLOCK_HARD:
            // Draw with border to indicate it's harder
            DrawRectangleRec(entity->rect, drawColor);
            DrawRectangleLinesEx(entity->rect, 2, BLACK);
            break;
        case BLOCK_INVINCIBLE:
            // Draw with special pattern for invincible blocks
            DrawRectangleRec(entity->rect, drawColor);
            
            // Criss-cross pattern
            DrawLineEx(
                (Vector2){entity->rect.x, entity->rect.y}, 
                (Vector2){entity->rect.x + entity->rect.width, entity->rect.y + entity->rect.height}, 
                2, BLACK);
            DrawLineEx(
                (Vector2){entity->rect.x + entity->rect.width, entity->rect.y}, 
                (Vector2){entity->rect.x, entity->rect.y + entity->rect.height}, 
                2, BLACK);
            break;
        case BLOCK_EXPLOSIVE:
            // Draw with explosion symbol
            DrawRectangleRec(entity->rect, drawColor);
            DrawTextEx(gameFont, "*", 
                    (Vector2){entity->rect.x + entity->rect.width/2 - 5, 
                    entity->rect.y + entity->rect.height/2 - 10}, 
                    20, 1, RED);
            break;
        case BLOCK_POWERUP:
            // Draw with power-up indicator
            DrawRectangleRec(entity->rect, drawColor);
            DrawTextEx(gameFont, "?", 
                    (Vector2){entity->rect.x + entity->rect.width/2 - 5, 
                    entity->rect.y + entity->rect.height/2 - 10}, 
                    20, 1, YELLOW);
            break;
        default:
            DrawRectangleRec(entity->rect, drawColor);
            break;
    }
    
    // Add visual indicator for block orientation/owner
    if (data->flipped) {
        // Draw a small indicator on the right side for player 2 blocks
        DrawRectangle(
            entity->rect.x + entity->rect.width - 4,
            entity->rect.y + 4,
            4,
            entity->rect.height - 8,
            ColorBrightness(drawColor, 1.5f)
        );
    } else {
        // Draw a small indicator on the left side for player 1 blocks
        DrawRectangle(
            entity->rect.x,
            entity->rect.y + 4,
            4,
            entity->rect.height - 8,
            ColorBrightness(drawColor, 1.5f)
        );
    }
}

// Handle collision with other entities
void OnBlockCollision(Entity* block, Entity* other) {
    if (!block || !other || !block->active || !other->active) return;
    if (block->type != ENTITY_BLOCK) return;
    
    BlockData* data = (BlockData*)block->data;
    if (!data) return;
    
    // Handle collision with ball
    if (other->type == ENTITY_BALL) {
        BallData* ballData = (BallData*)other->data;
        if (ballData) {
            // Calculate damage based on ball properties
            int damage = 1;
            
            // Apply damage multiplier if ball is in smash mode
            if (ballData->smash) {
                damage = (int)(damage * ballData->damage);
            }
            
            DamageBlock(block, damage);
        }
    }
}

// Clean up block resources
void DestroyBlock(Entity* entity) {
    if (!entity || entity->type != ENTITY_BLOCK) return;
    
    // Free block-specific data
    if (entity->data) {
        free(entity->data);
        entity->data = NULL;
    }
}

// Apply damage to a block
void DamageBlock(Entity* block, int damage) {
    if (!block || !block->active || block->type != ENTITY_BLOCK) return;
    
    BlockData* data = (BlockData*)block->data;
    if (!data) return;
    
    // Invincible blocks can't be damaged
    if (data->health == -1) return;
    
    // Apply damage
    data->health -= damage;
    
    // Visual effect for damage
    data->damaged = true;
    data->damageTimer = DAMAGE_EFFECT_TIME;
    
    // Check if block is destroyed
    if (data->health <= 0) {
        // Handle special effects based on block type
        if (data->type == BLOCK_EXPLOSIVE) {
            ExplodeBlock(block);
        }
        
        // TODO: Spawn power-up if this is a power-up block
        
        // Deactivate the block
        block->active = false;
    }
}

// Animate block
void AnimateBlock(Entity* block, float deltaTime) {
    if (!block || !block->active || block->type != ENTITY_BLOCK) return;
    
    BlockData* data = (BlockData*)block->data;
    if (!data || !data->hasAnimation) return;
    
    // Update animation timer
    data->animationTimer += deltaTime;
    
    // Advance frame if timer exceeds frame time
    if (data->animationTimer >= data->frameTime) {
        data->currentFrame = (data->currentFrame + 1) % data->frameCount;
        data->animationTimer = 0.0f;
    }
}

// Set power-up type for the block
void SetBlockPowerUp(Entity* block, int powerUpType) {
    if (!block || !block->active || block->type != ENTITY_BLOCK) return;
    
    BlockData* data = (BlockData*)block->data;
    if (!data) return;
    
    data->powerUpType = powerUpType;
    
    // If not already a power-up block, change it
    if (data->type != BLOCK_POWERUP) {
        data->type = BLOCK_POWERUP;
    }
}

// Handle explosive block destruction
void ExplodeBlock(Entity* block) {
    if (!block || !block->active || block->type != ENTITY_BLOCK) return;
    
    BlockData* data = (BlockData*)block->data;
    if (!data || data->type != BLOCK_EXPLOSIVE) return;
    
    // In a real implementation, we would:
    // 1. Find all blocks within explosion radius
    // 2. Damage those blocks
    // 3. Create explosion particle effects
    
    // For now, just print a message
    printf("Explosive block detonated!\n");
    
    // TODO: Implement finding and damaging nearby blocks
    // This requires access to the entity groups, which would be passed from the game state
} 