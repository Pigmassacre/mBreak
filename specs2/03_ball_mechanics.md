# Ball Mechanics and Physics

This document details the ball mechanics and physics implementation for the mBreak game, based on the current implementation in `objects/ball.py`.

## Ball Entity Structure

```c
typedef struct Ball {
    // Core properties
    Vector2 position;        // Float precision position
    Rectangle rect;          // Collision rectangle
    Vector2 previousPos;     // Position in previous frame for collision
    float angle;             // Movement angle in radians
    float speed;             // Current movement speed
    Color color;             // Ball color
    Texture2D texture;       // Ball texture
    
    // Ownership and damage
    Player* owner;           // Current ball owner
    int damage;              // Base damage value
    float damageToOwnBlocks; // Damage multiplier to own blocks (0.25)
    int paddleHits;          // Count of paddle hits
    
    // Speed properties
    float baseSpeed;         // Base movement speed (1.5 * FPS)
    float maxSpeed;          // Maximum allowed speed (5 * FPS)
    float speedStep;         // Speed increment value (0.75 * FPS)
    float minVerticalAngle;  // Minimum vertical angle (0.32 radians)
    
    // Effects
    SpriteList* effectList;  // List of active effects
    Shadow* shadow;          // Shadow effect
    bool smashActive;        // Whether smash is active
    int smashStack;          // Current smash stack count
    
    // Visual effects
    int traceCounter;        // Counter for trace spawning
    float traceSpawnRate;    // Rate to spawn trace effects (0.53 * FPS)
    int particleAmount;      // Amount of particles to spawn (3)
    
    // Smash properties
    float smashSpeed;        // Speed increase per smash (0.2 * FPS)
    float smashDamageFactor; // Damage multiplier for smash
    int smashMaxStack;       // Maximum smash stack (12)
    float smashSizeIncrease; // Visual size increase per stack
    
    // Collision handling
    Vector2 stuckCheckPos;   // Position for stuck detection
    int stuckCounter;        // Counter for stuck detection
    int stuckTime;           // Time since last stuck check
    
    // Sound
    Sound hitSound;          // Sound played on collision
} Ball;
```

## Initialization

```c
Ball* CreateBall(float x, float y, float angle, Player* owner) {
    Ball* ball = (Ball*)MemAlloc(sizeof(Ball));
    
    // Set position
    ball->position = (Vector2){ x, y };
    ball->previousPos = ball->position;
    
    // Create rect
    ball->rect = (Rectangle){ x, y, Ball_WIDTH, Ball_HEIGHT };
    
    // Set owner
    ball->owner = owner;
    
    // Set angle
    ball->angle = angle;
    
    // Set default values
    ball->speed = Ball_BASE_SPEED;
    ball->baseSpeed = Ball_BASE_SPEED;
    ball->maxSpeed = Ball_MAX_SPEED;
    ball->speedStep = Ball_SPEED_STEP;
    ball->damage = Ball_DAMAGE;
    ball->damageToOwnBlocks = Ball_DAMAGE_OWN_BLOCKS_FACTOR;
    ball->minVerticalAngle = Ball_MIN_VERTICAL_ANGLE;
    ball->traceSpawnRate = Ball_TRACE_SPAWN_RATE;
    ball->particleAmount = Ball_PARTICLE_AMOUNT;
    
    // Smash properties
    ball->smashActive = false;
    ball->smashStack = 0;
    ball->smashSpeed = Ball_SMASH_SPEED;
    ball->smashDamageFactor = Ball_SMASH_DAMAGE_FACTOR;
    ball->smashMaxStack = Ball_SMASH_MAX_STACK;
    ball->smashSizeIncrease = Ball_SMASH_SIZE_INCREASE;
    
    // Stuck detection
    ball->stuckCheckPos = ball->position;
    ball->stuckCounter = 0;
    ball->stuckTime = 0;
    
    // Visual
    ball->texture = LoadTexture("res/ball/ball.png");
    ball->color = owner->color;
    
    // Initialize effect list
    ball->effectList = CreateSpriteList();
    
    // Create shadow
    ball->shadow = CreateShadow(ball);
    
    // Add to groups
    AddBallToGroup(ball, owner->ballGroup);
    AddBallToGroup(ball, mainBallGroup);
    
    // Set sound
    ball->hitSound = ballSound;
    
    return ball;
}
```

