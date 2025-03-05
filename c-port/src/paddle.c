#include "../include/paddle.h"
#include <stdlib.h>
#include <stdio.h>

// Paddle constants
#define PADDLE_HEIGHT 33
#define DEFAULT_PADDLE_SPEED 350.0f
#define GAME_AREA_TOP 50
#define GAME_AREA_BOTTOM 550
#define GAME_AREA_LEFT 0
#define GAME_AREA_RIGHT 800

// Create a new paddle entity
Entity* CreatePaddle(int playerID, float x, float y, int width, float speed, Color color) {
    // Create the entity with default values
    Rectangle rect = { x, y, width, PADDLE_HEIGHT };
    Vector2 velocity = { 0.0f, 0.0f };
    
    Entity* paddle = CreateEntity(ENTITY_PADDLE, rect, velocity, color);
    if (!paddle) return NULL;
    
    // Set up paddle specific data
    PaddleData* data = (PaddleData*)malloc(sizeof(PaddleData));
    if (!data) {
        DestroyEntity(paddle);
        printf("Error: Failed to allocate memory for paddle data\n");
        return NULL;
    }
    
    data->playerID = playerID;
    data->width = width;
    data->baseWidth = width;
    data->speed = speed > 0 ? speed : DEFAULT_PADDLE_SPEED;
    data->baseSpeed = data->speed;
    data->sticky = false;
    data->powerUpTimer = 0.0f;
    data->moveVertical = true; // Default to vertical movement for mBreak
    
    // Set default controls based on player ID
    if (playerID == 1) {
        data->leftKey = KEY_A;
        data->rightKey = KEY_D;
        data->upKey = KEY_W;
        data->downKey = KEY_S;
    } else {
        data->leftKey = KEY_LEFT;
        data->rightKey = KEY_RIGHT;
        data->upKey = KEY_UP;
        data->downKey = KEY_DOWN;
    }
    
    // Set entity data
    paddle->data = data;
    
    // Set entity functions
    paddle->update = UpdatePaddle;
    paddle->draw = DrawPaddle;
    paddle->onCollision = OnPaddleCollision;
    paddle->destroy = DestroyPaddle;
    
    return paddle;
}

// Update paddle position and state
void UpdatePaddle(Entity* entity, float deltaTime) {
    if (!entity || !entity->active || entity->type != ENTITY_PADDLE) return;
    
    PaddleData* data = (PaddleData*)entity->data;
    if (!data) return;
    
    // Update power-up timers
    UpdatePaddlePowerUps(entity, deltaTime);
    
    // Handle input based on movement direction
    if (data->moveVertical) {
        // Vertical movement (for mBreak)
        if (IsKeyDown(data->upKey)) {
            MovePaddleUp(entity, deltaTime);
        }
        
        if (IsKeyDown(data->downKey)) {
            MovePaddleDown(entity, deltaTime);
        }
        
        // Keep paddle within vertical game bounds
        if (entity->rect.y < GAME_AREA_TOP) {
            entity->rect.y = GAME_AREA_TOP;
        }
        
        if (entity->rect.y + entity->rect.height > GAME_AREA_BOTTOM) {
            entity->rect.y = GAME_AREA_BOTTOM - entity->rect.height;
        }
    } else {
        // Horizontal movement (original Breakout style)
        if (IsKeyDown(data->leftKey)) {
            MovePaddleLeft(entity, deltaTime);
        }
        
        if (IsKeyDown(data->rightKey)) {
            MovePaddleRight(entity, deltaTime);
        }
        
        // Keep paddle within horizontal game bounds
        if (entity->rect.x < GAME_AREA_LEFT) {
            entity->rect.x = GAME_AREA_LEFT;
        }
        
        if (entity->rect.x + entity->rect.width > GAME_AREA_RIGHT) {
            entity->rect.x = GAME_AREA_RIGHT - entity->rect.width;
        }
    }
}

// Draw the paddle
void DrawPaddle(Entity* entity) {
    if (!entity || !entity->active || entity->type != ENTITY_PADDLE) return;
    
    PaddleData* data = (PaddleData*)entity->data;
    if (!data) return;
    
    // Draw the paddle rectangle
    DrawRectangleRec(entity->rect, entity->color);
    
    // Draw border around paddle
    DrawRectangleLinesEx(entity->rect, 1, ColorBrightness(entity->color, 0.5f));
    
    // Draw special effects for power-ups if active
    if (data->sticky) {
        // Draw a glowing effect for sticky paddle
        Color glowColor = ColorAlpha(WHITE, 0.5f);
        DrawRectangleLinesEx(entity->rect, 2, glowColor);
    }
}

