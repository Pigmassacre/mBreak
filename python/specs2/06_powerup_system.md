# Power-up System

This document details the power-up system for the mBreak game, based on the current implementation in `objects/powerups/` directory.

## Power-up Types

```c
typedef enum PowerupType {
    POWERUP_NONE,
    POWERUP_MULTIBALL,
    POWERUP_FIRE,
    POWERUP_FROST,
    POWERUP_GRAVITY,
    POWERUP_ROCKET,
    POWERUP_ENLARGER,
    POWERUP_REDUCER,
    POWERUP_SPEEDBOOST,
    POWERUP_ELECTRICITY,
    POWERUP_COUNT  // Used to get the total number of powerup types
} PowerupType;
```

## Power-up Entity Structure

```c
typedef struct Powerup {
    // Core properties
    Vector2 position;        // Float precision position
    Rectangle rect;          // Collision rectangle
    PowerupType type;        // Type of powerup
    
    // Visual properties
    Texture2D texture;       // Powerup texture
    Color color;             // Tint color
    float rotation;          // Current rotation angle
    float rotation_speed;    // Speed of rotation
    float scale;             // Size scale (1.0 = normal)
    Shadow* shadow;          // Shadow effect
    
    // Bob effect properties
    float center_y;          // Original Y position for bob effect
    float bob_factor;        // How noticeable the bob effect should be
    
    // Particle effects
    float particle_spawn_rate;  // How often particles spawn
    int particle_spawn_amount;  // How many particles spawn at once
    
    // Movement properties
    Vector2 velocity;        // Current movement velocity
    float gravity;           // Gravity effect on powerup
    
    // Lifetime properties
    float lifetime;          // How long the powerup has existed
    float max_lifetime;      // Maximum lifetime before disappearing
    float fade_start;        // When to start fading out
    float alpha;             // Current transparency
    
    // State
    bool is_hit;             // Whether powerup has been hit
    bool is_destroyed;       // Whether powerup is marked for destruction
    bool is_display;         // Whether this is a display-only powerup
} Powerup;
```

## Initialization

```c
Powerup* CreatePowerup(float x, float y, PowerupType type) {
    Powerup* powerup = (Powerup*)MemAlloc(sizeof(Powerup));
    
    // Set position
    powerup->position.x = x;
    powerup->position.y = y;
    
    // Set center_y for bob effect
    powerup->center_y = y;
    
    // Create rect
    powerup->rect = (Rectangle){ 
        x - POWERUP_WIDTH/2, 
        y - POWERUP_HEIGHT/2, 
        POWERUP_WIDTH, 
        POWERUP_HEIGHT 
    };
    
    // Set type
    powerup->type = type;
    
    // Set texture based on type
    powerup->texture = GetPowerupTexture(type);
    
    // Set color based on type
    powerup->color = GetPowerupColor(type);
    
    // Set visual properties
    powerup->rotation = 0.0f;
    powerup->rotation_speed = GetRandomValue(50, 150) / 100.0f; // 0.5 to 1.5
    if (GetRandomValue(0, 1)) {
        powerup->rotation_speed *= -1; // Randomly reverse direction
    }
    powerup->scale = 1.0f;
    powerup->bob_factor = POWERUP_BOB_FACTOR;
    
    // Set particle properties based on type
    SetPowerupParticleProperties(powerup);
    
    // Set movement properties
    powerup->velocity = (Vector2){ 0, 0 };
    powerup->gravity = POWERUP_GRAVITY;
    
    // Set lifetime properties
    powerup->lifetime = 0.0f;
    powerup->max_lifetime = POWERUP_MAX_LIFETIME;
    powerup->fade_start = POWERUP_FADE_START;
    powerup->alpha = 1.0f;
    
    // Set state
    powerup->is_hit = false;
    powerup->is_destroyed = false;
    powerup->is_display = false;
    
    // Create shadow
    powerup->shadow = CreateShadow(powerup);
    
    // Add to main powerup group
    AddPowerupToGroup(powerup, mainPowerupGroup);
    
    return powerup;
}

void SpawnPowerup(float x, float y, PowerupType type) {
    // If type is POWERUP_NONE, randomly select a type
    if (type == POWERUP_NONE) {
        type = GetRandomPowerupType();
    }
    
    // Create the powerup
    Powerup* powerup = CreatePowerup(x, y, type);
    
    // Add initial velocity for more dynamic movement
    powerup->velocity.x = GetRandomValue(-100, 100) / 100.0f * POWERUP_INITIAL_VELOCITY;
    powerup->velocity.y = GetRandomValue(-150, -50) / 100.0f * POWERUP_INITIAL_VELOCITY;
    
    // Play spawn sound
    PlaySound(powerupSpawnSound);
}

PowerupType GetRandomPowerupType() {
    // Get a random powerup type (excluding POWERUP_NONE)
    return (PowerupType)GetRandomValue(1, POWERUP_COUNT - 1);
}

Color GetPowerupColor(PowerupType type) {
    // Return appropriate color based on powerup type
    switch (type) {
        case POWERUP_MULTIBALL:
            return SKYBLUE;
        case POWERUP_FIRE:
            return RED;
        case POWERUP_FROST:
            return BLUE;
        case POWERUP_GRAVITY:
            return PURPLE;
        case POWERUP_ROCKET:
            return YELLOW;
        case POWERUP_ENLARGER:
            return GREEN;
        case POWERUP_REDUCER:
            return PINK;
        case POWERUP_SPEEDBOOST:
            return BROWN;
        case POWERUP_ELECTRICITY:
            return ORANGE;
        default:
            return WHITE;
    }
}
```

