#ifndef BALL_H
#define BALL_H

#include "entity.h"
#include "paddle.h"

// Ball specific data
typedef struct BallData {
    Vector2 position;       // Precise float position
    float radius;           // Ball radius
    float baseSpeed;        // Base speed
    float speedMultiplier;  // Current speed multiplier
    float damage;           // Damage multiplier for blocks
    bool stuck;             // Whether ball is stuck to paddle
    Entity* attachedPaddle; // Paddle ball is attached to (if stuck)
    Entity* owner;          // Current owner of the ball (for scoring)
    int ownerID;            // Current owner ID of the ball (1 or 2)
    float offsetX;          // X offset from paddle when stuck
    float stuckTimer;       // Time since ball last moved significantly
    bool smash;             // Smash mode (high velocity/damage)
    float smashTimer;       // Timer for smash powerup
    float trailTime;        // Time between trail effects
} BallData;

// Ball functions
Entity* CreateBall(float x, float y, float radius, float speed, Color color);
void UpdateBall(Entity* entity, float deltaTime);
void DrawBall(Entity* entity);
void OnBallCollision(Entity* ball, Entity* other);
void DestroyBall(Entity* entity);

// Ball action functions
void LaunchBall(Entity* ball, float initialAngle);
void StickBallToPaddle(Entity* ball, Entity* paddle);
void ReleaseBallFromPaddle(Entity* ball);
void BounceBall(Entity* ball, Entity* other);
void ActivateSmash(Entity* ball, float duration);
void SetBallSpeed(Entity* ball, float speedMultiplier);
void CheckWallCollision(Entity* ball);
void CheckStuckDetection(Entity* ball, float deltaTime);
void ChangeBallOwner(Entity* ball, Entity* newOwner);

#endif // BALL_H 