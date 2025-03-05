#ifndef PADDLE_H
#define PADDLE_H

#include "entity.h"

// Paddle specific data
typedef struct PaddleData {
    int playerID;           // Player ID (1 or 2)
    int width;              // Current width
    int baseWidth;          // Base width (for power-ups)
    float speed;            // Movement speed
    float baseSpeed;        // Base speed (for power-ups)
    bool sticky;            // Sticky paddle power-up
    float powerUpTimer;     // Timer for power-ups
    KeyboardKey leftKey;    // Key for moving left
    KeyboardKey rightKey;   // Key for moving right
    KeyboardKey upKey;      // Key for moving up
    KeyboardKey downKey;    // Key for moving down
    bool moveVertical;      // Whether paddle moves vertically (true) or horizontally (false)
} PaddleData;

// Paddle functions
Entity* CreatePaddle(int playerID, float x, float y, int width, float speed, Color color);
void UpdatePaddle(Entity* entity, float deltaTime);
void DrawPaddle(Entity* entity);
void OnPaddleCollision(Entity* paddle, Entity* other);
void DestroyPaddle(Entity* entity);

// Paddle action functions
void MovePaddleLeft(Entity* paddle, float deltaTime);
void MovePaddleRight(Entity* paddle, float deltaTime);
void MovePaddleUp(Entity* paddle, float deltaTime);
void MovePaddleDown(Entity* paddle, float deltaTime);
void ResizePaddle(Entity* paddle, float widthFactor);
void ChangeSpeed(Entity* paddle, float speedFactor);
void MakePaddleSticky(Entity* paddle, float duration);
void UpdatePaddlePowerUps(Entity* paddle, float deltaTime);

#endif // PADDLE_H 