## Core Physics and Movement

```c
void UpdateBall(Ball* ball, GameClock* clock) {
    // Store previous position for collision detection
    ball->previousPos = ball->position;
    
    // Calculate movement based on angle and speed
    float delta = GetDeltaTime(clock);
    ball->position.x += cosf(ball->angle) * ball->speed * delta;
    ball->position.y += sinf(ball->angle) * ball->speed * delta;
    
    // Update rect position
    ball->rect.x = ball->position.x;
    ball->rect.y = ball->position.y;
    
    // Update stuck detection
    ball->stuckTime += GetMilliseconds(clock);
    if (ball->stuckTime >= Ball_STUCK_DETECTION_TIME) {
        float distance = Vector2Distance(ball->position, ball->stuckCheckPos);
        
        if (distance < Ball_STUCK_DETECTION_DISTANCE) {
            // Ball might be stuck
            ball->stuckCounter++;
            
            if (ball->stuckCounter >= 3) {
                // Ball is definitely stuck, randomize angle
                ball->angle = GetRandomFloat(0, 2 * PI);
                ball->stuckCounter = 0;
            }
        } else {
            // Ball is moving normally
            ball->stuckCounter = 0;
        }
        
        // Reset stuck detection
        ball->stuckCheckPos = ball->position;
        ball->stuckTime = 0;
    }
    
    // Spawn trace effects based on trace counter
    ball->traceCounter++;
    if (ball->traceCounter >= ball->traceSpawnRate) {
        CreateTrace(ball->position.x + ball->rect.width/2, 
                    ball->position.y + ball->rect.height/2,
                    ball->rect.width/2, ball->rect.height/2, ball->color);
        ball->traceCounter = 0;
    }
    
    // Check collisions
    CheckBallCollisions(ball);
    
    // Update effects
    UpdateSpriteList(ball->effectList, clock);
}
```

## Collision Handling

```c
void CheckBallCollisions(Ball* ball) {
    // Check level boundaries
    CheckBallWallCollision(ball);
    
    // Check block collisions
    for (int i = 0; i < GetBlockCount(); i++) {
        Block* block = GetBlockAt(i);
        if (CheckCollisionRecs(ball->rect, block->rect)) {
            HandleBallBlockCollision(ball, block);
        }
    }
    
    // Check paddle collisions
    for (int i = 0; i < GetPaddleCount(); i++) {
        Paddle* paddle = GetPaddleAt(i);
        if (CheckCollisionRecs(ball->rect, paddle->rect)) {
            HandleBallPaddleCollision(ball, paddle);
        }
    }
    
    // Check other ball collisions
    for (int i = 0; i < GetBallCount(); i++) {
        Ball* otherBall = GetBallAt(i);
        if (otherBall != ball && CheckCollisionRecs(ball->rect, otherBall->rect)) {
            HandleBallBallCollision(ball, otherBall);
        }
    }
    
    // Check powerup collisions
    for (int i = 0; i < GetPowerupCount(); i++) {
        Powerup* powerup = GetPowerupAt(i);
        if (CheckCollisionRecs(ball->rect, powerup->rect)) {
            powerup->hit(powerup, ball);
        }
    }
}
```

### Wall Collision