## Update and Physics

```c
void UpdatePowerup(Powerup* powerup, GameClock* clock) {
    float delta = GetDeltaTime(clock);
    
    // Skip if destroyed
    if (powerup->is_destroyed) {
        return;
    }
    
    // Update lifetime
    powerup->lifetime += delta;
    
    // Check if powerup should be destroyed due to lifetime
    if (powerup->lifetime >= powerup->max_lifetime) {
        DestroyPowerup(powerup);
        return;
    }
    
    // Update alpha for fade out
    if (powerup->lifetime >= powerup->fade_start) {
        float fadeProgress = (powerup->lifetime - powerup->fade_start) / 
                            (powerup->max_lifetime - powerup->fade_start);
        powerup->alpha = 1.0f - fadeProgress;
        
        // Blink effect near end of lifetime
        if (powerup->lifetime >= powerup->max_lifetime - 1.0f) {
            if (fmodf(powerup->lifetime * 10, 2) < 1) {
                powerup->alpha = 0.0f;
            }
        }
    }
    
    // Apply bob effect
    if (!powerup->is_display) {
        powerup->position.y = powerup->center_y + sinf(powerup->lifetime * 2) * powerup->bob_factor;
    }
    
    // Update rotation
    powerup->rotation += powerup->rotation_speed * delta * 60.0f;
    
    // Apply gravity if not a display powerup
    if (!powerup->is_display) {
        powerup->velocity.y += powerup->gravity * delta;
    }
    
    // Update position
    powerup->position.x += powerup->velocity.x * delta;
    powerup->position.y += powerup->velocity.y * delta;
    
    // Update particle effects
    UpdatePowerupParticles(powerup, delta);
    
    // Bounce off walls
    if (powerup->position.x - POWERUP_WIDTH/2 < 0) {
        powerup->position.x = POWERUP_WIDTH/2;
        powerup->velocity.x = -powerup->velocity.x * POWERUP_BOUNCE_DAMPING;
    } else if (powerup->position.x + POWERUP_WIDTH/2 > LEVEL_WIDTH) {
        powerup->position.x = LEVEL_WIDTH - POWERUP_WIDTH/2;
        powerup->velocity.x = -powerup->velocity.x * POWERUP_BOUNCE_DAMPING;
    }
    
    // Bounce off top
    if (powerup->position.y - POWERUP_HEIGHT/2 < 0) {
        powerup->position.y = POWERUP_HEIGHT/2;
        powerup->velocity.y = -powerup->velocity.y * POWERUP_BOUNCE_DAMPING;
    }
    
    // Check if powerup fell off bottom of screen
    if (powerup->position.y - POWERUP_HEIGHT/2 > LEVEL_HEIGHT) {
        DestroyPowerup(powerup);
        return;
    }
    
    // Update rect position
    powerup->rect.x = powerup->position.x - POWERUP_WIDTH/2;
    powerup->rect.y = powerup->position.y - POWERUP_HEIGHT/2;
    
    // Update shadow
    UpdateShadow(powerup->shadow);
}
```

## Collision and Activation

