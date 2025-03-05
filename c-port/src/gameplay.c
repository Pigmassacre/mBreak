#include "screens.h"
#include "entity.h"
#include "paddle.h"
#include "ball.h"
#include "block.h"
#include "font.h"
#include <stdlib.h>
#include <stdio.h>
#include <math.h>

// Game constants
#define PADDLE_WIDTH 22
#define PADDLE_HEIGHT 33
#define PADDLE_SPEED 350.0f
#define BLOCKS_ROWS 7
#define BLOCKS_COLUMNS 3
#define BLOCK_WIDTH 32
#define BLOCK_HEIGHT 32
#define BLOCK_PADDING 0
#define GAME_AREA_TOP LEVEL_Y
#define GAME_AREA_BOTTOM LEVEL_MAX_Y
#define GAME_AREA_LEFT LEVEL_X
#define GAME_AREA_RIGHT LEVEL_MAX_X

// Gameplay screen state
typedef struct GameplayState {
    EntityPool entityPool;      // Entity pool for all game objects
    EntityGroup paddleGroup;    // Group for paddle entities
    EntityGroup ballGroup;      // Group for ball entities
    EntityGroup blockGroup;     // Group for block entities
    EntityGroup player1BlockGroup; // Group for player 1's blocks
    EntityGroup player2BlockGroup; // Group for player 2's blocks
    
    Entity* player1Paddle;      // Player 1 paddle reference
    Entity* player2Paddle;      // Player 2 paddle reference
    Entity* mainBall;           // Main ball reference
    
    int player1Score;           // Player 1 score
    int player2Score;           // Player 2 score
    int player1BlockCount;      // Number of player 1's blocks remaining
    int player2BlockCount;      // Number of player 2's blocks remaining
    
    bool gameOver;              // Whether game is over
    bool roundComplete;         // Whether round is complete
    bool paused;                // Whether game is paused
    int winner;                 // Winner of the round (1 or 2)
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
    InitEntityGroup(&gameState.blockGroup, BLOCKS_ROWS * BLOCKS_COLUMNS * 2);
    InitEntityGroup(&gameState.player1BlockGroup, BLOCKS_ROWS * BLOCKS_COLUMNS);
    InitEntityGroup(&gameState.player2BlockGroup, BLOCKS_ROWS * BLOCKS_COLUMNS);
    
    // Initialize game state
    gameState.player1Score = 0;
    gameState.player2Score = 0;
    gameState.player1BlockCount = 0;
    gameState.player2BlockCount = 0;
    gameState.gameOver = false;
    gameState.roundComplete = false;
    gameState.paused = false;
    gameState.winner = 0;
    
    // Create paddles for both players
    // Player 1 paddle on the left side
    float leftPaddleX = LEVEL_X + BLOCK_WIDTH * BLOCKS_COLUMNS + PADDLE_WIDTH * 3;
    float leftPaddleY = LEVEL_Y + (LEVEL_HEIGHT - PADDLE_HEIGHT) / 2.0f;
    gameState.player1Paddle = CreatePaddle(1, leftPaddleX, leftPaddleY, PADDLE_WIDTH, PADDLE_SPEED, BLUE);
    
    // Player 2 paddle on the right side
    float rightPaddleX = LEVEL_MAX_X - (BLOCK_WIDTH * BLOCKS_COLUMNS) - PADDLE_WIDTH * 4;
    float rightPaddleY = LEVEL_Y + (LEVEL_HEIGHT - PADDLE_HEIGHT) / 2.0f;
    gameState.player2Paddle = CreatePaddle(2, rightPaddleX, rightPaddleY, PADDLE_WIDTH, PADDLE_SPEED, RED);
    
    // Update paddle controls for vertical movement (overriding left/right keys)
    PaddleData* p1Data = (PaddleData*)gameState.player1Paddle->data;
    p1Data->upKey = KEY_W;
    p1Data->downKey = KEY_S;
    p1Data->moveVertical = true;
    
    PaddleData* p2Data = (PaddleData*)gameState.player2Paddle->data;
    p2Data->upKey = KEY_UP;
    p2Data->downKey = KEY_DOWN;
    p2Data->moveVertical = true;
    
    // Add paddles to group
    AddEntityToGroup(&gameState.paddleGroup, gameState.player1Paddle);
    AddEntityToGroup(&gameState.paddleGroup, gameState.player2Paddle);
    
    // Create the blocks
    CreateBlocks();
    
    // Create the initial ball
    ResetBall();
}