```c
void CheckBallWallCollision(Ball* ball) {
    bool collision = false;
    
    // Left wall
    if (ball->position.x < 0) {
        ball->position.x = 0;
        ball->angle = PI - ball->angle;
        collision = true;
    }
    
    // Right wall
    if (ball->position.x + ball->rect.width > LEVEL_WIDTH) {
        ball->position.x = LEVEL_WIDTH - ball->rect.width;
        ball->angle = PI - ball->angle;
        collision = true;
    }
    
    // Top wall
    if (ball->position.y < 0) {
        ball->position.y = 0;
        ball->angle = -ball->angle;
        collision = true;
    }
    
    // Bottom wall
    if (ball->position.y + ball->rect.height > LEVEL_HEIGHT) {
        ball->position.y = LEVEL_HEIGHT - ball->rect.height;
        ball->angle = -ball->angle;
        collision = true;
    }
    
    // If collision occurred
    if (collision) {
        // Enforce minimum vertical angle
        EnforceMinVerticalAngle(ball);
        
        // Add small random variation
        ball->angle += GetRandomFloat(-Ball_RANDOM_BOUNCE_VARIATION, Ball_RANDOM_BOUNCE_VARIATION);
        
        // Normalize angle
        while (ball->angle < 0) ball->angle += 2 * PI;
        while (ball->angle >= 2 * PI) ball->angle -= 2 * PI;
        
        // Play sound
        PlaySound(ball->hitSound);
        
        // Trigger effects
        TriggerOnHitWall(ball);
    }
}
```

### Paddle Collision

```c
void HandleBallPaddleCollision(Ball* ball, Paddle* paddle) {
    // Calculate collision point and normal
    Vector2 collisionPoint = GetCollisionPoint(ball, paddle);
    Vector2 normal = GetCollisionNormal(collisionPoint, paddle);
    
    // Calculate reflection angle
    float incidentAngle = ball->angle;
    float reflectionAngle = 2 * Vector2Angle(normal, VECTOR2_ZERO) - incidentAngle;
    
    // Adjust angle based on paddle position
    float paddleCenter = paddle->rect.y + paddle->rect.height / 2;
    float relativePosition = (collisionPoint.y - paddleCenter) / (paddle->rect.height / 2);
    
    // Adjust angle based on relative position (-1 to 1)
    reflectionAngle += relativePosition * (PI / 4);  // Up to 45 degrees adjustment
    
    // Ensure minimum bounce angle
    if (fabsf(reflectionAngle - PI/2) < Ball_MIN_BOUNCE_ANGLE) {
        reflectionAngle = PI/2 + (reflectionAngle > PI/2 ? Ball_MIN_BOUNCE_ANGLE : -Ball_MIN_BOUNCE_ANGLE);
    }
    if (fabsf(reflectionAngle - 3*PI/2) < Ball_MIN_BOUNCE_ANGLE) {
        reflectionAngle = 3*PI/2 + (reflectionAngle > 3*PI/2 ? Ball_MIN_BOUNCE_ANGLE : -Ball_MIN_BOUNCE_ANGLE);
    }
    
    // Set new angle
    ball->angle = reflectionAngle;
    
    // Add small random variation
    ball->angle += GetRandomFloat(-Ball_RANDOM_BOUNCE_VARIATION, Ball_RANDOM_BOUNCE_VARIATION);
    
    // Normalize angle
    while (ball->angle < 0) ball->angle += 2 * PI;
    while (ball->angle >= 2 * PI) ball->angle -= 2 * PI;
    
    // Increase speed
    ball->speed += ball->speedStep;
    if (ball->speed > ball->maxSpeed) {
        ball->speed = ball->maxSpeed;
    }
    
    // Move ball out of paddle
    RepositionBallOutsidePaddle(ball, paddle);
    
    // Update ownership if needed
    UpdateBallOwnership(ball, paddle);
    
    // Increment paddle hit counter
    ball->paddleHits++;
    
    // Give energy to paddle owner
    float energyGain = CalculateEnergyGain(ball, paddle);
    paddle->owner->energy += energyGain;
    
    // Play sound
    PlaySound(ball->hitSound);
    
    // Trigger effects
    TriggerOnHitPaddle(ball, paddle);
}
```

### Block Collision

