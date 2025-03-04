#include "../include/screens.h"
#include "../include/entity.h"
#include "../include/paddle.h"
#include "../include/ball.h"
#include "../include/block.h"
#include <stdlib.h>
#include <stdio.h>

// Game constants
#define PLAYER_PADDLE_WIDTH 120
#define PLAYER_PADDLE_SPEED 400.0f
#define BLOCKS_ROWS 5
#define BLOCKS_COLUMNS 10
#define BLOCK_WIDTH 70
#define BLOCK_HEIGHT 30
#define BLOCK_PADDING 5
#define GAME_AREA_TOP 50
#define DEFAULT_LIVES 3

// Gameplay screen state
typedef struct GameplayState {
    EntityPool entityPool;      // Entity pool for all game objects
    EntityGroup paddleGroup;    // Group for paddle entities
    EntityGroup ballGroup;      // Group for ball entities
    EntityGroup blockGroup;     // Group for block entities
    
    Entity* playerPaddle;       // Player paddle reference
    Entity* mainBall;           // Main ball reference
    
    int score;                  // Current score
    int lives;                  // Remaining lives
    int blockCount;             // Number of blocks remaining
    
    bool gameOver;              // Whether game is over
    bool levelComplete;         // Whether level is complete
    bool paused;                // Whether game is paused
} GameplayState;

// Static game state
static GameplayState gameState;

// Function declarations
static void InitGameplay(void);
static void UpdateGameplay(float deltaTime);
static void DrawGameplay(void);
static void UnloadGameplay(void);
static GameScreen GetNextGameplayScreen(void);
static void ResetBall(void);
static void CreateBlocks(void);
static void CheckGameConditions(void);
static void HandleInput(float deltaTime);

// Initialize gameplay
static void InitGameplay(void) {
    // Initialize entity systems
    InitEntityPool(&gameState.entityPool);
    InitEntityGroup(&gameState.paddleGroup, 5);
    InitEntityGroup(&gameState.ballGroup, 10);
    InitEntityGroup(&gameState.blockGroup, BLOCKS_ROWS * BLOCKS_COLUMNS);
    
    // Initialize game state
    gameState.score = 0;
    gameState.lives = DEFAULT_LIVES;
    gameState.blockCount = 0;
    gameState.gameOver = false;
    gameState.levelComplete = false;
    gameState.paused = false;
    
    // Create player paddle at bottom of screen
    float paddleX = GetScreenWidth()/2 - PLAYER_PADDLE_WIDTH/2;
    float paddleY = GetScreenHeight() - 40;
    gameState.playerPaddle = CreatePaddle(1, paddleX, paddleY, PLAYER_PADDLE_WIDTH, 
                                         PLAYER_PADDLE_SPEED, BLUE);
    AddEntityToGroup(&gameState.paddleGroup, gameState.playerPaddle);
    
    // Create ball
    float ballX = paddleX + PLAYER_PADDLE_WIDTH/2;
    float ballY = paddleY - 15;
    gameState.mainBall = CreateBall(ballX, ballY, 10, 300, WHITE);
    AddEntityToGroup(&gameState.ballGroup, gameState.mainBall);
    
    // Stick ball to paddle initially
    StickBallToPaddle(gameState.mainBall, gameState.playerPaddle);
    
    // Create blocks
    CreateBlocks();
    
    printf("Gameplay screen initialized\n");
}