// Handle collision with other entities
void OnPaddleCollision(Entity* paddle, Entity* other) {
    if (!paddle || !other || !paddle->active || !other->active) return;
    if (paddle->type != ENTITY_PADDLE) return;
    
    PaddleData* data = (PaddleData*)paddle->data;
    if (!data) return;
    
    // Handle collision with ball
    if (other->type == ENTITY_BALL) {
        // Ball physics will be handled in ball.c
    }
    
    // Handle collision with power-ups
    if (other->type == ENTITY_POWERUP) {
        // TODO: Handle power-up effects
    }
}

// Clean up paddle resources
void DestroyPaddle(Entity* entity) {
    if (!entity || entity->type != ENTITY_PADDLE) return;
    
    // Free paddle-specific data
    if (entity->data) {
        free(entity->data);
        entity->data = NULL;
    }
}

// Move paddle left
void MovePaddleLeft(Entity* paddle, float deltaTime) {
    if (!paddle || !paddle->active || paddle->type != ENTITY_PADDLE) return;
    
    PaddleData* data = (PaddleData*)paddle->data;
    if (!data) return;
    
    paddle->rect.x -= data->speed * deltaTime;
}

// Move paddle right
void MovePaddleRight(Entity* paddle, float deltaTime) {
    if (!paddle || !paddle->active || paddle->type != ENTITY_PADDLE) return;
    
    PaddleData* data = (PaddleData*)paddle->data;
    if (!data) return;
    
    paddle->rect.x += data->speed * deltaTime;
}

// Move paddle up
void MovePaddleUp(Entity* paddle, float deltaTime) {
    if (!paddle || !paddle->active || paddle->type != ENTITY_PADDLE) return;
    
    PaddleData* data = (PaddleData*)paddle->data;
    if (!data) return;
    
    paddle->rect.y -= data->speed * deltaTime;
}

// Move paddle down
void MovePaddleDown(Entity* paddle, float deltaTime) {
    if (!paddle || !paddle->active || paddle->type != ENTITY_PADDLE) return;
    
    PaddleData* data = (PaddleData*)paddle->data;
    if (!data) return;
    
    paddle->rect.y += data->speed * deltaTime;
}

// Resize paddle (for power-ups)
void ResizePaddle(Entity* paddle, float widthFactor) {
    if (!paddle || !paddle->active || paddle->type != ENTITY_PADDLE) return;
    
    PaddleData* data = (PaddleData*)paddle->data;
    if (!data) return;
    
    // Calculate new width based on base width
    int newWidth = (int)(data->baseWidth * widthFactor);
    
    // Adjust position to keep paddle centered
    float centerX = paddle->rect.x + paddle->rect.width / 2.0f;
    paddle->rect.width = newWidth;
    paddle->rect.x = centerX - newWidth / 2.0f;
    
    // Update paddle data
    data->width = newWidth;
}

// Change paddle speed (for power-ups)
void ChangeSpeed(Entity* paddle, float speedFactor) {
    if (!paddle || !paddle->active || paddle->type != ENTITY_PADDLE) return;
    
    PaddleData* data = (PaddleData*)paddle->data;
    if (!data) return;
    
    data->speed = data->baseSpeed * speedFactor;
}

// Make paddle sticky (for power-ups)
void MakePaddleSticky(Entity* paddle, float duration) {
    if (!paddle || !paddle->active || paddle->type != ENTITY_PADDLE) return;
    
    PaddleData* data = (PaddleData*)paddle->data;
    if (!data) return;
    
    data->sticky = true;
    data->powerUpTimer = duration;
}

// Update paddle power-up timers
void UpdatePaddlePowerUps(Entity* paddle, float deltaTime) {
    if (!paddle || !paddle->active || paddle->type != ENTITY_PADDLE) return;
    
    PaddleData* data = (PaddleData*)paddle->data;
    if (!data) return;
    
    // Update sticky paddle timer
    if (data->sticky && data->powerUpTimer > 0) {
        data->powerUpTimer -= deltaTime;
        
        // Reset when timer expires
        if (data->powerUpTimer <= 0) {
            data->sticky = false;
            data->powerUpTimer = 0;
        }
    }
} 