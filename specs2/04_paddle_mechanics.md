# Paddle Mechanics and AI System

This document details the paddle mechanics and AI system for the mBreak game, based on the current implementation in `objects/paddle.py`.

## Paddle Entity Structure

```c
typedef struct Paddle {
    // Core properties
    Vector2 position;        // Float precision position
    Rectangle rect;          // Collision rectangle
    Color color;             // Paddle color
    
    // Textures
    Texture2D topTexture;    // Top segment texture
    Texture2D middleTexture; // Middle (repeatable) segment
    Texture2D bottomTexture; // Bottom segment texture
    
    // Movement properties
    float velocity_y;        // Current vertical velocity
    float acceleration;      // Movement acceleration (1.0 * FPS)
    float retardation;       // Deceleration when not moving (2.5 * FPS)
    float max_speed;         // Maximum movement speed (2.5 * FPS)
    
    // Size properties
    float actual_width;      // Actual width (can exceed limits)
    float actual_height;     // Actual height (can exceed limits)
    float max_height;        // Maximum allowed height (33)
    float min_height;        // Minimum allowed height (11)
    float max_width;         // Maximum allowed width
    float min_width;         // Minimum allowed width
    
    // Visual effects
    float center_x;          // Desired x position for visuals
    float nudge_distance;    // Current visual displacement
    float stabilize_speed;   // Speed of return to center (0.1 * FPS)
    float max_nudge_distance; // Maximum visual displacement (2.5)
    Shadow* shadow;          // Shadow effect
    SpriteList* effectList;  // List of active effects
    
    // Input state
    bool key_up_pressed;     // Whether up key is pressed
    bool key_down_pressed;   // Whether down key is pressed
    
    // Ownership
    Player* owner;           // Paddle owner
    
    // AI properties
    bool is_ai;              // Whether paddle is AI controlled
    float decision_cooldown; // Time between AI decisions (0.08 seconds)
    float last_decision_time; // Time of last decision
    float target_y;          // Target y position
    float target_movement_buffer; // Distance buffer before stopping (3 pixels)
    int missed_balls;        // Counter for missed balls
    float direction_change_cooldown; // Cooldown for direction changes (0.1 seconds)
    float last_direction_change; // Time of last direction change
    
    // AI targeting
    void* focused_item;      // Currently focused ball or powerup
    float min_distance;      // Minimum distance to target
    Vector2 predicted_y;     // Predicted y position
    void* current_prediction; // Current trajectory prediction
} Paddle;
```

## Initialization

```c
Paddle* CreatePaddle(float x, float y, Player* owner) {
    Paddle* paddle = (Paddle*)MemAlloc(sizeof(Paddle));
    
    // Set position
    paddle->position.x = x;
    paddle->position.y = y;
    paddle->center_x = x;  // For visual effects
    
    // Create rect
    paddle->rect = (Rectangle){ x, y, Paddle_WIDTH, Paddle_HEIGHT };
    
    // Set owner
    paddle->owner = owner;
    
    // Set default values
    paddle->velocity_y = 0;
    paddle->acceleration = Paddle_ACCELERATION;
    paddle->retardation = Paddle_RETARDATION;
    paddle->max_speed = Paddle_MAX_SPEED;
    
    // Size properties
    paddle->actual_width = paddle->rect.width;
    paddle->actual_height = paddle->rect.height;
    paddle->max_height = Paddle_MAX_HEIGHT;
    paddle->min_height = Paddle_MIN_HEIGHT;
    paddle->max_width = Paddle_MAX_WIDTH;
    paddle->min_width = Paddle_MIN_WIDTH;
    
    // Visual effect properties
    paddle->nudge_distance = 0;
    paddle->stabilize_speed = Paddle_STABILIZE_SPEED;
    paddle->max_nudge_distance = Paddle_MAX_NUDGE_DISTANCE;
    
    // Input state
    paddle->key_up_pressed = false;
    paddle->key_down_pressed = false;
    
    // Load textures
    paddle->topTexture = paddleTopTexture;
    paddle->middleTexture = paddleMiddleTexture;
    paddle->bottomTexture = paddleBottomTexture;
    
    // Set color
    paddle->color = owner->color;
    
    // Create shadow
    paddle->shadow = CreateShadow(paddle);
    
    // Initialize effect list
    paddle->effectList = CreateSpriteList();
    
    // Initialize AI properties
    paddle->is_ai = (owner->ai_difficulty > 0);
    paddle->decision_cooldown = 0.08f;
    paddle->last_decision_time = 0;
    paddle->target_y = 0;
    paddle->target_movement_buffer = 3.0f;
    paddle->missed_balls = 0;
    paddle->direction_change_cooldown = 0.1f;
    paddle->last_direction_change = 0;
    paddle->focused_item = NULL;
    paddle->min_distance = 99999;
    paddle->predicted_y = (Vector2){ 0, 0 };
    paddle->current_prediction = NULL;
    
    // Add to groups
    AddPaddleToGroup(paddle, owner->paddleGroup);
    AddPaddleToGroup(paddle, mainPaddleGroup);
    
    return paddle;
}
```

