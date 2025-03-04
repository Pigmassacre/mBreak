#include "../include/ball.h"
#include <stdlib.h>
#include <stdio.h>
#include <math.h>

// Ball constants
#define DEFAULT_BALL_RADIUS 10.0f
#define DEFAULT_BALL_SPEED 300.0f
#define MINIMUM_BOUNCE_ANGLE 0.2f  // Radians
#define STUCK_DETECTION_TIME 3.0f  // Time to detect if ball is stuck
#define STUCK_DISTANCE_THRESHOLD 20.0f  // Distance to detect if ball is stuck
#define TRAIL_EFFECT_TIME 0.05f    // Time between trail effects

// Create a new ball entity
Entity* CreateBall(float x, float y, float radius, float speed, Color color) {
    // Create entity with default values
    float ballRadius = radius > 0 ? radius : DEFAULT_BALL_RADIUS;
    Rectangle rect = { x - ballRadius, y - ballRadius, ballRadius * 2, ballRadius * 2 };
    Vector2 velocity = { 0.0f, 0.0f };
    
    Entity* ball = CreateEntity(ENTITY_BALL, rect, velocity, color);
    if (!ball) return NULL;
    
    // Set up ball specific data
    BallData* data = (BallData*)malloc(sizeof(BallData));
    if (!data) {
        DestroyEntity(ball);
        printf("Error: Failed to allocate memory for ball data\n");
        return NULL;
    }
    
    data->position = (Vector2){ x, y };
    data->radius = ballRadius;
    data->baseSpeed = speed > 0 ? speed : DEFAULT_BALL_SPEED;
    data->speedMultiplier = 1.0f;
    data->damage = 1.0f;
    data->stuck = true;  // Ball starts stuck to paddle
    data->attachedPaddle = NULL;
    data->offsetX = 0.0f;
    data->stuckTimer = 0.0f;
    data->smash = false;
    data->smashTimer = 0.0f;
    data->trailTime = 0.0f;
    
    // Set entity data
    ball->data = data;
    
    // Set entity functions
    ball->update = UpdateBall;
    ball->draw = DrawBall;
    ball->onCollision = OnBallCollision;
    ball->destroy = DestroyBall;
    
    return ball;
}

// Update ball position and state
void UpdateBall(Entity* entity, float deltaTime) {
    if (!entity || !entity->active || entity->type != ENTITY_BALL) return;
    
    BallData* data = (BallData*)entity->data;
    if (!data) return;
    
    // If ball is stuck to paddle, update its position relative to paddle
    if (data->stuck && data->attachedPaddle) {
        PaddleData* paddleData = (PaddleData*)data->attachedPaddle->data;
        if (paddleData) {
            data->position.x = data->attachedPaddle->rect.x + data->offsetX;
            data->position.y = data->attachedPaddle->rect.y - data->radius;
            
            // Release ball if space is pressed
            if (IsKeyPressed(KEY_SPACE)) {
                ReleaseBallFromPaddle(entity);
            }
        }
    } else {
        // Update ball position based on velocity
        data->position.x += entity->velocity.x * deltaTime;
        data->position.y += entity->velocity.y * deltaTime;
        
        // Check if ball is stuck (not moving much)
        CheckStuckDetection(entity, deltaTime);
        
        // Handle collisions with walls
        CheckWallCollision(entity);
    }
    
    // Update ball position in the entity rectangle
    entity->rect.x = data->position.x - data->radius;
    entity->rect.y = data->position.y - data->radius;
    
    // Update power-up timers
    if (data->smash && data->smashTimer > 0) {
        data->smashTimer -= deltaTime;
        
        // Reset when timer expires
        if (data->smashTimer <= 0) {
            data->smash = false;
            data->damage = 1.0f;
            data->smashTimer = 0.0f;
            
            // Reset speed to normal if it was increased
            if (data->speedMultiplier > 1.5f) {
                data->speedMultiplier = 1.0f;
                
                // Normalize the velocity but maintain the direction
                float len = sqrtf(pow(entity->velocity.x, 2) + pow(entity->velocity.y, 2));
                if (len > 0) {
                    entity->velocity.x = (entity->velocity.x / len) * data->baseSpeed * data->speedMultiplier;
                    entity->velocity.y = (entity->velocity.y / len) * data->baseSpeed * data->speedMultiplier;
                }
            }
        }
    }
    
    // Update trail effect timer
    data->trailTime -= deltaTime;
    if (data->trailTime <= 0) {
        // TODO: Add trail effect particles
        data->trailTime = TRAIL_EFFECT_TIME;
    }
}

// Draw the ball
void DrawBall(Entity* entity) {
    if (!entity || !entity->active || entity->type != ENTITY_BALL) return;
    
    BallData* data = (BallData*)entity->data;
    if (!data) return;
    
    // Draw the ball
    DrawCircleV(data->position, data->radius, entity->color);
    
    // Draw effects for powerups if active
    if (data->smash) {
        // Draw a red glow for smash
        Color glowColor = ColorAlpha(RED, 0.5f);
        DrawCircleV(data->position, data->radius + 5, glowColor);
    }
}