// Update gameplay logic
static void UpdateGameplay(float deltaTime) {
    // If game is over or round complete, wait for key press to continue
    if (gameState.gameOver || gameState.roundComplete) {
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
    
    // Check if ball is out of bounds (left or right side of game area)
    if (gameState.mainBall) {
        BallData* ballData = (BallData*)gameState.mainBall->data;
        if (ballData) {
            // Check left boundary
            if (ballData->position.x - ballData->radius < 0) {
                // Ball went out on the left side, player 2 scores
                gameState.player2Score++;
                gameState.winner = 2;
                gameState.roundComplete = true;
            }
            // Check right boundary
            else if (ballData->position.x + ballData->radius > LEVEL_WIDTH) {
                // Ball went out on the right side, player 1 scores
                gameState.player1Score++;
                gameState.winner = 1;
                gameState.roundComplete = true;
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
    DrawRectangleLinesEx((Rectangle){LEVEL_X, LEVEL_Y, LEVEL_WIDTH, LEVEL_HEIGHT}, 2, GRAY);
    
    // Draw all entities
    DrawEntityGroup(&gameState.blockGroup);
    DrawEntityGroup(&gameState.paddleGroup);
    DrawEntityGroup(&gameState.ballGroup);
    
    // Draw UI elements with custom font
    DrawTextEx(gameFont, TextFormat("PLAYER 1: %d", gameState.player1Score), (Vector2){10, 10}, 20, 1, BLUE);
    DrawTextEx(gameFont, TextFormat("PLAYER 2: %d", gameState.player2Score), (Vector2){GetScreenWidth() - 150, 10}, 20, 1, RED);
    
    // Draw additional messages based on game state
    if (gameState.paused) {
        DrawTextEx(gameFont, "PAUSED", (Vector2){GAME_WIDTH/2 - 50, GAME_HEIGHT/2}, 30, 1, WHITE);
        DrawTextEx(gameFont, "Press P to resume", (Vector2){GAME_WIDTH/2 - 120, GAME_HEIGHT/2 + 50}, 20, 1, GRAY);
    }
    
    if (gameState.gameOver) {
        DrawTextEx(gameFont, "GAME OVER", (Vector2){GAME_WIDTH/2 - 100, GAME_HEIGHT/2 - 40}, 40, 1, YELLOW);
        DrawTextEx(gameFont, TextFormat("PLAYER %d WINS!", gameState.winner), 
                (Vector2){GAME_WIDTH/2 - 120, GAME_HEIGHT/2}, 30, 1, (gameState.winner == 1) ? BLUE : RED);
        DrawTextEx(gameFont, "Press ENTER to return to menu", 
                (Vector2){GAME_WIDTH/2 - 180, GAME_HEIGHT/2 + 50}, 20, 1, GRAY);
    }
    
    if (gameState.roundComplete) {
        DrawTextEx(gameFont, "ROUND COMPLETE!", (Vector2){GAME_WIDTH/2 - 150, GAME_HEIGHT/2 - 40}, 40, 1, GREEN);
        DrawTextEx(gameFont, TextFormat("PLAYER %d WINS THIS ROUND", gameState.winner), 
                (Vector2){GAME_WIDTH/2 - 180, GAME_HEIGHT/2}, 30, 1, (gameState.winner == 1) ? BLUE : RED);
        DrawTextEx(gameFont, "Press ENTER to continue", 
                (Vector2){GAME_WIDTH/2 - 150, GAME_HEIGHT/2 + 50}, 20, 1, GRAY);
    }
}

// Unload gameplay resources
static void UnloadGameplay(void) {
    // Clean up entity groups
    ClearEntityGroup(&gameState.paddleGroup);
    ClearEntityGroup(&gameState.ballGroup);
    ClearEntityGroup(&gameState.blockGroup);
    ClearEntityGroup(&gameState.player1BlockGroup);
    ClearEntityGroup(&gameState.player2BlockGroup);
    
    // Clean up entity pool
    ClearEntityPool(&gameState.entityPool);
    
    printf("Gameplay screen unloaded\n");
}

// Get next screen after gameplay
static GameScreen GetNextGameplayScreen(void) {
    if (gameState.gameOver) {
        return GAME_OVER;
    } else if (gameState.roundComplete) {
        // Normally would go to next level or match over screen, but for now return to main menu
        return MAIN_MENU;
    }
    
    return MAIN_MENU;  // Default fallback
}

// Reset the ball to the center and give it a random direction
static void ResetBall(void) {
    // If a ball already exists, remove it
    if (gameState.mainBall) {
        RemoveEntityFromGroup(&gameState.ballGroup, gameState.mainBall);
        DestroyEntity(gameState.mainBall);
    }
    
    // Create a new ball in the center of the level
    float ballX = LEVEL_X + LEVEL_WIDTH / 2.0f;
    float ballY = LEVEL_Y + LEVEL_HEIGHT / 2.0f;
    gameState.mainBall = CreateBall(ballX, ballY, 8, 300, WHITE);
    AddEntityToGroup(&gameState.ballGroup, gameState.mainBall);
    
    // Randomly determine initial direction
    float initialAngle;
    if (GetRandomValue(0, 1) == 0) {
        // Right direction with small variation
        initialAngle = GetRandomValue(-15, 15) * DEG2RAD;
    } else {
        // Left direction with small variation
        initialAngle = PI + GetRandomValue(-15, 15) * DEG2RAD;
    }
    
    // Launch the ball in the initial direction
    LaunchBall(gameState.mainBall, initialAngle);
}

// Create the blocks for both players
static void CreateBlocks(void) {
    // Constants for block creation
    int strongRows = 1;
    int normalRows = 1;
    int weakRows = 1;
    int totalRows = BLOCKS_ROWS;
    
    gameState.player1BlockCount = 0;
    gameState.player2BlockCount = 0;
    
    // Colors for each player's blocks
    Color player1Color = BLUE;
    Color player2Color = RED;
    
    // Create blocks for player 1 (left side)
    for (int column = 0; column < BLOCKS_COLUMNS; column++) {
        // Strong blocks
        for (int row = 0; row < totalRows; row++) {
            BlockType blockType;
            
            // Determine block type based on position
            if (column < strongRows) {
                blockType = BLOCK_HARD;
            } else if (column < strongRows + normalRows) {
                blockType = BLOCK_NORMAL;
            } else {
                blockType = BLOCK_NORMAL; // Using normal instead of weak for now
            }
            
            float x = LEVEL_X + (BLOCK_WIDTH * column);
            float y = LEVEL_Y + (BLOCK_HEIGHT * row);
            
            Entity* block = CreateBlock(x, y, BLOCK_WIDTH, BLOCK_HEIGHT, blockType, player1Color);
            if (block) {
                AddEntityToGroup(&gameState.blockGroup, block);
                AddEntityToGroup(&gameState.player1BlockGroup, block);
                gameState.player1BlockCount++;
            }
        }
    }
    
    // Create blocks for player 2 (right side)
    for (int column = 0; column < BLOCKS_COLUMNS; column++) {
        for (int row = 0; row < totalRows; row++) {
            BlockType blockType;
            
            // Determine block type based on position
            if (column < strongRows) {
                blockType = BLOCK_HARD;
            } else if (column < strongRows + normalRows) {
                blockType = BLOCK_NORMAL;
            } else {
                blockType = BLOCK_NORMAL; // Using normal instead of weak for now
            }
            
            float x = LEVEL_MAX_X - (BLOCK_WIDTH * (column + 1));
            float y = LEVEL_Y + (BLOCK_HEIGHT * row);
            
            Entity* block = CreateBlock(x, y, BLOCK_WIDTH, BLOCK_HEIGHT, blockType, player2Color);
            if (block) {
                AddEntityToGroup(&gameState.blockGroup, block);
                AddEntityToGroup(&gameState.player2BlockGroup, block);
                gameState.player2BlockCount++;
                
                // Flip the block texture horizontally (will be implemented in draw function)
                BlockData* blockData = (BlockData*)block->data;
                if (blockData) {
                    blockData->flipped = true;
                }
            }
        }
    }
    
    printf("Created %d blocks for Player 1\n", gameState.player1BlockCount);
    printf("Created %d blocks for Player 2\n", gameState.player2BlockCount);
}

// Check for game conditions
static void CheckGameConditions(void) {
    // Update block counts
    gameState.player1BlockCount = gameState.player1BlockGroup.count;
    gameState.player2BlockCount = gameState.player2BlockGroup.count;
    
    // Check if any player's blocks are all destroyed
    if (gameState.player1BlockCount <= 0) {
        // Player 2 wins
        gameState.player2Score++;
        gameState.winner = 2;
        gameState.roundComplete = true;
    } else if (gameState.player2BlockCount <= 0) {
        // Player 1 wins
        gameState.player1Score++;
        gameState.winner = 1;
        gameState.roundComplete = true;
    }
}

// Handle player input
static void HandleInput(float deltaTime) {
    // Ball mechanics handled in ball.c
}

// Initialize the gameplay screen
Screen InitGameplayScreen(void) {
    Screen screen = {0};
    screen.init = InitGameplay;
    screen.update = UpdateGameplay;
    screen.draw = DrawGameplay;
    screen.unload = UnloadGameplay;
    screen.getNextScreen = GetNextGameplayScreen;
    screen.finishScreen = false;
    screen.nextScreen = GAME_OVER;
    
    return screen;
} 