## Core Movement and Physics

```c
void UpdatePaddle(Paddle* paddle, GameClock* clock) {
    float delta = GetDeltaTime(clock);
    
    // Process AI if active
    if (paddle->is_ai) {
        UpdatePaddleAI(paddle, clock);
    }
    
    // Apply acceleration based on input
    if (paddle->key_up_pressed) {
        paddle->velocity_y -= paddle->acceleration * delta;
        if (paddle->velocity_y < -paddle->max_speed) {
            paddle->velocity_y = -paddle->max_speed;
        }
    } else if (paddle->key_down_pressed) {
        paddle->velocity_y += paddle->acceleration * delta;
        if (paddle->velocity_y > paddle->max_speed) {
            paddle->velocity_y = paddle->max_speed;
        }
    } else {
        // Apply retardation (slow down when not moving)
        if (paddle->velocity_y > 0) {
            paddle->velocity_y -= paddle->retardation * delta;
            if (paddle->velocity_y < 0) {
                paddle->velocity_y = 0;
            }
        } else if (paddle->velocity_y < 0) {
            paddle->velocity_y += paddle->retardation * delta;
            if (paddle->velocity_y > 0) {
                paddle->velocity_y = 0;
            }
        }
    }
    
    // Move paddle
    if (paddle->velocity_y != 0) {
        paddle->position.y += paddle->velocity_y * delta;
        
        // Clamp to level boundaries
        if (paddle->position.y < 0) {
            paddle->position.y = 0;
            paddle->velocity_y = 0;
        } else if (paddle->position.y + paddle->rect.height > LEVEL_HEIGHT) {
            paddle->position.y = LEVEL_HEIGHT - paddle->rect.height;
            paddle->velocity_y = 0;
        }
    }
    
    // Update visual nudge effect
    if (paddle->nudge_distance != 0) {
        if (paddle->nudge_distance > 0) {
            paddle->nudge_distance -= paddle->stabilize_speed * delta;
            if (paddle->nudge_distance < 0) {
                paddle->nudge_distance = 0;
            }
        } else {
            paddle->nudge_distance += paddle->stabilize_speed * delta;
            if (paddle->nudge_distance > 0) {
                paddle->nudge_distance = 0;
            }
        }
    }
    
    // Update rect position
    paddle->rect.x = paddle->position.x + paddle->nudge_distance;
    paddle->rect.y = paddle->position.y;
    
    // Update effects
    UpdateSpriteList(paddle->effectList, clock);
}
```

## Size Modification

```c
void SetPaddleHeight(Paddle* paddle, float height) {
    // Store original center
    float center_y = paddle->position.y + (paddle->rect.height / 2);
    
    // Update the actual height
    paddle->actual_height = height;
    
    // Clamp to min/max
    if (paddle->actual_height > paddle->max_height) {
        paddle->rect.height = paddle->max_height;
    } else if (paddle->actual_height < paddle->min_height) {
        paddle->rect.height = paddle->min_height;
    } else {
        paddle->rect.height = paddle->actual_height;
    }
    
    // Reposition to maintain center
    paddle->position.y = center_y - (paddle->rect.height / 2);
    
    // Clamp to level boundaries
    if (paddle->position.y < 0) {
        paddle->position.y = 0;
    } else if (paddle->position.y + paddle->rect.height > LEVEL_HEIGHT) {
        paddle->position.y = LEVEL_HEIGHT - paddle->rect.height;
    }
}

void SetPaddleWidth(Paddle* paddle, float width) {
    // Store original center
    float center_x = paddle->position.x + (paddle->rect.width / 2);
    
    // Update the actual width
    paddle->actual_width = width;
    
    // Clamp to min/max
    if (paddle->actual_width > paddle->max_width) {
        paddle->rect.width = paddle->max_width;
    } else if (paddle->actual_width < paddle->min_width) {
        paddle->rect.width = paddle->min_width;
    } else {
        paddle->rect.width = paddle->actual_width;
    }
    
    // Reposition to maintain center
    paddle->position.x = center_x - (paddle->rect.width / 2);
}
```