// Handle collision with other entities
void OnBallCollision(Entity* ball, Entity* other) {
    if (!ball || !other || !ball->active || !other->active) return;
    if (ball->type != ENTITY_BALL) return;
    
    BallData* data = (BallData*)ball->data;
    if (!data || data->stuck) return;
    
    // Handle collision with paddle
    if (other->type == ENTITY_PADDLE) {
        PaddleData* paddleData = (PaddleData*)other->data;
        if (paddleData) {
            // If paddle is sticky, attach ball
            if (paddleData->sticky) {
                StickBallToPaddle(ball, other);
                return;
            }
            
            // Calculate bounce angle based on where the ball hit the paddle
            float paddleCenter = other->rect.x + other->rect.width / 2.0f;
            float hitPosition = data->position.x;
            float relativePosition = (hitPosition - paddleCenter) / (other->rect.width / 2.0f);
            
            // Maximum angle is 75 degrees (5*PI/12 radians)
            float bounceAngle = relativePosition * (5.0f * PI / 12.0f);
            
            // Ensure minimum bounce angle to prevent horizontal bounces
            if (fabsf(bounceAngle) < MINIMUM_BOUNCE_ANGLE) {
                bounceAngle = MINIMUM_BOUNCE_ANGLE * (bounceAngle >= 0 ? 1 : -1);
            }
            
            // Calculate new velocity
            float speed = sqrtf(pow(ball->velocity.x, 2) + pow(ball->velocity.y, 2));
            ball->velocity.x = speed * sinf(bounceAngle);
            ball->velocity.y = -speed * cosf(bounceAngle);  // Negative because the paddle is below
        }
    }
    // Handle collision with blocks
    else if (other->type == ENTITY_BLOCK) {
        BounceBall(ball, other);
    }
}

// Clean up ball resources
void DestroyBall(Entity* entity) {
    if (!entity || entity->type != ENTITY_BALL) return;
    
    // Free ball-specific data
    if (entity->data) {
        free(entity->data);
        entity->data = NULL;
    }
}

// Launch ball at a specific angle
void LaunchBall(Entity* ball, float initialAngle) {
    if (!ball || !ball->active || ball->type != ENTITY_BALL) return;
    
    BallData* data = (BallData*)ball->data;
    if (!data) return;
    
    // Calculate velocity components based on angle
    ball->velocity.x = data->baseSpeed * data->speedMultiplier * sinf(initialAngle);
    ball->velocity.y = data->baseSpeed * data->speedMultiplier * cosf(initialAngle);
    
    // Ball is no longer stuck
    data->stuck = false;
    data->attachedPaddle = NULL;
}

// Stick ball to paddle
void StickBallToPaddle(Entity* ball, Entity* paddle) {
    if (!ball || !paddle || !ball->active || !paddle->active) return;
    if (ball->type != ENTITY_BALL || paddle->type != ENTITY_PADDLE) return;
    
    BallData* data = (BallData*)ball->data;
    if (!data) return;
    
    // Calculate offset from paddle center
    float paddleCenter = paddle->rect.x + paddle->rect.width / 2.0f;
    float offset = data->position.x - paddleCenter;
    
    // Set ball as stuck to this paddle
    data->stuck = true;
    data->attachedPaddle = paddle;
    data->offsetX = offset + paddle->rect.width / 2.0f;
    
    // Update ball position to be on top of paddle
    data->position.x = paddle->rect.x + data->offsetX;
    data->position.y = paddle->rect.y - data->radius;
    
    // Stop the ball movement
    ball->velocity.x = 0;
    ball->velocity.y = 0;
}

// Release ball from paddle
void ReleaseBallFromPaddle(Entity* ball) {
    if (!ball || !ball->active || ball->type != ENTITY_BALL) return;
    
    BallData* data = (BallData*)ball->data;
    if (!data || !data->stuck) return;
    
    // Launch the ball upward at a random angle between -60 and 60 degrees
    float angle = (rand() % 120 - 60) * DEG2RAD;
    LaunchBall(ball, angle);
}