```c
bool CheckPowerupPaddleCollision(Powerup* powerup, Paddle* paddle) {
    // Skip if already hit or destroyed
    if (powerup->is_hit || powerup->is_destroyed) {
        return false;
    }
    
    // Check for collision
    if (CheckCollisionRecs(powerup->rect, paddle->rect)) {
        // Mark as hit
        powerup->is_hit = true;
        
        // Apply powerup effect
        ActivatePowerup(powerup, paddle->owner);
        
        // Play hit sound
        PlaySound(powerupHitSound);
        
        // Destroy powerup
        DestroyPowerup(powerup);
        
        return true;
    }
    
    return false;
}

void ActivatePowerup(Powerup* powerup, Player* player) {
    // Apply effect based on powerup type
    switch (powerup->type) {
        case POWERUP_MULTIBALL:
            ActivateMultiball(player);
            break;
        case POWERUP_FIRE:
            ActivateFire(player);
            break;
        case POWERUP_FROST:
            ActivateFrost(player);
            break;
        case POWERUP_GRAVITY:
            ActivateGravity(player);
            break;
        case POWERUP_ROCKET:
            ActivateRocket(player);
            break;
        case POWERUP_ENLARGER:
            ActivateEnlarger(player);
            break;
        case POWERUP_REDUCER:
            ActivateReducer(player);
            break;
        case POWERUP_SPEEDBOOST:
            ActivateSpeedboost(player);
            break;
        case POWERUP_ELECTRICITY:
            ActivateElectricity(player);
            break;
        default:
            break;
    }
}
```

## Power-up Effect Implementations

### Multiball

