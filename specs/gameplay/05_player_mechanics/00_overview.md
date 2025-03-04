# Player Mechanics Overview

## System Components

### Core Player Class
```c
typedef struct Player {
    // Identity
    int id;
    Color color;
    char* name;
    
    // Game state
    float energy;
    int score;
    bool isAI;
    
    // Groups
    PaddleGroup* paddles;
    BallGroup* balls;
    BlockGroup* blocks;
    PowerupGroup* powerups;
    EffectGroup* effects;
    
    // Input state
    InputState input;
    
    // Display
    Rectangle displayArea;
    PowerupDisplay* powerupDisplay;
} Player;
```

### Input System
```c
typedef struct InputState {
    // Keyboard state
    bool keyUp;
    bool keyDown;
    bool keyAction;
    bool keySpecial;
    
    // Gamepad state
    float axisVertical;
    bool buttonAction;
    bool buttonSpecial;
    
    // Input configuration
    InputConfig config;
} InputState;
```

### Energy System
```c
typedef struct EnergySystem {
    float currentEnergy;
    float maxEnergy;
    float rechargeRate;
    float consumptionRate;
    
    // Multipliers
    float gainMultiplier;
    float consumeMultiplier;
    
    // Thresholds
    float specialThreshold;
    float superThreshold;
} EnergySystem;
```

### Score System
```c
typedef struct ScoreSystem {
    int currentScore;
    int matchScore;
    int highScore;
    
    // Multipliers
    float comboMultiplier;
    int comboCounter;
    
    // Statistics
    int blocksDestroyed;
    int powerupsCollected;
    int specialsUsed;
} ScoreSystem;
```

## Core Mechanics

### Player Initialization
```c
Player* InitPlayer(int id, Color color, bool isAI) {
    Player* player = MemAlloc(sizeof(Player));
    
    // Initialize base properties
    player->id = id;
    player->color = color;
    player->isAI = isAI;
    
    // Initialize systems
    InitializeGroups(player);
    InitializeEnergy(player);
    InitializeInput(player);
    InitializeDisplay(player);
    
    return player;
}
```

### Input Processing
```c
void ProcessPlayerInput(Player* player) {
    if (player->isAI) {
        ProcessAIInput(player);
        return;
    }
    
    // Process keyboard input
    player->input.keyUp = IsKeyDown(player->input.config.keyUp);
    player->input.keyDown = IsKeyDown(player->input.config.keyDown);
    player->input.keyAction = IsKeyPressed(player->input.config.keyAction);
    
    // Process gamepad input if available
    if (IsGamepadAvailable(player->id)) {
        player->input.axisVertical = GetGamepadAxisMovement(player->id, GAMEPAD_AXIS_LEFT_Y);
        player->input.buttonAction = IsGamepadButtonPressed(player->id, player->input.config.padAction);
    }
}
```

### Energy Management
```c
void UpdatePlayerEnergy(Player* player, float deltaTime) {
    // Natural recharge
    player->energy = Clamp(
        player->energy + (player->energySystem.rechargeRate * deltaTime),
        0.0f,
        player->energySystem.maxEnergy
    );
    
    // Process energy consumption
    if (player->input.keySpecial && player->energy >= player->energySystem.specialThreshold) {
        ConsumeEnergy(player, player->energySystem.specialThreshold);
        ActivateSpecialAbility(player);
    }
}
```

### Score Management
```c
void UpdatePlayerScore(Player* player, int points, bool isComboPossible) {
    if (isComboPossible) {
        player->scoreSystem.comboCounter++;
        player->scoreSystem.comboMultiplier = MIN(3.0f, 1.0f + (player->scoreSystem.comboCounter * 0.5f));
    } else {
        player->scoreSystem.comboCounter = 0;
        player->scoreSystem.comboMultiplier = 1.0f;
    }
    
    int finalPoints = (int)(points * player->scoreSystem.comboMultiplier);
    player->scoreSystem.currentScore += finalPoints;
}
```

## Group Management

### Entity Groups
```c
void InitializeGroups(Player* player) {
    // Initialize sprite groups
    player->paddles = CreatePaddleGroup();
    player->balls = CreateBallGroup();
    player->blocks = CreateBlockGroup();
    player->powerups = CreatePowerupGroup();
    player->effects = CreateEffectGroup();
}
```

### Group Updates
```c
void UpdatePlayerGroups(Player* player, float deltaTime) {
    // Update all entity groups
    UpdatePaddleGroup(player->paddles, deltaTime);
    UpdateBallGroup(player->balls, deltaTime);
    UpdateBlockGroup(player->blocks, deltaTime);
    UpdatePowerupGroup(player->powerups, deltaTime);
    UpdateEffectGroup(player->effects, deltaTime);
}
```

## Display System

### Power-up Display
```c
typedef struct PowerupDisplay {
    Vector2 position;
    Rectangle bounds;
    PowerupIcon* icons;
    int iconCount;
    float scale;
} PowerupDisplay;

void UpdatePowerupDisplay(Player* player) {
    // Update power-up icon positions
    for (int i = 0; i < player->powerupDisplay->iconCount; i++) {
        UpdateIconPosition(&player->powerupDisplay->icons[i]);
        UpdateIconDuration(&player->powerupDisplay->icons[i]);
    }
}
```

### Score Display
```c
void DrawPlayerScore(Player* player) {
    char scoreText[32];
    sprintf(scoreText, "Score: %d", player->scoreSystem.currentScore);
    
    Vector2 position = GetScorePosition(player);
    DrawText(scoreText, position.x, position.y, 20, player->color);
}
```

## Event System

### Event Handling
```c
void HandlePlayerEvent(Player* player, GameEvent event) {
    switch (event.type) {
        case EVENT_BLOCK_DESTROYED:
            HandleBlockDestroyed(player, event.data);
            break;
        case EVENT_POWERUP_COLLECTED:
            HandlePowerupCollected(player, event.data);
            break;
        case EVENT_PADDLE_HIT:
            HandlePaddleHit(player, event.data);
            break;
    }
}
```

### Event Callbacks
```c
void HandleBlockDestroyed(Player* player, EventData data) {
    player->scoreSystem.blocksDestroyed++;
    UpdatePlayerScore(player, data.points, data.isCombo);
    
    if (player->scoreSystem.blocksDestroyed % 10 == 0) {
        TriggerAchievement(player, ACHIEVEMENT_BLOCK_DESTROYER);
    }
}
```

## Memory Management

### Resource Handling
```c
void CleanupPlayer(Player* player) {
    // Cleanup groups
    CleanupPaddleGroup(player->paddles);
    CleanupBallGroup(player->balls);
    CleanupBlockGroup(player->blocks);
    CleanupPowerupGroup(player->powerups);
    CleanupEffectGroup(player->effects);
    
    // Cleanup display
    CleanupPowerupDisplay(player->powerupDisplay);
    
    // Free player memory
    MemFree(player);
}
```

## Debug Features

### State Visualization
```c
void DrawPlayerDebug(Player* player) {
    if (!IsDebugMode()) return;
    
    // Draw energy bar
    DrawEnergyBar(player);
    
    // Draw input state
    DrawInputState(player);
    
    // Draw group counts
    DrawGroupCounts(player);
}
``` 