## Visual Effects

```c
void NudgePaddle(Paddle* paddle, float distance) {
    // Nudge paddle visually in x-direction
    paddle->nudge_distance = distance;
    
    // Clamp to max distance
    if (paddle->nudge_distance > paddle->max_nudge_distance) {
        paddle->nudge_distance = paddle->max_nudge_distance;
    } else if (paddle->nudge_distance < -paddle->max_nudge_distance) {
        paddle->nudge_distance = -paddle->max_nudge_distance;
    }
}

void AddHitEffect(Paddle* paddle) {
    // Create a flash effect on hit
    Color startColor = WHITE;
    startColor.a = 160;
    Color endColor = WHITE;
    endColor.a = 0;
    
    Flash* flash = CreateFlash(paddle, startColor, endColor, Paddle_HIT_EFFECT_TICKS);
    AddToSpriteList(paddle->effectList, flash);
}
```

## Drawing

```c
void DrawPaddle(Paddle* paddle) {
    // Calculate draw position
    Vector2 drawPos = GetWorldToScreen(paddle->position);
    
    // Draw shadow
    DrawShadow(paddle->shadow);
    
    // Draw segmented paddle
    // Top segment
    DrawTexture(paddle->topTexture, drawPos.x, drawPos.y, paddle->color);
    
    // Middle segments (repeat as needed)
    float middleY = drawPos.y + paddle->topTexture.height;
    float remainingHeight = paddle->rect.height - paddle->topTexture.height - paddle->bottomTexture.height;
    
    while (remainingHeight > 0) {
        float segmentHeight = fminf(paddle->middleTexture.height, remainingHeight);
        Rectangle srcRect = { 0, 0, paddle->middleTexture.width, segmentHeight };
        Rectangle destRect = { drawPos.x, middleY, paddle->middleTexture.width, segmentHeight };
        
        DrawTexturePro(paddle->middleTexture, srcRect, destRect, VECTOR2_ZERO, 0, paddle->color);
        
        middleY += segmentHeight;
        remainingHeight -= segmentHeight;
    }
    
    // Bottom segment
    DrawTexture(paddle->bottomTexture, drawPos.x, 
               drawPos.y + paddle->rect.height - paddle->bottomTexture.height, 
               paddle->color);
    
    // Draw effects
    DrawSpriteList(paddle->effectList);
    
    // Debug visualization
    if (IsDebugMode()) {
        DrawRectangleLines(
            drawPos.x, drawPos.y,
            paddle->rect.width, paddle->rect.height,
            RED
        );
        
        if (paddle->is_ai && paddle->target_y > 0) {
            // Draw AI target
            DrawCircleLines(
                drawPos.x + paddle->rect.width/2,
                paddle->target_y,
                5,
                YELLOW
            );
        }
    }
}
```

## AI System Implementation