// Update gameplay logic
static void UpdateGameplay(float deltaTime) {
    // If game is over or level complete, wait for key press to continue
    if (gameState.gameOver || gameState.levelComplete) {
        if (IsKeyPressed(KEY_ENTER)) {
            ScreenGameplay.finishScreen = true;
        }
        return;
    }
    
    // Handle pause
    if (IsKeyPressed(KEY_P)) {
        gameState.paused = !gameState.paused;
    }
    
    // Skip updates if paused
    if (gameState.paused) return;
    
    // Handle player input
    HandleInput(deltaTime);
    
    // Update all entities
    UpdateEntityGroup(&gameState.paddleGroup, deltaTime);
    UpdateEntityGroup(&gameState.ballGroup, deltaTime);
    UpdateEntityGroup(&gameState.blockGroup, deltaTime);
    
    // Check for collisions
    CheckCollisionsInGroup(&gameState.ballGroup, &gameState.paddleGroup);
    CheckCollisionsInGroup(&gameState.ballGroup, &gameState.blockGroup);
    
    // Check if ball is out of bounds (bottom of screen)
    BallData* ballData = (BallData*)gameState.mainBall->data;
    if (ballData && !ballData->stuck) {
        if (ballData->position.y > GetScreenHeight()) {
            gameState.lives--;
            if (gameState.lives <= 0) {
                gameState.gameOver = true;
            } else {
                ResetBall();
            }
        }
    }
    
    // Check for game conditions
    CheckGameConditions();
}

// Draw gameplay elements
static void DrawGameplay(void) {
    // Draw background
    DrawRectangle(0, 0, GetScreenWidth(), GetScreenHeight(), BLACK);
    
    // Draw game area borders
    DrawRectangleLinesEx((Rectangle){0, GAME_AREA_TOP, GetScreenWidth(), GetScreenHeight() - GAME_AREA_TOP}, 
                        2, GRAY);
    
    // Draw all entities
    DrawEntityGroup(&gameState.blockGroup);
    DrawEntityGroup(&gameState.paddleGroup);
    DrawEntityGroup(&gameState.ballGroup);
    
    // Draw UI elements
    DrawText(TextFormat("SCORE: %d", gameState.score), 10, 10, 20, WHITE);
    DrawText(TextFormat("LIVES: %d", gameState.lives), GetScreenWidth() - 150, 10, 20, WHITE);
    
    // Draw additional messages based on game state
    if (gameState.paused) {
        DrawText("PAUSED", GetScreenWidth()/2 - 70, GetScreenHeight()/2, 40, WHITE);
        DrawText("Press P to resume", GetScreenWidth()/2 - 120, GetScreenHeight()/2 + 50, 20, GRAY);
    }
    
    if (gameState.gameOver) {
        DrawText("GAME OVER", GetScreenWidth()/2 - 100, GetScreenHeight()/2 - 40, 40, RED);
        DrawText(TextFormat("FINAL SCORE: %d", gameState.score), GetScreenWidth()/2 - 120, 
                GetScreenHeight()/2, 30, WHITE);
        DrawText("Press ENTER to return to menu", GetScreenWidth()/2 - 180, 
                GetScreenHeight()/2 + 50, 20, GRAY);
    }
    
    if (gameState.levelComplete) {
        DrawText("LEVEL COMPLETE!", GetScreenWidth()/2 - 150, GetScreenHeight()/2 - 40, 40, GREEN);
        DrawText(TextFormat("SCORE: %d", gameState.score), GetScreenWidth()/2 - 80, 
                GetScreenHeight()/2, 30, WHITE);
        DrawText("Press ENTER to continue", GetScreenWidth()/2 - 150, 
                GetScreenHeight()/2 + 50, 20, GRAY);
    }
    
    // Draw help text for new players
    if (!gameState.gameOver && !gameState.levelComplete && !gameState.paused) {
        BallData* ballData = (BallData*)gameState.mainBall->data;
        if (ballData && ballData->stuck) {
            DrawText("Press SPACE to launch the ball", GetScreenWidth()/2 - 180, 
                    GetScreenHeight() - 80, 20, LIGHTGRAY);
        }
    }
}

// Unload gameplay resources
static void UnloadGameplay(void) {
    // Clean up entity groups
    ClearEntityGroup(&gameState.paddleGroup);
    ClearEntityGroup(&gameState.ballGroup);
    ClearEntityGroup(&gameState.blockGroup);
    
    // Clean up entity pool
    ClearEntityPool(&gameState.entityPool);
    
    printf("Gameplay screen unloaded\n");
}

// Get next screen after gameplay
static GameScreen GetNextGameplayScreen(void) {
    if (gameState.gameOver) {
        return GAME_OVER;
    } else if (gameState.levelComplete) {
        // Normally would go to next level, but for now return to main menu
        return MAIN_MENU;
    }
    
    return MAIN_MENU;  // Default fallback
}