```c
void HandleBallBlockCollision(Ball* ball, Block* block) {
    // Calculate collision point and side
    Vector2 collisionPoint = GetCollisionPoint(ball, block);
    int collisionSide = GetCollisionSide(ball->previousPos, collisionPoint, block);
    
    // Calculate damage
    float damage = ball->damage;
    if (block->owner == ball->owner) {
        // Reduced damage to own blocks
        damage *= ball->damageToOwnBlocks;
    }
    
    // Apply smash multiplier if active
    if (ball->smashActive) {
        damage *= (1.0f + (ball->smashStack * ball->smashDamageFactor));
    }
    
    // Apply damage to block
    block->on_hit(block, damage, ball->owner);
    
    // Adjust ball angle based on collision side
    switch (collisionSide) {
        case SIDE_TOP:
        case SIDE_BOTTOM:
            ball->angle = -ball->angle;
            break;
        case SIDE_LEFT:
        case SIDE_RIGHT:
            ball->angle = PI - ball->angle;
            break;
    }
    
    // Enforce minimum vertical angle
    EnforceMinVerticalAngle(ball);
    
    // Add small random variation
    ball->angle += GetRandomFloat(-Ball_RANDOM_BOUNCE_VARIATION, Ball_RANDOM_BOUNCE_VARIATION);
    
    // Normalize angle
    while (ball->angle < 0) ball->angle += 2 * PI;
    while (ball->angle >= 2 * PI) ball->angle -= 2 * PI;
    
    // Move ball out of block
    RepositionBallOutsideBlock(ball, block);
    
    // Play sound
    PlaySound(ball->hitSound);
    
    // Spawn particles
    SpawnBallBlockCollisionParticles(ball, collisionPoint);
    
    // Trigger effects
    TriggerOnHitBlock(ball, block);
}
```

### Ball-Ball Collision

```c
void HandleBallBallCollision(Ball* ball1, Ball* ball2) {
    // Calculate collision vector
    Vector2 collision = Vector2Subtract(ball2->position, ball1->position);
    float distance = Vector2Length(collision);
    
    // Normalize collision vector
    Vector2 normal = Vector2Scale(collision, 1.0f / distance);
    
    // Calculate relative velocity
    Vector2 velocity1 = Vector2FromAngle(ball1->angle, ball1->speed);
    Vector2 velocity2 = Vector2FromAngle(ball2->angle, ball2->speed);
    Vector2 relativeVelocity = Vector2Subtract(velocity1, velocity2);
    
    // Calculate impulse
    float dotProduct = Vector2DotProduct(relativeVelocity, normal);
    
    // Only collide if balls are moving toward each other
    if (dotProduct < 0) {
        // Exchange momentum
        float impulse = -2.0f * dotProduct / (2.0f);  // Assuming equal mass
        
        // Apply impulse to velocities
        Vector2 impulseVector = Vector2Scale(normal, impulse);
        Vector2 newVelocity1 = Vector2Subtract(velocity1, impulseVector);
        Vector2 newVelocity2 = Vector2Add(velocity2, impulseVector);
        
        // Update ball angles and speeds
        ball1->angle = Vector2Angle(newVelocity1, VECTOR2_ZERO);
        ball1->speed = Vector2Length(newVelocity1);
        
        ball2->angle = Vector2Angle(newVelocity2, VECTOR2_ZERO);
        ball2->speed = Vector2Length(newVelocity2);
        
        // Reposition balls to prevent sticking
        RepositionBallsAfterCollision(ball1, ball2);
        
        // Play sound
        PlaySound(ball1->hitSound);
        
        // Trigger effects
        TriggerOnHitBall(ball1, ball2);
        TriggerOnHitBall(ball2, ball1);
        
        // Spawn particles at collision point
        Vector2 collisionPoint = Vector2Add(
            ball1->position,
            Vector2Scale(normal, ball1->rect.width / 2)
        );
        SpawnBallBallCollisionParticles(collisionPoint, ball1->color, ball2->color);
    }
}
```

## Smash Mechanics