```c
void UpdatePaddleAI(Paddle* paddle, GameClock* clock) {
    // Reset movement inputs
    paddle->key_up_pressed = false;
    paddle->key_down_pressed = false;
    
    // Determine which side of the screen the paddle is on
    bool paddle_side_left = (paddle->position.x < SCREEN_WIDTH / 2);
    
    // Get current time for decision making
    float current_time = GetTime();
    
    // Decide whether to recalculate AI decisions
    bool should_recalculate = (current_time - paddle->last_decision_time) >= paddle->decision_cooldown;
    
    // Always recalculate if no target yet
    if (paddle->target_y == 0) {
        should_recalculate = true;
    }
    
    // Recalculate more frequently if missing balls
    if (paddle->missed_balls > 0) {
        should_recalculate = should_recalculate || 
                            (current_time - paddle->last_decision_time) >= (paddle->decision_cooldown * 0.5f);
    }
    
    // Decide whether to use energy attack
    if (should_recalculate && GetRandomValue(0, 100) < 20) { // 20% chance
        if (DecideEnergyUsage(paddle)) {
            paddle->owner->attack();
        }
    }
    
    // Recalculate AI decisions
    if (should_recalculate) {
        paddle->last_decision_time = current_time;
        
        // Reset targeting variables
        void* old_focused_item = paddle->focused_item;
        void* old_prediction = paddle->current_prediction;
        
        paddle->focused_item = NULL;
        paddle->min_distance = 99999;
        paddle->predicted_y = (Vector2){ 0, 0 };
        paddle->current_prediction = NULL;
        
        // Find balls to target
        for (int i = 0; i < GetBallCount(); i++) {
            Ball* ball = GetBallAt(i);
            
            // Skip balls already heading away from this paddle
            if (ShouldSkipBall(paddle, ball, paddle_side_left)) {
                continue;
            }
            
            // Calculate trajectory and get intersection point
            Vector2 intersection = PredictBallTrajectory(ball, paddle);
            
            // If valid intersection found
            if (intersection.x != 0 && intersection.y != 0) {
                // Calculate distance to intersection
                float distance = fabsf(intersection.x - paddle->position.x);
                
                // Calculate priority (closer = higher priority)
                float priority = CalculatePriority(paddle, ball, distance);
                
                // Check if this is the best target
                if (priority < paddle->min_distance) {
                    paddle->min_distance = priority;
                    paddle->target_y = intersection.y;
                    paddle->focused_item = ball;
                    paddle->current_prediction = CreateTrajectoryPrediction(ball, intersection);
                }
            }
        }
        
        // If no balls to target, look for powerups
        if (paddle->focused_item == NULL) {
            FindPowerupTarget(paddle, paddle_side_left);
        }
        
        // If still no target, return to center position
        if (paddle->focused_item == NULL) {
            paddle->target_y = LEVEL_HEIGHT / 2 - paddle->rect.height / 2;
        }
    }
    
    // If we have a target, move toward it
    if (paddle->target_y > 0) {
        float paddle_center = paddle->position.y + paddle->rect.height / 2;
        float target_center = paddle->target_y + paddle->rect.height / 2;
        
        // Only move if outside of buffer zone
        if (fabsf(paddle_center - target_center) > paddle->target_movement_buffer) {
            // Check direction change cooldown
            float time_since_direction_change = current_time - paddle->last_direction_change;
            
            if (paddle_center < target_center) {
                // Need to move down
                if (paddle->velocity_y <= 0 && time_since_direction_change >= paddle->direction_change_cooldown) {
                    paddle->last_direction_change = current_time;
                }
                paddle->key_down_pressed = true;
            } else {
                // Need to move up
                if (paddle->velocity_y >= 0 && time_since_direction_change >= paddle->direction_change_cooldown) {
                    paddle->last_direction_change = current_time;
                }
                paddle->key_up_pressed = true;
            }
        }
    }
}
```

## AI Helper Functions

```c
bool ShouldSkipBall(Paddle* paddle, Ball* ball, bool paddle_side_left) {
    // Get ball movement direction
    float angle = ball->angle;
    bool ball_moving_right = (angle > PI * 1.5 || angle < PI * 0.5);
    
    // Skip if ball is moving away from paddle
    if ((paddle_side_left && ball_moving_right) || 
        (!paddle_side_left && !ball_moving_right)) {
        return false;
    }
    
    return true;
}

Vector2 PredictBallTrajectory(Ball* ball, Paddle* paddle) {
    // Create trajectory predictor
    TrajectoryPredictor* predictor = CreateTrajectoryPredictor(ball);
    
    // Get paddle side
    bool paddle_side_left = (paddle->position.x < SCREEN_WIDTH / 2);
    
    // Set target x position based on paddle side
    float target_x = paddle_side_left ? 
                    paddle->position.x + paddle->rect.width : 
                    paddle->position.x;
    
    // Predict ball path and find intersection with paddle x position
    Vector2 intersection = PredictIntersection(predictor, target_x);
    
    // Clean up
    DestroyTrajectoryPredictor(predictor);
    
    return intersection;
}

float CalculatePriority(Paddle* paddle, Ball* ball, float distance) {
    // Base priority is distance
    float priority = distance;
    
    // Adjust priority based on ball speed (faster balls get higher priority)
    priority -= (ball->speed / Ball_MAX_SPEED) * 100.0f;
    
    // Adjust priority based on ball ownership (own balls get lower priority)
    if (ball->owner == paddle->owner) {
        priority += 200.0f;
    }
    
    // Adjust priority for very slow balls (they're not urgent)
    if (ball->speed < Ball_BASE_SPEED * 0.7f) {
        priority += 150.0f;
    }
    
    return priority;
}

void FindPowerupTarget(Paddle* paddle, bool paddle_side_left) {
    for (int i = 0; i < GetPowerupCount(); i++) {
        Powerup* powerup = GetPowerupAt(i);
        
        // Only target powerups on same side of screen
        bool powerup_side_left = (powerup->position.x < SCREEN_WIDTH / 2);
        if (paddle_side_left != powerup_side_left) {
            continue;
        }
        
        // Calculate distance
        float distance = Vector2Distance(
            (Vector2){ paddle->position.x, paddle->position.y + paddle->rect.height/2 },
            (Vector2){ powerup->position.x, powerup->position.y }
        );
        
        // Check if this is the best target
        if (distance < paddle->min_distance) {
            paddle->min_distance = distance;
            paddle->target_y = powerup->position.y - paddle->rect.height/2;
            paddle->focused_item = powerup;
        }
    }
}

bool DecideEnergyUsage(Paddle* paddle) {
    // Check if enough energy available
    if (paddle->owner->energy < paddle->owner->attack_energy_cost) {
        return false;
    }
    
    // Base chance depends on difficulty
    float base_chance = 0.05f * paddle->owner->ai_difficulty;
    
    // Increase chance based on available energy percentage
    float energy_percentage = paddle->owner->energy / paddle->owner->max_energy;
    base_chance += energy_percentage * 0.3f;
    
    // Decision
    return GetRandomValue(0, 100) < (base_chance * 100);
}
```