// Reset the ball position and attach to paddle
static void ResetBall(void) {
    if (!gameState.mainBall || !gameState.playerPaddle) return;
    
    // Reset ball position and state
    BallData* ballData = (BallData*)gameState.mainBall->data;
    if (ballData) {
        // Stick ball to paddle
        StickBallToPaddle(gameState.mainBall, gameState.playerPaddle);
    }
}

// Create the blocks for the level
static void CreateBlocks(void) {
    float startX = (GetScreenWidth() - (BLOCKS_COLUMNS * (BLOCK_WIDTH + BLOCK_PADDING))) / 2;
    float startY = GAME_AREA_TOP + 50;
    
    gameState.blockCount = 0;
    
    for (int row = 0; row < BLOCKS_ROWS; row++) {
        for (int col = 0; col < BLOCKS_COLUMNS; col++) {
            float x = startX + col * (BLOCK_WIDTH + BLOCK_PADDING);
            float y = startY + row * (BLOCK_HEIGHT + BLOCK_PADDING);
            
            // Determine block type and color based on row
            BlockType type = BLOCK_NORMAL;
            Color color = LIME;
            
            if (row == 0) {
                // Top row has some hard blocks
                if (col % 3 == 0) {
                    type = BLOCK_HARD;
                    color = ORANGE;
                }
            } else if (row == 1) {
                // Second row has some power-up blocks
                if (col % 5 == 0) {
                    type = BLOCK_POWERUP;
                    color = PURPLE;
                }
            } else if (row == 2) {
                // Middle row has different color
                color = YELLOW;
                
                // Add an explosive block in the middle
                if (col == BLOCKS_COLUMNS / 2) {
                    type = BLOCK_EXPLOSIVE;
                    color = RED;
                }
            } else if (row == BLOCKS_ROWS - 1) {
                // Bottom row has different color
                color = BLUE;
                
                // Add an invincible block on the edges
                if (col == 0 || col == BLOCKS_COLUMNS - 1) {
                    type = BLOCK_INVINCIBLE;
                    color = GRAY;
                }
            }
            
            // Create the block
            Entity* block = CreateBlock(x, y, BLOCK_WIDTH, BLOCK_HEIGHT, type, color);
            if (block) {
                AddEntityToGroup(&gameState.blockGroup, block);
                
                // Don't count invincible blocks towards total
                if (type != BLOCK_INVINCIBLE) {
                    gameState.blockCount++;
                }
            }
        }
    }
    
    printf("Created %d blocks\n", gameState.blockCount);
}

// Check game conditions (win/lose)
static void CheckGameConditions(void) {
    // Count active non-invincible blocks
    int activeBlocks = 0;
    for (int i = 0; i < gameState.blockGroup.count; i++) {
        Entity* block = gameState.blockGroup.entities[i];
        if (block && block->active) {
            BlockData* blockData = (BlockData*)block->data;
            if (blockData && blockData->type != BLOCK_INVINCIBLE) {
                activeBlocks++;
            }
        }
    }
    
    // Level complete if all breakable blocks are gone
    if (activeBlocks == 0) {
        gameState.levelComplete = true;
    }
}

// Handle input during gameplay
static void HandleInput(float deltaTime) {
    // Handle ball launch with spacebar
    BallData* ballData = (BallData*)gameState.mainBall->data;
    if (ballData && ballData->stuck && IsKeyPressed(KEY_SPACE)) {
        ReleaseBallFromPaddle(gameState.mainBall);
    }
}

// Screen initializer called by the screen management system
Screen InitGameplayScreen(void) {
    // No need for static Screen ScreenGameplay as we use the global one defined in screens.c
    
    // Create a local Screen structure and return it
    Screen screen = {
        .init = InitGameplay,
        .update = UpdateGameplay,
        .draw = DrawGameplay,
        .unload = UnloadGameplay,
        .getNextScreen = GetNextGameplayScreen,
        .finishScreen = false,
        .nextScreen = GAME_OVER
    };
    
    return screen;
} 