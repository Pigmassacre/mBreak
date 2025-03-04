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
    
    // Block targeting (for advanced AI)
    Block* target_block;     // Current block being targeted
    float block_target_score; // Score assigned to current block target
    int consecutive_hits;    // Count of consecutive successful hits
    
    // Strategy state
    AIStrategy current_strategy; // Current strategy being used
    float strategy_change_time; // Time when strategy was last changed
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
    paddle->target_block = NULL;
    paddle->block_target_score = 0;
    paddle->consecutive_hits = 0;
    paddle->current_strategy = STRATEGY_DEFENSIVE;
    paddle->strategy_change_time = 0;
    
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
        
        // At higher difficulties, adapt faster to missed balls
        if (paddle->owner->ai_difficulty > 2 && paddle->missed_balls > 2) {
            should_recalculate = true;
        }
    }
    
    // Decide whether to use energy attack
    if (should_recalculate) {
        // Base chance depends on difficulty
        int attack_chance = 5 + (paddle->owner->ai_difficulty * 5); // 5-20% chance based on difficulty
        
        if (GetRandomValue(0, 100) < attack_chance) {
            if (DecideEnergyUsage(paddle)) {
                paddle->owner->attack();
            }
        }
    }
    
    // Recalculate AI decisions
    if (should_recalculate) {
        paddle->last_decision_time = current_time;
        
        // Reset targeting variables
        void* old_focused_item = paddle->focused_item;
        void* old_prediction = paddle->current_prediction;
        Block* old_target_block = paddle->target_block;
        
        paddle->focused_item = NULL;
        paddle->min_distance = 99999;
        paddle->predicted_y = (Vector2){ 0, 0 };
        paddle->current_prediction = NULL;
        paddle->target_block = NULL;
        paddle->block_target_score = 0;
        
        // Difficulty-based strategy selection
        UpdateAIStrategy(paddle, current_time);
        
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
                    
                    // For higher difficulties, also look for block targeting opportunities
                    if (paddle->owner->ai_difficulty >= 2) {
                        FindTargetBlock(paddle, ball);
                    }
                }
            }
        }
        
        // If no balls to target, look for powerups
        if (paddle->focused_item == NULL) {
            FindPowerupTarget(paddle, paddle_side_left);
        }
        
        // If still no target, return to center position or strategic position
        if (paddle->focused_item == NULL) {
            if (paddle->owner->ai_difficulty <= 1) {
                // Basic AI just returns to center
                paddle->target_y = LEVEL_HEIGHT / 2 - paddle->rect.height / 2;
            } else {
                // Advanced AI picks strategic position based on game state
                paddle->target_y = ChooseStrategicPosition(paddle);
            }
        }
        
        // Clean up old prediction if it changed
        if (old_prediction != NULL && old_prediction != paddle->current_prediction) {
            DestroyTrajectoryPrediction(old_prediction);
        }
    }
    
    // If we have a target, move toward it
    if (paddle->target_y > 0) {
        float paddle_center = paddle->position.y + paddle->rect.height / 2;
        float target_center = paddle->target_y + paddle->rect.height / 2;
        
        // Adjust movement buffer based on difficulty (higher = more precise)
        float adjusted_buffer = paddle->target_movement_buffer;
        if (paddle->owner->ai_difficulty > 2) {
            adjusted_buffer *= 0.75f;
        }
        
        // Only move if outside of buffer zone
        if (fabsf(paddle_center - target_center) > adjusted_buffer) {
            // Check direction change cooldown
            float time_since_direction_change = current_time - paddle->last_direction_change;
            
            // Adjust direction change cooldown based on difficulty
            float adjusted_cooldown = paddle->direction_change_cooldown;
            if (paddle->owner->ai_difficulty > 2) {
                adjusted_cooldown *= 0.75f;
            } else if (paddle->owner->ai_difficulty == 1) {
                adjusted_cooldown *= 1.5f; // Less responsive at low difficulty
            }
            
            if (paddle_center < target_center) {
                // Need to move down
                if (paddle->velocity_y <= 0 && time_since_direction_change >= adjusted_cooldown) {
                    paddle->last_direction_change = current_time;
                }
                paddle->key_down_pressed = true;
            } else {
                // Need to move up
                if (paddle->velocity_y >= 0 && time_since_direction_change >= adjusted_cooldown) {
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
    
    // Always consider balls at higher difficulties
    if (paddle->owner->ai_difficulty >= 3) {
        return false;
    }
    
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
    
    // Set maximum bounce count based on AI difficulty
    int max_bounces = 1;  // Default for low difficulty
    if (paddle->owner->ai_difficulty >= 2) {
        max_bounces = 3;  // Medium difficulty
    } else if (paddle->owner->ai_difficulty >= 4) {
        max_bounces = 5;  // High difficulty
    }
    
    // Predict ball path and find intersection with paddle x position
    // This accounts for multiple bounces off walls, ceiling, and blocks
    Vector2 intersection = PredictIntersectionWithBounces(predictor, target_x, max_bounces);
    
    // Clean up
    DestroyTrajectoryPredictor(predictor);
    
    return intersection;
}

// Advanced trajectory prediction with multiple bounces
Vector2 PredictIntersectionWithBounces(TrajectoryPredictor* predictor, float target_x, int max_bounces) {
    // Start with ball's current position and velocity
    Vector2 position = predictor->ball->position;
    float angle = predictor->ball->angle;
    float speed = predictor->ball->speed;
    
    // Calculate velocity components
    float velocity_x = speed * cosf(angle);
    float velocity_y = speed * sinf(angle);
    
    // Track number of bounces
    int bounce_count = 0;
    
    // Maximum simulation steps
    const int MAX_STEPS = 1000;
    
    for (int i = 0; i < MAX_STEPS && bounce_count <= max_bounces; i++) {
        // Calculate time to reach target_x
        float time_to_target = 0;
        if (fabsf(velocity_x) > 0.1f) {
            time_to_target = (target_x - position.x) / velocity_x;
        }
        
        // If we'll reach the target_x with current velocity
        if (time_to_target > 0) {
            // Calculate y position at intersection
            float y_at_target = position.y + velocity_y * time_to_target;
            
            // Check if y position is within screen bounds
            if (y_at_target >= 0 && y_at_target <= LEVEL_HEIGHT) {
                return (Vector2){ target_x, y_at_target };
            }
        }
        
        // If no intersection found, continue simulating until next bounce
        // Calculate time to hit walls, ceiling, or floor
        float time_to_top = (velocity_y < 0) ? -position.y / velocity_y : INFINITY;
        float time_to_bottom = (velocity_y > 0) ? (LEVEL_HEIGHT - position.y) / velocity_y : INFINITY;
        float time_to_left = (velocity_x < 0) ? -position.x / velocity_x : INFINITY;
        float time_to_right = (velocity_x > 0) ? (LEVEL_WIDTH - position.x) / velocity_x : INFINITY;
        
        // Find next collision
        float time_to_collision = fminf(fminf(time_to_top, time_to_bottom), 
                                      fminf(time_to_left, time_to_right));
        
        // Check for collision with blocks
        BlockCollision block_collision = CheckBlockCollisions(predictor->ball, position, 
                                                           velocity_x, velocity_y);
        if (block_collision.will_collide && block_collision.time < time_to_collision) {
            time_to_collision = block_collision.time;
        }
        
        // Update position to collision point
        position.x += velocity_x * time_to_collision;
        position.y += velocity_y * time_to_collision;
        
        // Handle bounce physics
        if (time_to_collision == time_to_top || time_to_collision == time_to_bottom) {
            velocity_y = -velocity_y;
        } else if (time_to_collision == time_to_left || time_to_collision == time_to_right) {
            velocity_x = -velocity_x;
        } else if (block_collision.will_collide) {
            // Handle block collision based on collision normal
            if (block_collision.normal.x != 0) {
                velocity_x = -velocity_x;
            }
            if (block_collision.normal.y != 0) {
                velocity_y = -velocity_y;
            }
        }
        
        // Update angle from new velocity
        angle = atan2f(velocity_y, velocity_x);
        
        // Count bounce
        bounce_count++;
    }
    
    // If no solution found, return invalid point
    return (Vector2){ 0, 0 };
}

float CalculatePriority(Paddle* paddle, Ball* ball, float distance) {
    // Base priority is distance
    float priority = distance;
    
    // Adjust priority based on ball speed (faster balls get higher priority)
    priority -= (ball->speed / Ball_MAX_SPEED) * 100.0f;
    
    // Adjust priority based on ball ownership (own balls get lower priority at low difficulties)
    if (ball->owner == paddle->owner) {
        if (paddle->owner->ai_difficulty <= 2) {
            priority += 200.0f;
        } else {
            // Advanced AI is more strategic with owned balls
            // If we have a target block, give higher priority to owned balls
            if (paddle->target_block != NULL) {
                priority += 50.0f;
            } else {
                priority += 150.0f;
            }
        }
    }
    
    // Adjust priority for ball heading to opponent side (more valuable)
    bool paddle_side_left = (paddle->position.x < SCREEN_WIDTH / 2);
    bool ball_moving_right = (ball->angle > PI * 1.5 || ball->angle < PI * 0.5);
    
    if ((paddle_side_left && ball_moving_right) || (!paddle_side_left && !ball_moving_right)) {
        if (paddle->owner->ai_difficulty >= 3) {
            priority -= 75.0f; // Advanced AI values offensive opportunities
        }
    }
    
    // Adjust priority for very slow balls (they're not urgent)
    if (ball->speed < Ball_BASE_SPEED * 0.7f) {
        priority += 150.0f;
    }
    
    return priority;
}

// Find a strategic block to target
void FindTargetBlock(Paddle* paddle, Ball* ball) {
    // Only used by medium and high difficulty AI
    if (paddle->owner->ai_difficulty < 2) {
        return;
    }
    
    // Create block scoring system
    BlockScorer* scorer = CreateBlockScorer();
    
    // Score each block based on current strategy
    for (int i = 0; i < GetBlockCount(); i++) {
        Block* block = GetBlockAt(i);
        
        // Skip dead blocks
        if (block->health <= 0) {
            continue;
        }
        
        // Calculate base score
        float score = CalculateBlockScore(paddle, block, ball);
        
        // Apply strategy modifiers
        ApplyStrategyToBlockScore(paddle, block, &score);
        
        // Check if this is the best target
        if (score > paddle->block_target_score) {
            paddle->block_target_score = score;
            paddle->target_block = block;
        }
    }
    
    // If we found a target block, adjust trajectory prediction
    if (paddle->target_block != NULL && paddle->current_prediction != NULL) {
        AdjustTrajectoryForBlock(paddle, ball, paddle->target_block);
    }
    
    // Clean up
    DestroyBlockScorer(scorer);
}

// Calculate desirability score for a block
float CalculateBlockScore(Paddle* paddle, Block* block, Ball* ball) {
    // Base score starts with block value
    float score = block->value;
    
    // Reward special blocks more
    if (block->has_powerup) {
        score *= 1.5f;
    }
    
    // Add bonus for low health blocks (easier to destroy)
    score += (block->max_health - block->health) * 5.0f;
    
    // Reduce score based on distance from ball
    float distance = Vector2Distance(ball->position, block->position);
    score -= distance * 0.01f;
    
    // Apply difficulty multipliers
    if (paddle->owner->ai_difficulty >= 4) {
        // Expert AI values strategic blocks more
        if (block->row < 3) {
            score *= 1.3f; // Top rows are valuable
        }
    }
    
    return score;
}

// Adjust trajectory to try to hit target block
void AdjustTrajectoryForBlock(Paddle* paddle, Ball* ball, Block* target_block) {
    // Only advanced AI can do this
    if (paddle->owner->ai_difficulty < 3) {
        return;
    }
    
    // Calculate ideal angle to hit block
    Vector2 ball_pos = ball->position;
    Vector2 block_pos = target_block->position;
    Vector2 paddle_pos = paddle->position;
    
    // Calculate vector from paddle to ball
    Vector2 paddle_to_ball = {
        ball_pos.x - paddle_pos.x,
        ball_pos.y - (paddle_pos.y + paddle->rect.height/2)
    };
    
    // Calculate vector from ball to block
    Vector2 ball_to_block = {
        block_pos.x - ball_pos.x,
        block_pos.y - ball_pos.y
    };
    
    // Normalize vectors
    float paddle_to_ball_length = sqrtf(paddle_to_ball.x*paddle_to_ball.x + paddle_to_ball.y*paddle_to_ball.y);
    float ball_to_block_length = sqrtf(ball_to_block.x*ball_to_block.x + ball_to_block.y*ball_to_block.y);
    
    if (paddle_to_ball_length > 0 && ball_to_block_length > 0) {
        paddle_to_ball.x /= paddle_to_ball_length;
        paddle_to_ball.y /= paddle_to_ball_length;
        ball_to_block.x /= ball_to_block_length;
        ball_to_block.y /= ball_to_block_length;
        
        // Calculate ideal paddle position to achieve this angle
        float ideal_offset = CalculateIdealPaddleOffset(paddle, ball, paddle_to_ball, ball_to_block);
        
        // Adjust target_y based on ideal offset
        paddle->target_y = ball_pos.y - (paddle->rect.height/2) + ideal_offset;
        
        // Clamp to screen boundaries
        if (paddle->target_y < 0) {
            paddle->target_y = 0;
        } else if (paddle->target_y + paddle->rect.height > LEVEL_HEIGHT) {
            paddle->target_y = LEVEL_HEIGHT - paddle->rect.height;
        }
    }
}

// Calculate ideal paddle position to hit ball at specific angle
float CalculateIdealPaddleOffset(Paddle* paddle, Ball* ball, Vector2 paddle_to_ball, Vector2 ball_to_block) {
    // Calculate dot product to determine ideal offset
    float dot_product = paddle_to_ball.x * ball_to_block.x + paddle_to_ball.y * ball_to_block.y;
    
    // Convert to angle measure
    float angle = acosf(Clamp(dot_product, -1.0f, 1.0f));
    
    // Map angle to paddle offset
    float paddle_half_height = paddle->rect.height / 2.0f;
    float offset = (angle / PI) * paddle_half_height * 1.2f; // 1.2 multiplier for fine-tuning
    
    // Adjust sign based on relative positions
    if (ball->position.y < paddle->position.y + paddle_half_height) {
        offset = -offset;
    }
    
    return offset;
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
        
        // Adjust distance based on powerup type and AI difficulty
        if (paddle->owner->ai_difficulty >= 2) {
            // Advanced AI considers powerup value
            float value_modifier = GetPowerupValueForAI(powerup);
            distance /= value_modifier;
        }
        
        // Check if this is the best target
        if (distance < paddle->min_distance) {
            paddle->min_distance = distance;
            paddle->target_y = powerup->position.y - paddle->rect.height/2;
            paddle->focused_item = powerup;
        }
    }
}

float GetPowerupValueForAI(Powerup* powerup) {
    // Different powerups have different value to AI
    switch (powerup->type) {
        case POWERUP_EXTRA_LIFE:
            return 3.0f;
        case POWERUP_ENLARGE_PADDLE:
            return 2.5f;
        case POWERUP_SHRINK_OPPONENT:
            return 2.2f;
        case POWERUP_BALL_SPEED_UP:
            return 1.8f;
        case POWERUP_BALL_SPEED_DOWN:
            return 1.5f;
        case POWERUP_EXTRA_BALL:
            return 2.0f;
        case POWERUP_ENERGY:
            return 2.0f;
        default:
            return 1.0f;
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
    
    // Strategic considerations
    if (paddle->owner->ai_difficulty >= 3) {
        // Advanced AI makes better energy decisions
        
        // Higher chance when opponent has few lives
        Player* opponent = GetOpponent(paddle->owner);
        if (opponent->lives <= 2) {
            base_chance += 0.15f;
        }
        
        // Higher chance when there are many balls on screen
        if (GetBallCount() >= 3) {
            base_chance += 0.1f;
        }
        
        // Lower chance if energy is low and no immediate advantage
        if (energy_percentage < 0.3f && opponent->lives > 2) {
            base_chance -= 0.15f;
        }
    }
    
    // Decision (0-1 scale)
    return GetRandomValue(0, 100) < (base_chance * 100);
}

// Update AI strategy based on game state
void UpdateAIStrategy(Paddle* paddle, float current_time) {
    // Only used by higher difficulty AIs
    if (paddle->owner->ai_difficulty < 2) {
        return;
    }
    
    // Check if it's time to reconsider strategy
    float strategy_duration = 5.0f;  // Every 5 seconds
    if (current_time - paddle->strategy_change_time < strategy_duration) {
        return;
    }
    
    // Analyze game state
    Player* opponent = GetOpponent(paddle->owner);
    int ball_count = GetBallCount();
    int own_balls = CountOwnedBalls(paddle->owner);
    int block_count = GetBlockCount();
    
    // Strategy weights
    float offensive_weight = 1.0f;
    float defensive_weight = 1.0f;
    float powerup_weight = 1.0f;
    
    // Adjust weights based on game state
    
    // Defensive focus if losing
    if (paddle->owner->lives < opponent->lives) {
        defensive_weight += 0.5f;
    }
    
    // Offensive focus if winning
    if (paddle->owner->lives > opponent->lives) {
        offensive_weight += 0.3f;
    }
    
    // Powerup focus if low on energy
    if (paddle->owner->energy < paddle->owner->max_energy * 0.3f) {
        powerup_weight += 0.4f;
    }
    
    // More defensive if opponent has energy for attack
    if (opponent->energy >= opponent->attack_energy_cost) {
        defensive_weight += 0.3f;
    }
    
    // More offensive if we have majority of balls
    if (own_balls > ball_count / 2) {
        offensive_weight += 0.4f;
    }
    
    // Choose strategy based on weights
    AIStrategy new_strategy;
    float total_weight = offensive_weight + defensive_weight + powerup_weight;
    float random_value = GetRandomValue(0, 100) / 100.0f * total_weight;
    
    if (random_value < offensive_weight) {
        new_strategy = STRATEGY_OFFENSIVE;
    } else if (random_value < offensive_weight + defensive_weight) {
        new_strategy = STRATEGY_DEFENSIVE;
    } else {
        new_strategy = STRATEGY_POWERUP_FOCUS;
    }
    
    // Apply new strategy
    paddle->current_strategy = new_strategy;
    paddle->strategy_change_time = current_time;
}

// Choose strategic position when no immediate target
float ChooseStrategicPosition(Paddle* paddle) {
    switch (paddle->current_strategy) {
        case STRATEGY_OFFENSIVE:
            // Position to attack opponent
            return (LEVEL_HEIGHT / 2) - (paddle->rect.height / 2) + 
                   GetRandomValue(-20, 20); // Slight randomization
            
        case STRATEGY_DEFENSIVE:
            // Position near center but with slight bias toward screen edges
            return (LEVEL_HEIGHT / 2) - (paddle->rect.height / 2) + 
                   (GetRandomValue(0, 1) ? 30 : -30);
            
        case STRATEGY_POWERUP_FOCUS:
            // Position to catch falling powerups - scan for closest block with powerup
            Block* powerup_block = FindClosestPowerupBlock(paddle);
            if (powerup_block != NULL) {
                return powerup_block->position.y - (paddle->rect.height / 2);
            }
            // Fallback to center
            return (LEVEL_HEIGHT / 2) - (paddle->rect.height / 2);
            
        default:
            // Default to center
            return (LEVEL_HEIGHT / 2) - (paddle->rect.height / 2);
    }
}

// Apply current strategy to block scoring
void ApplyStrategyToBlockScore(Paddle* paddle, Block* block, float* score) {
    switch (paddle->current_strategy) {
        case STRATEGY_OFFENSIVE:
            // Prefer blocks that open paths to opponent
            if (block->row < 3) {
                *score *= 1.3f;
            }
            // Prefer blocks that will drop powerups
            if (block->has_powerup) {
                *score *= 1.2f;
            }
            break;
            
        case STRATEGY_DEFENSIVE:
            // Prefer blocks away from our side
            bool paddle_side_left = (paddle->position.x < SCREEN_WIDTH / 2);
            if ((paddle_side_left && block->position.x > LEVEL_WIDTH / 2) ||
                (!paddle_side_left && block->position.x < LEVEL_WIDTH / 2)) {
                *score *= 1.25f;
            }
            break;
            
        case STRATEGY_POWERUP_FOCUS:
            // Heavily prefer blocks with powerups
            if (block->has_powerup) {
                *score *= 2.0f;
            }
            break;
    }
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
        
        // Performance based difficulty adjustment for advanced AI
        if (paddle->owner->ai_difficulty >= 3) {
            if (paddle->missed_balls > 2) {
                // Temporarily increase decision rate
                paddle->decision_cooldown *= 0.8f;
            }
        }
    }
}
```

## AI Strategy Enum

```c
typedef enum {
    STRATEGY_DEFENSIVE,
    STRATEGY_OFFENSIVE,
    STRATEGY_POWERUP_FOCUS
} AIStrategy;
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

// AI difficulty levels
#define AI_DIFFICULTY_EASY 1
#define AI_DIFFICULTY_MEDIUM 2
#define AI_DIFFICULTY_HARD 3
#define AI_DIFFICULTY_EXPERT 4
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

This specification details the paddle mechanics and AI system implementation for the C + Raylib port, based on the actual implementation in the Python version. It covers all aspects of paddle behavior, physics, visual effects, and AI decision making, including the sophisticated strategy and block targeting systems. 
This specification details the paddle mechanics and AI system implementation for the C + Raylib port, based on the actual implementation in the Python version. It covers all aspects of paddle behavior, physics, visual effects, and AI decision making. 