## Ball Miss Detection

```c
void RegisterBallMiss(Paddle* paddle, Ball* ball) {
    // Only count if ball was heading toward this paddle
    bool paddle_side_left = (paddle->position.x < SCREEN_WIDTH / 2);
    bool ball_moving_right = (ball->angle > PI * 1.5 || ball->angle < PI * 0.5);
    
    if ((paddle_side_left && !ball_moving_right) || 
        (!paddle_side_left && ball_moving_right)) {
        // Increment missed balls counter
        paddle->missed_balls++;
        
        // Reset counter after a while
        if (paddle->missed_balls > 5) {
            paddle->missed_balls = 1;
        }
    }
}
```

## Constants

```c
// Basic properties
#define Paddle_WIDTH 10
#define Paddle_HEIGHT 22

// Speed values
#define Paddle_ACCELERATION (1.0f * GAME_FPS)
#define Paddle_RETARDATION (2.5f * GAME_FPS)
#define Paddle_MAX_SPEED (2.5f * GAME_FPS)

// Size limits
#define Paddle_MAX_HEIGHT 33
#define Paddle_MIN_HEIGHT 11
#define Paddle_MAX_WIDTH 10
#define Paddle_MIN_WIDTH 10

// Visual effects
#define Paddle_STABILIZE_SPEED (0.1f * GAME_FPS)
#define Paddle_MAX_NUDGE_DISTANCE 2.5f
#define Paddle_HIT_EFFECT_TICKS (22 * GAME_FPS)

// AI properties
#define Paddle_AI_DECISION_COOLDOWN 0.08f
#define Paddle_AI_DIRECTION_CHANGE_COOLDOWN 0.1f
#define Paddle_AI_TARGET_BUFFER 3.0f
```

## Memory Management

```c
void DestroyPaddle(Paddle* paddle) {
    // Remove from groups
    RemovePaddleFromGroup(paddle, paddle->owner->paddleGroup);
    RemovePaddleFromGroup(paddle, mainPaddleGroup);
    
    // Destroy effects
    for (int i = 0; i < paddle->effectList->count; i++) {
        Effect* effect = (Effect*)paddle->effectList->items[i];
        DestroyEffect(effect);
    }
    
    // Destroy effect list
    DestroySpriteList(paddle->effectList);
    
    // Destroy shadow
    DestroyShadow(paddle->shadow);
    
    // Free trajectory prediction if exists
    if (paddle->current_prediction != NULL) {
        DestroyTrajectoryPrediction(paddle->current_prediction);
    }
    
    // Free memory
    MemFree(paddle);
}
```

This specification details the paddle mechanics and AI system implementation for the C + Raylib port, based on the actual implementation in the Python version. It covers all aspects of paddle behavior, physics, visual effects, and AI decision making. 