```c
void ActivateMultiball(Player* player) {
    // Get all balls owned by this player
    int ballCount = GetPlayerBallCount(player);
    
    // Create a list to store original balls
    Ball* originalBalls[MAX_BALLS];
    int originalBallCount = 0;
    
    // Collect original balls
    for (int i = 0; i < ballCount; i++) {
        Ball* ball = GetPlayerBallAt(player, i);
        if (ball != NULL) {
            originalBalls[originalBallCount++] = ball;
        }
    }
    
    // For each original ball, create a new ball
    for (int i = 0; i < originalBallCount; i++) {
        Ball* originalBall = originalBalls[i];
        
        // Create new ball at same position
        Ball* newBall = CreateBall(
            originalBall->position.x,
            originalBall->position.y,
            player
        );
        
        // Set angle to be slightly different from original
        float newAngle = originalBall->angle + PI/6;
        SetBallAngle(newBall, newAngle);
        
        // Copy speed from original
        newBall->speed = originalBall->speed;
        
        // Copy effects from original
        CopyBallEffects(originalBall, newBall);
        
        // Add timeout effect to new ball
        Timeout* timeout = CreateTimeoutEffect(newBall, MULTIBALL_DURATION);
        AddToSpriteList(newBall->effectList, timeout);
    }
    
    // Award points
    AddPlayerPoints(player, MULTIBALL_POINTS);
}

void CopyBallEffects(Ball* source, Ball* target) {
    // Copy all effects except Charged
    for (int i = 0; i < source->effectList->count; i++) {
        Effect* effect = (Effect*)source->effectList->items[i];
        
        // Skip Charged effect
        if (IsEffectType(effect, "Charged")) {
            continue;
        }
        
        // Clone the effect
        Effect* clonedEffect = CloneEffect(effect, target);
        if (clonedEffect != NULL) {
            AddToSpriteList(target->effectList, clonedEffect);
        }
    }
}

void ActivateFire(Player* player) {
    // Get all balls owned by this player
    int ballCount = GetPlayerBallCount(player);
    
    // Apply fire effect to each ball
    for (int i = 0; i < ballCount; i++) {
        Ball* ball = GetPlayerBallAt(player, i);
        if (ball != NULL) {
            // Add burning effect to ball
            Burning* burning = CreateBurningEffect(ball, FIRE_DURATION);
            AddToSpriteList(ball->effectList, burning);
            
            // Set ball as burning
            ball->is_burning = true;
            ball->burn_source = player;
        }
    }
    
    // Award points
    AddPlayerPoints(player, FIRE_POINTS);
}

void ActivateFrost(Player* player) {
    // Get opponent player
    Player* opponent = GetOpponentPlayer(player);
    
    // Get all balls owned by opponent
    int ballCount = GetPlayerBallCount(opponent);
    
    // Apply frost effect to each opponent ball
    for (int i = 0; i < ballCount; i++) {
        Ball* ball = GetPlayerBallAt(opponent, i);
        if (ball != NULL) {
            // Add freezing effect to ball
            Freezing* freezing = CreateFreezingEffect(ball, FROST_DURATION);
            AddToSpriteList(ball->effectList, freezing);
            
            // Set ball as frozen
            ball->is_frozen = true;
            
            // Slow down ball
            ball->speed *= FROST_SPEED_MULTIPLIER;
        }
    }
    
    // Get all blocks
    int blockCount = GetBlockCount();
    
    // Apply frost effect to blocks on opponent's side
    bool opponent_side_left = (opponent->side == PLAYER_SIDE_LEFT);
    
    for (int i = 0; i < blockCount; i++) {
        Block* block = GetBlockAt(i);
        
        // Skip destroyed blocks
        if (block->is_destroyed) {
            continue;
        }
        
        // Check if block is on opponent's side
        bool block_side_left = (block->position.x < LEVEL_WIDTH / 2);
        
        if (block_side_left == opponent_side_left) {
            // Set block as frozen
            SetBlockFrozen(block, true);
        }
    }
    
    // Award points
    AddPlayerPoints(player, FROST_POINTS);
}

void ActivateGravity(Player* player) {
    // Create gravitational pull effect at center of player's side
    float x = (player->side == PLAYER_SIDE_LEFT) ? 
              LEVEL_WIDTH * 0.25f : 
              LEVEL_WIDTH * 0.75f;
    float y = LEVEL_HEIGHT * 0.5f;
    
    // Create the effect
    GravitationalPull* gravity = CreateGravitationalPullEffect(
        x, y, GRAVITY_RADIUS, GRAVITY_STRENGTH, GRAVITY_DURATION
    );
    
    // Set owner
    gravity->owner = player;
    
    // Add to global effects list
    AddToGlobalEffectsList(gravity);
    
    // Award points
    AddPlayerPoints(player, GRAVITY_POINTS);
}

void ActivateRocket(Player* player) {
    // Get player's paddle
    Paddle* paddle = GetPlayerPaddle(player);
    
    // Create rocket effect
    Rocket* rocket = CreateRocketEffect(paddle, ROCKET_DURATION);
    
    // Add to paddle's effect list
    AddToSpriteList(paddle->effectList, rocket);
    
    // Award points
    AddPlayerPoints(player, ROCKET_POINTS);
}

void ActivateEnlarger(Player* player) {
    // Get player's paddle
    Paddle* paddle = GetPlayerPaddle(player);
    
    // Calculate new height
    float newHeight = paddle->actual_height * ENLARGER_MULTIPLIER;
    
    // Set paddle height
    SetPaddleHeight(paddle, newHeight);
    
    // Create size change effect
    SizeChange* sizeChange = CreateSizeChangeEffect(
        paddle, paddle->actual_height, newHeight, ENLARGER_DURATION
    );
    
    // Add to paddle's effect list
    AddToSpriteList(paddle->effectList, sizeChange);
    
    // Award points
    AddPlayerPoints(player, ENLARGER_POINTS);
}

void ActivateReducer(Player* player) {
    // Get opponent player
    Player* opponent = GetOpponentPlayer(player);
    
    // Get opponent's paddle
    Paddle* paddle = GetPlayerPaddle(opponent);
    
    // Calculate new height
    float newHeight = paddle->actual_height * REDUCER_MULTIPLIER;
    
    // Set paddle height
    SetPaddleHeight(paddle, newHeight);
    
    // Create size change effect
    SizeChange* sizeChange = CreateSizeChangeEffect(
        paddle, paddle->actual_height, newHeight, REDUCER_DURATION
    );
    
    // Add to paddle's effect list
    AddToSpriteList(paddle->effectList, sizeChange);
    
    // Award points
    AddPlayerPoints(player, REDUCER_POINTS);
}

void ActivateSpeedboost(Player* player) {
    // Get all balls owned by this player
    int ballCount = GetPlayerBallCount(player);
    
    // Apply speedboost effect to each ball
    for (int i = 0; i < ballCount; i++) {
        Ball* ball = GetPlayerBallAt(player, i);
        if (ball != NULL) {
            // Store original speed
            float originalSpeed = ball->speed;
            
            // Speed up ball
            ball->speed *= SPEEDBOOST_MULTIPLIER;
            
            // Create speed effect
            Speed* speed = CreateSpeedEffect(
                ball, originalSpeed, ball->speed, SPEEDBOOST_DURATION
            );
            
            // Add to ball's effect list
            AddToSpriteList(ball->effectList, speed);
        }
    }
    
    // Award points
    AddPlayerPoints(player, SPEEDBOOST_POINTS);
}

void ActivateElectricity(Player* player) {
    // Get all balls owned by this player
    int ballCount = GetPlayerBallCount(player);
    
    // Apply charged effect to each ball
    for (int i = 0; i < ballCount; i++) {
        Ball* ball = GetPlayerBallAt(player, i);
        if (ball != NULL) {
            // Add charged effect to ball
            Charged* charged = CreateChargedEffect(ball, ELECTRICITY_DURATION);
            AddToSpriteList(ball->effectList, charged);
            
            // Set ball as charged
            ball->is_charged = true;
            ball->charge_damage = ELECTRICITY_DAMAGE_MULTIPLIER;
        }
    }
    
    // Award points
    AddPlayerPoints(player, ELECTRICITY_POINTS);
}
```

