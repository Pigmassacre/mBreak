#include "ball.h"
#include "block.h"
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
    data->stuck = false;  // Ball starts unstuck for mBreak
    data->attachedPaddle = NULL;
    data->owner = NULL;  // No owner initially
    data->ownerID = 0;   // 0 means no owner
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
    
    // Determine ball color based on owner
    Color ballColor = entity->color;
    if (data->ownerID == 1) {
        ballColor = BLUE;
    } else if (data->ownerID == 2) {
        ballColor = RED;
    }
    
    // Draw the ball
    DrawCircleV(data->position, data->radius, ballColor);
    
    // Draw special effects for power-ups if active
    if (data->smash) {
        // Draw a glow effect for smash mode
        Color glowColor = ColorAlpha(WHITE, 0.5f);
        DrawCircleLines(data->position.x, data->position.y, data->radius + 2, glowColor);
    }
}

// Handle collision with other entities
void OnBallCollision(Entity* ball, Entity* other) {
    if (!ball || !other || !ball->active || !other->active) return;
    if (ball->type != ENTITY_BALL) return;
    
    BallData* ballData = (BallData*)ball->data;
    if (!ballData) return;
    
    // Handle collision with paddle
    if (other->type == ENTITY_PADDLE) {
        PaddleData* paddleData = (PaddleData*)other->data;
        if (!paddleData) return;
        
        // Change ownership when a paddle is hit
        ChangeBallOwner(ball, other);
        
        // Bounce the ball
        BounceBall(ball, other);
        
        // Apply additional effects
        if (paddleData->sticky) {
            // Stick ball to paddle
            StickBallToPaddle(ball, other);
        }
    }
    
    // Handle collision with block
    if (other->type == ENTITY_BLOCK) {
        // Bounce the ball
        BounceBall(ball, other);
        
        // Deal damage to the block based on ball properties
        BlockData* blockData = (BlockData*)other->data;
        if (blockData) {
            // Deal different damage based on ball ownership and block ownership
            if (ballData->ownerID != 0) {
                // Get player ID associated with the block
                int blockPlayerID = 0;
                
                // Determine block owner based on position or flipped property
                if (blockData->flipped) {
                    blockPlayerID = 2; // Player 2's block
                } else {
                    blockPlayerID = 1; // Player 1's block
                }
                
                // Calculate damage based on ownership
                int damage = 1;
                
                // Apply full damage if ball is owned by opponent
                if (ballData->ownerID != blockPlayerID) {
                    damage = ballData->smash ? 2 : 1; // Double damage if smash is active
                } else {
                    // Reduced damage if hitting own blocks
                    damage = 0; // No damage to own blocks for now
                }
                
                // Apply damage
                if (damage > 0) {
                    DamageBlock(other, damage);
                }
            }
        }
    }
    
    // Handle collision with other balls
    if (other->type == ENTITY_BALL) {
        // Bounce the balls off each other
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

// Bounce the ball off another entity
void BounceBall(Entity* ball, Entity* other) {
    if (!ball || !other || !ball->active || !other->active || ball->type != ENTITY_BALL) return;
    
    BallData* data = (BallData*)ball->data;
    if (!data) return;
    
    // Calculate current ball speed
    float speed = sqrtf(powf(ball->velocity.x, 2) + powf(ball->velocity.y, 2));
    
    // Handle bounce differently based on the type of entity we hit
    if (other->type == ENTITY_PADDLE) {
        PaddleData* paddleData = (PaddleData*)other->data;
        if (!paddleData) return;
        
        if (paddleData->moveVertical) {
            // For vertical paddles (mBreak style)
            // Calculate bounce angle based on where the ball hit the paddle
            float paddleCenter = other->rect.y + other->rect.height / 2.0f;
            float hitPosition = data->position.y;
            float relativePosition = (hitPosition - paddleCenter) / (other->rect.height / 2.0f);
            
            // Determine if the ball hit the left paddle (player 1) or right paddle (player 2)
            bool hitLeftPaddle = (paddleData->playerID == 1);
            
            // Maximum angle is 75 degrees (5*PI/12 radians)
            float bounceAngle = relativePosition * (5.0f * PI / 12.0f);
            
            // Ensure minimum bounce angle to prevent vertical bounces
            if (fabsf(bounceAngle) < MINIMUM_BOUNCE_ANGLE) {
                bounceAngle = MINIMUM_BOUNCE_ANGLE * (bounceAngle >= 0 ? 1 : -1);
            }
            
            // Add a small random variation to prevent predictable patterns
            bounceAngle += ((float)GetRandomValue(-5, 5) / 100.0f);
            
            // Calculate new velocity - reverse X direction based on which paddle was hit
            if (hitLeftPaddle) {
                // Ball hit left paddle, should bounce to the right
                ball->velocity.x = speed * cosf(bounceAngle);
                ball->velocity.y = speed * sinf(bounceAngle);
            } else {
                // Ball hit right paddle, should bounce to the left
                ball->velocity.x = -speed * cosf(bounceAngle);
                ball->velocity.y = speed * sinf(bounceAngle);
            }
        } else {
            // For horizontal paddles (original Breakout style)
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
            ball->velocity.x = speed * sinf(bounceAngle);
            ball->velocity.y = -speed * cosf(bounceAngle);  // Negative because the paddle is below
        }
    } 
    else if (other->type == ENTITY_BLOCK) {
        // Determine which side of the block was hit
        float overlapLeft = (data->position.x + data->radius) - other->rect.x;
        float overlapRight = (other->rect.x + other->rect.width) - (data->position.x - data->radius);
        float overlapTop = (data->position.y + data->radius) - other->rect.y;
        float overlapBottom = (other->rect.y + other->rect.height) - (data->position.y - data->radius);
        
        // Find the smallest overlap
        float minOverlap = overlapLeft;
        char side = 'L';
        
        if (overlapRight < minOverlap) {
            minOverlap = overlapRight;
            side = 'R';
        }
        
        if (overlapTop < minOverlap) {
            minOverlap = overlapTop;
            side = 'T';
        }
        
        if (overlapBottom < minOverlap) {
            minOverlap = overlapBottom;
            side = 'B';
        }
        
        // Bounce based on the side hit
        if (side == 'L' || side == 'R') {
            ball->velocity.x *= -1;
        } else {
            ball->velocity.y *= -1;
        }
        
        // Add a tiny random variation to prevent getting stuck
        ball->velocity.x += ((float)GetRandomValue(-5, 5) / 100.0f) * speed;
        ball->velocity.y += ((float)GetRandomValue(-5, 5) / 100.0f) * speed;
    }
    else if (other->type == ENTITY_BALL) {
        // For ball-to-ball collisions, use elastic collision physics
        BallData* otherBallData = (BallData*)other->data;
        if (!otherBallData) return;
        
        // Calculate normal vector
        Vector2 normal = {
            data->position.x - otherBallData->position.x,
            data->position.y - otherBallData->position.y
        };
        
        // Normalize
        float distance = sqrtf(normal.x * normal.x + normal.y * normal.y);
        normal.x /= distance;
        normal.y /= distance;
        
        // Calculate relative velocity
        Vector2 relativeVelocity = {
            ball->velocity.x - other->velocity.x,
            ball->velocity.y - other->velocity.y
        };
        
        // Calculate dot product
        float dotProduct = relativeVelocity.x * normal.x + relativeVelocity.y * normal.y;
        
        // Apply impulse
        float impulseFactor = 2.0f * dotProduct;
        ball->velocity.x -= impulseFactor * normal.x;
        ball->velocity.y -= impulseFactor * normal.y;
        
        // Ensure balls don't get stuck together by pushing slightly apart
        data->position.x += normal.x * 1.0f;
        data->position.y += normal.y * 1.0f;
    }
    
    // Normalize velocity to ensure consistent speed
    float newSpeed = sqrtf(powf(ball->velocity.x, 2) + powf(ball->velocity.y, 2));
    if (newSpeed > 0) {
        ball->velocity.x = (ball->velocity.x / newSpeed) * speed;
        ball->velocity.y = (ball->velocity.y / newSpeed) * speed;
    }
}

// Check for collision with walls and handle bounces
void CheckWallCollision(Entity* ball) {
    if (!ball || !ball->active || ball->type != ENTITY_BALL) return;
    
    BallData* data = (BallData*)ball->data;
    if (!data) return;
    
    // Game area boundaries (mBreak style)
    int gameAreaLeft = 0;
    int gameAreaRight = 800;
    int gameAreaTop = 50;
    int gameAreaBottom = 550;
    
    // Check top and bottom walls
    if (data->position.y - data->radius <= gameAreaTop) {
        // Top wall collision
        data->position.y = gameAreaTop + data->radius;
        ball->velocity.y *= -1;
        
        // Add small random variation to prevent getting stuck
        float speed = sqrtf(powf(ball->velocity.x, 2) + powf(ball->velocity.y, 2));
        ball->velocity.x += ((float)GetRandomValue(-5, 5) / 100.0f) * speed;
    }
    else if (data->position.y + data->radius >= gameAreaBottom) {
        // Bottom wall collision
        data->position.y = gameAreaBottom - data->radius;
        ball->velocity.y *= -1;
        
        // Add small random variation to prevent getting stuck
        float speed = sqrtf(powf(ball->velocity.x, 2) + powf(ball->velocity.y, 2));
        ball->velocity.x += ((float)GetRandomValue(-5, 5) / 100.0f) * speed;
    }
    
    // For horizontal walls, we don't bounce - ball goes out of bounds and resets
    // This is handled in the gameplay loop rather than here
    // In mBreak, if a ball goes out on the left or right side, the other player scores
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

// Change the ball's owner
void ChangeBallOwner(Entity* ball, Entity* newOwner) {
    if (!ball || !ball->active || ball->type != ENTITY_BALL || !newOwner) return;
    
    BallData* ballData = (BallData*)ball->data;
    if (!ballData) return;
    
    // Only change owner if it's a paddle
    if (newOwner->type == ENTITY_PADDLE) {
        PaddleData* paddleData = (PaddleData*)newOwner->data;
        if (paddleData) {
            ballData->owner = newOwner;
            ballData->ownerID = paddleData->playerID;
            
            // Slightly increase ball speed on each paddle hit
            float newSpeed = ballData->speedMultiplier + 0.1f;
            if (newSpeed <= 2.0f) { // Cap speed increase
                SetBallSpeed(ball, newSpeed);
            }
        }
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