// Bounce ball based on collision
void BounceBall(Entity* ball, Entity* other) {
    if (!ball || !other || !ball->active || !other->active) return;
    if (ball->type != ENTITY_BALL) return;
    
    BallData* data = (BallData*)ball->data;
    if (!data) return;
    
    // Calculate the ball center
    Vector2 ballCenter = data->position;
    
    // Calculate the collision side
    Rectangle otherRect = other->rect;
    
    // Find the closest point on the rectangle to the circle center
    float closestX = fmaxf(otherRect.x, fminf(ballCenter.x, otherRect.x + otherRect.width));
    float closestY = fmaxf(otherRect.y, fminf(ballCenter.y, otherRect.y + otherRect.height));
    
    // Determine collision side by comparing distances
    float deltaX = closestX - ballCenter.x;
    float deltaY = closestY - ballCenter.y;
    
    // Check if we're colliding horizontally or vertically
    if (fabsf(deltaX) > fabsf(deltaY)) {
        // Horizontal collision
        ball->velocity.x = -ball->velocity.x;
        
        // Add a slight random angle variation
        ball->velocity.y += ((rand() % 100) / 500.0f - 0.1f) * data->baseSpeed;
    } else {
        // Vertical collision
        ball->velocity.y = -ball->velocity.y;
        
        // Add a slight random angle variation
        ball->velocity.x += ((rand() % 100) / 500.0f - 0.1f) * data->baseSpeed;
    }
    
    // Ensure minimum bounce angle to prevent horizontal/vertical bounces
    float speed = sqrtf(pow(ball->velocity.x, 2) + pow(ball->velocity.y, 2));
    float angle = atan2f(ball->velocity.x, ball->velocity.y);
    
    // Check if angle is too horizontal/vertical
    if (fabsf(fmodf(angle, PI / 2)) < MINIMUM_BOUNCE_ANGLE) {
        // Adjust the angle to ensure minimum bounce
        angle += MINIMUM_BOUNCE_ANGLE * (rand() % 2 == 0 ? 1 : -1);
        ball->velocity.x = speed * sinf(angle);
        ball->velocity.y = speed * cosf(angle);
    }
}

// Activate smash mode (power-up)
void ActivateSmash(Entity* ball, float duration) {
    if (!ball || !ball->active || ball->type != ENTITY_BALL) return;
    
    BallData* data = (BallData*)ball->data;
    if (!data) return;
    
    data->smash = true;
    data->damage = 2.0f;  // Double damage
    data->smashTimer = duration;
    
    // Increase speed for smash
    data->speedMultiplier = 2.0f;
    
    // Update velocity with new speed
    float len = sqrtf(pow(ball->velocity.x, 2) + pow(ball->velocity.y, 2));
    if (len > 0) {
        ball->velocity.x = (ball->velocity.x / len) * data->baseSpeed * data->speedMultiplier;
        ball->velocity.y = (ball->velocity.y / len) * data->baseSpeed * data->speedMultiplier;
    }
}

// Set ball speed multiplier
void SetBallSpeed(Entity* ball, float speedMultiplier) {
    if (!ball || !ball->active || ball->type != ENTITY_BALL) return;
    
    BallData* data = (BallData*)ball->data;
    if (!data) return;
    
    data->speedMultiplier = speedMultiplier;
    
    // Update velocity with new speed
    float len = sqrtf(pow(ball->velocity.x, 2) + pow(ball->velocity.y, 2));
    if (len > 0) {
        ball->velocity.x = (ball->velocity.x / len) * data->baseSpeed * data->speedMultiplier;
        ball->velocity.y = (ball->velocity.y / len) * data->baseSpeed * data->speedMultiplier;
    }
}

// Check collision with screen edges
void CheckWallCollision(Entity* ball) {
    if (!ball || !ball->active || ball->type != ENTITY_BALL) return;
    
    BallData* data = (BallData*)ball->data;
    if (!data) return;
    
    // Check collision with left and right walls
    if (data->position.x - data->radius <= 0) {
        data->position.x = data->radius;
        ball->velocity.x = fabs(ball->velocity.x);
    } else if (data->position.x + data->radius >= GetScreenWidth()) {
        data->position.x = GetScreenWidth() - data->radius;
        ball->velocity.x = -fabs(ball->velocity.x);
    }
    
    // Check collision with top wall
    if (data->position.y - data->radius <= 0) {
        data->position.y = data->radius;
        ball->velocity.y = fabs(ball->velocity.y);
    }
    
    // Check collision with bottom (ball out of bounds)
    // This will be handled by the game screen to determine game over state
}

// Check if ball is stuck (not moving much)
void CheckStuckDetection(Entity* ball, float deltaTime) {
    if (!ball || !ball->active || ball->type != ENTITY_BALL) return;
    
    BallData* data = (BallData*)ball->data;
    if (!data || data->stuck) return;
    
    // Calculate movement distance in this frame
    float movementDistance = sqrtf(pow(ball->velocity.x * deltaTime, 2) + 
                                   pow(ball->velocity.y * deltaTime, 2));
    
    // If we're moving slower than the threshold
    if (movementDistance < STUCK_DISTANCE_THRESHOLD * deltaTime) {
        data->stuckTimer += deltaTime;
        
        // If stuck for too long, reset with a random angle
        if (data->stuckTimer >= STUCK_DETECTION_TIME) {
            printf("Ball appears stuck, adjusting trajectory\n");
            
            // Set a random angle
            float angle = (rand() % 360) * DEG2RAD;
            float speed = data->baseSpeed * data->speedMultiplier;
            
            ball->velocity.x = speed * sinf(angle);
            ball->velocity.y = speed * cosf(angle);
            
            // Reset stuck timer
            data->stuckTimer = 0;
        }
    } else {
        // We're moving normally, reset the stuck timer
        data->stuckTimer = 0;
    }
} 