## Drawing

```c
void DrawPowerup(Powerup* powerup) {
    // Skip if destroyed
    if (powerup->is_destroyed) {
        return;
    }
    
    // Calculate draw position
    Vector2 drawPos = GetWorldToScreen(powerup->position);
    
    // Draw shadow
    DrawShadow(powerup->shadow);
    
    // Draw particles
    DrawPowerupParticles(powerup);
    
    // Calculate color with alpha
    Color drawColor = powerup->color;
    drawColor.a = (unsigned char)(255 * powerup->alpha);
    
    // Draw powerup with rotation
    if (powerup->rotation != 0.0f) {
        // Calculate center for rotation
        Vector2 origin = { 
            powerup->texture.width / 2.0f, 
            powerup->texture.height / 2.0f 
        };
        
        // Calculate destination rectangle
        Rectangle destRect = {
            drawPos.x,
            drawPos.y,
            powerup->texture.width * powerup->scale,
            powerup->texture.height * powerup->scale
        };
        
        // Draw texture with rotation
        DrawTexturePro(
            powerup->texture,
            (Rectangle){ 0, 0, powerup->texture.width, powerup->texture.height },
            destRect,
            origin,
            powerup->rotation,
            drawColor
        );
    } else {
        // Simple draw without rotation
        DrawTexture(
            powerup->texture, 
            drawPos.x - powerup->texture.width * powerup->scale / 2, 
            drawPos.y - powerup->texture.height * powerup->scale / 2, 
            drawColor
        );
    }
    
    // Debug visualization
    if (IsDebugMode()) {
        DrawRectangleLines(
            drawPos.x - POWERUP_WIDTH/2, 
            drawPos.y - POWERUP_HEIGHT/2,
            POWERUP_WIDTH, 
            POWERUP_HEIGHT,
            RED
        );
    }
}
```

## Constants

```c
// Powerup dimensions
#define POWERUP_WIDTH 8.0f
#define POWERUP_HEIGHT 8.0f

// Physics
#define POWERUP_GRAVITY 9.8f
#define POWERUP_INITIAL_VELOCITY 2.0f
#define POWERUP_BOUNCE_DAMPING 0.7f
#define POWERUP_BOB_FACTOR 0.5f

// Lifetime
#define POWERUP_MAX_LIFETIME 10.0f
#define POWERUP_FADE_START 7.0f

// Points awarded
#define MULTIBALL_POINTS 50
#define FIRE_POINTS 50
#define FROST_POINTS 50
#define GRAVITY_POINTS 50
#define ROCKET_POINTS 50
#define ENLARGER_POINTS 50
#define REDUCER_POINTS 50
#define SPEEDBOOST_POINTS 50
#define ELECTRICITY_POINTS 50

// Effect durations
#define MULTIBALL_DURATION 15.0f
#define FIRE_DURATION 10.0f
#define FROST_DURATION 5.0f
#define GRAVITY_DURATION 8.0f
#define ROCKET_DURATION 5.0f
#define ENLARGER_DURATION 10.0f
#define REDUCER_DURATION 10.0f
#define SPEEDBOOST_DURATION 7.0f
#define ELECTRICITY_DURATION 12.0f

// Effect strengths
#define FROST_SPEED_MULTIPLIER 0.5f
#define GRAVITY_RADIUS 150.0f
#define GRAVITY_STRENGTH 50.0f
#define ENLARGER_MULTIPLIER 1.5f
#define REDUCER_MULTIPLIER 0.7f
#define SPEEDBOOST_MULTIPLIER 1.4f
#define ELECTRICITY_DAMAGE_MULTIPLIER 2.0f
```

## Memory Management

```c
void DestroyPowerup(Powerup* powerup) {
    // Mark as destroyed
    powerup->is_destroyed = true;
    
    // Remove from powerup group
    RemovePowerupFromGroup(powerup, mainPowerupGroup);
    
    // Play sound if needed
    if (!powerup->is_hit) {
        PlaySound(powerupDestroySound);
    }
    
    // Destroy shadow
    DestroyShadow(powerup->shadow);
    
    // Free memory
    MemFree(powerup);
}
```

This specification details the power-up system implementation for the C + Raylib port, based on the actual implementation in the Python version. It covers all aspects of power-up behavior, physics, visual effects, and the various power-up types and their effects. 