```c
void ActivateSmash(Ball* ball) {
    // Already at max stack
    if (ball->smashStack >= ball->smashMaxStack) {
        return;
    }
    
    // Activate smash if not already active
    if (!ball->smashActive) {
        ball->smashActive = true;
    }
    
    // Increment smash stack
    ball->smashStack++;
    
    // Increase speed based on smash
    ball->speed += ball->smashSpeed;
    if (ball->speed > ball->maxSpeed) {
        ball->speed = ball->maxSpeed;
    }
    
    // Visual effect for smash activation
    Color startColor = RAYWHITE;
    startColor.a = 255;
    Color endColor = RAYWHITE;
    endColor.a = 0;
    
    // Create flash effect
    Flash* flash = CreateFlash(ball, startColor, endColor, Ball_SMASH_EFFECT_TICKS);
    AddToSpriteList(ball->effectList, flash);
    
    // Scale up the ball visual size based on smash stack
    float scaleFactor = 1.0f + (ball->smashStack * ball->smashSizeIncrease);
    ScaleBallVisual(ball, scaleFactor);
}

void DeactivateSmash(Ball* ball) {
    if (!ball->smashActive) {
        return;
    }
    
    // Reset smash properties
    ball->smashActive = false;
    ball->smashStack = 0;
    
    // Reset speed to base speed
    ball->speed = ball->baseSpeed;
    
    // Reset ball visual size
    ScaleBallVisual(ball, 1.0f);
}
```

## Helper Functions

```c
void EnforceMinVerticalAngle(Ball* ball) {
    // Ensure ball doesn't get stuck bouncing vertically
    float normalizedAngle = fmodf(ball->angle, 2 * PI);
    if (normalizedAngle < 0) normalizedAngle += 2 * PI;
    
    // Check if too close to straight up
    if (fabsf(normalizedAngle - (3 * PI / 2)) < ball->minVerticalAngle) {
        if (normalizedAngle < 3 * PI / 2) {
            ball->angle = 3 * PI / 2 - ball->minVerticalAngle;
        } else {
            ball->angle = 3 * PI / 2 + ball->minVerticalAngle;
        }
    }
    
    // Check if too close to straight down
    if (fabsf(normalizedAngle - (PI / 2)) < ball->minVerticalAngle) {
        if (normalizedAngle < PI / 2) {
            ball->angle = PI / 2 - ball->minVerticalAngle;
        } else {
            ball->angle = PI / 2 + ball->minVerticalAngle;
        }
    }
}

void UpdateBallOwnership(Ball* ball, Paddle* paddle) {
    // Only transfer ownership if ball hit enemy paddle
    if (ball->owner != paddle->owner) {
        // Remove from current owner's group
        RemoveBallFromGroup(ball, ball->owner->ballGroup);
        
        // Set new owner
        ball->owner = paddle->owner;
        
        // Add to new owner's group
        AddBallToGroup(ball, ball->owner->ballGroup);
        
        // Update ball color
        ball->color = ball->owner->color;
        
        // Reset paddle hit counter
        ball->paddleHits = 0;
    }
}

float CalculateEnergyGain(Ball* ball, Paddle* paddle) {
    // Base energy values
    float baseEnergy = 5.0f;
    float multiplier = 1.0f + (ball->paddleHits * 0.5f);
    
    // Cap multiplier
    if (multiplier > 3.0f) multiplier = 3.0f;
    
    // Different gain for own vs enemy balls
    if (ball->owner == paddle->owner) {
        // Own ball - half energy
        return (baseEnergy * multiplier) / 2.0f;
    } else {
        // Enemy ball - full energy
        return baseEnergy * multiplier;
    }
}
```

## Drawing

```c
void DrawBall(Ball* ball) {
    // Calculate draw position
    Vector2 drawPos = GetWorldToScreen(ball->position);
    
    // Draw shadow
    DrawShadow(ball->shadow);
    
    // Draw the ball texture with color tint
    DrawTexture(ball->texture, drawPos.x, drawPos.y, ball->color);
    
    // Draw effects
    DrawSpriteList(ball->effectList);
    
    // Debug visualization
    if (IsDebugMode()) {
        DrawRectangleLines(
            drawPos.x, drawPos.y,
            ball->rect.width, ball->rect.height,
            RED
        );
        
        // Draw velocity vector
        Vector2 center = {
            drawPos.x + ball->rect.width/2,
            drawPos.y + ball->rect.height/2
        };
        Vector2 endPoint = {
            center.x + cosf(ball->angle) * 20,
            center.y + sinf(ball->angle) * 20
        };
        DrawLineV(center, endPoint, YELLOW);
    }
}
```

## Effect Triggers

```c
void TriggerOnHitWall(Ball* ball) {
    // Notify all attached effects
    for (int i = 0; i < ball->effectList->count; i++) {
        Effect* effect = (Effect*)ball->effectList->items[i];
        effect->on_hit_wall(effect);
    }
}

void TriggerOnHitPaddle(Ball* ball, Paddle* paddle) {
    // Notify all attached effects
    for (int i = 0; i < ball->effectList->count; i++) {
        Effect* effect = (Effect*)ball->effectList->items[i];
        effect->on_hit_paddle(effect, paddle);
    }
}

void TriggerOnHitBlock(Ball* ball, Block* block) {
    // Notify all attached effects
    for (int i = 0; i < ball->effectList->count; i++) {
        Effect* effect = (Effect*)ball->effectList->items[i];
        effect->on_hit_block(effect, block);
    }
}

void TriggerOnHitBall(Ball* ball, Ball* otherBall) {
    // Notify all attached effects
    for (int i = 0; i < ball->effectList->count; i++) {
        Effect* effect = (Effect*)ball->effectList->items[i];
        effect->on_hit_ball(effect, otherBall);
    }
}
```

## Constants

```c
// Basic properties
#define Ball_WIDTH 10
#define Ball_HEIGHT 10

// Speed values
#define Ball_BASE_SPEED (1.5f * GAME_FPS)
#define Ball_MAX_SPEED (5.0f * GAME_FPS)
#define Ball_SPEED_STEP (0.75f * GAME_FPS)

// Physics constants
#define Ball_MIN_BOUNCE_ANGLE (PI / 10.0f)
#define Ball_MIN_VERTICAL_ANGLE 0.32f
#define Ball_RANDOM_BOUNCE_VARIATION 0.1f
#define Ball_PADDLE_NUDGE_DISTANCE 1.34f

// Stuck detection
#define Ball_STUCK_DETECTION_TIME 500
#define Ball_STUCK_DETECTION_DISTANCE 5

// Visual effects
#define Ball_TRACE_SPAWN_RATE (0.53f * GAME_FPS)
#define Ball_PARTICLE_AMOUNT 3

// Damage values
#define Ball_DAMAGE 10
#define Ball_DAMAGE_OWN_BLOCKS_FACTOR 0.25f

// Smash properties
#define Ball_SMASH_SPEED (0.2f * GAME_FPS)
#define Ball_SMASH_DAMAGE_FACTOR 1.0f
#define Ball_SMASH_MAX_STACK 12
#define Ball_SMASH_SIZE_INCREASE 0.1f
#define Ball_SMASH_EFFECT_TICKS (10 * GAME_FPS)

// Hit effect properties
#define Ball_HIT_EFFECT_TICKS (8 * GAME_FPS)
```

## Memory Management

```c
void DestroyBall(Ball* ball) {
    // Remove from groups
    RemoveBallFromGroup(ball, ball->owner->ballGroup);
    RemoveBallFromGroup(ball, mainBallGroup);
    
    // Destroy effects
    for (int i = 0; i < ball->effectList->count; i++) {
        Effect* effect = (Effect*)ball->effectList->items[i];
        DestroyEffect(effect);
    }
    
    // Destroy effect list
    DestroySpriteList(ball->effectList);
    
    // Destroy shadow
    DestroyShadow(ball->shadow);
    
    // Free memory
    MemFree(ball);
}
```

This specification details the ball mechanics implementation for the C + Raylib port, based on the actual implementation in the Python version. It covers all aspects of ball behavior, physics, and visual effects. 