# Level System

## Overview

The level system in mBreak is responsible for creating, loading, and managing gameplay levels. Each level consists of block arrangements, player paddles, and various game elements. This specification details how levels are implemented in the Python codebase and provides guidelines for implementing the level system in the C/Raylib port.

## Current Implementation (Python + Pygame)

### Core Components

#### Level Module

The primary level module (`screens/level.py`) handles:
- Level creation and initialization
- Block placement and arrangement
- Paddle placement and setup
- Game boundary setup
- Level difficulty scaling

#### Level Integration

The level system integrates with:
- Game screen for rendering and updates
- Block system for creating various block types
- Paddle system for player controls
- Camera system for viewport management

### Implementation Details

#### Level Creation

The level creation process involves:
- Setting up the playing field dimensions
- Creating blocks with specific arrangements
- Placing player paddles at appropriate positions
- Establishing game boundaries

```python
# Example level creation (simplified)
def create_level(window_surface, player_one, player_two):
    # Create blocks
    block_group = pygame.sprite.Group()
    for y in range(BLOCK_ROWS):
        for x in range(BLOCK_COLUMNS):
            block_position = (x * (BLOCK_WIDTH + BLOCK_SPACING), y * (BLOCK_HEIGHT + BLOCK_SPACING))
            block = Block(block_position)
            block_group.add(block)
    
    # Setup player paddles
    paddle_one = Paddle(player_one, PADDLE_ONE_POSITION)
    paddle_two = Paddle(player_two, PADDLE_TWO_POSITION)
    
    return block_group, paddle_one, paddle_two
```

#### Level Difficulty

The game adjusts level difficulty by:
- Changing block types and distributions
- Modifying block health/durability
- Adjusting powerup spawn rates
- Changing level layout complexity

## Port Implementation (C + Raylib)

### Core Level Structs

```c
// Block arrangement types
typedef enum BlockArrangementType {
    BLOCK_ARRANGEMENT_GRID,
    BLOCK_ARRANGEMENT_DIAGONAL,
    BLOCK_ARRANGEMENT_CIRCULAR,
    BLOCK_ARRANGEMENT_RANDOM
} BlockArrangementType;

// Level configuration
typedef struct LevelConfig {
    int width;                      // Level width
    int height;                     // Level height
    int blockRows;                  // Number of block rows
    int blockColumns;               // Number of block columns
    float blockSpacing;             // Spacing between blocks
    BlockArrangementType arrangement; // Block arrangement pattern
    float normalBlockChance;        // Chance for normal blocks
    float strongBlockChance;        // Chance for strong blocks
    float weakBlockChance;          // Chance for weak blocks
    float powerupSpawnChance;       // Chance for powerup to spawn when block is destroyed
    int difficultyLevel;            // Level difficulty (1-10)
} LevelConfig;

// Level structure
typedef struct Level {
    LevelConfig config;             // Level configuration
    Rectangle bounds;               // Level boundaries
    Block** blocks;                 // Array of block pointers
    int blockCount;                 // Number of blocks
    int blockCapacity;              // Maximum block capacity
    Paddle playerOnePaddle;         // Player one paddle
    Paddle playerTwoPaddle;         // Player two paddle
    Vector2 playerOneStartPos;      // Player one starting position
    Vector2 playerTwoStartPos;      // Player two starting position
    Ball** balls;                   // Array of ball pointers
    int ballCount;                  // Number of balls
    int ballCapacity;               // Maximum ball capacity
    bool initialized;               // Whether the level is fully initialized
} Level;
```

### Level Management System

```c
// Initialize the level system
Level* InitLevel(const LevelConfig* config);

// Free level resources
void FreeLevel(Level* level);

// Create blocks for level based on arrangement type
void CreateLevelBlocks(Level* level);

// Create specific block arrangement patterns
void CreateGridBlockArrangement(Level* level);
void CreateDiagonalBlockArrangement(Level* level);
void CreateCircularBlockArrangement(Level* level);
void CreateRandomBlockArrangement(Level* level);

// Setup player paddles
void SetupLevelPaddles(Level* level, Player* playerOne, Player* playerTwo);

// Reset level (for new rounds)
void ResetLevel(Level* level);

// Update and draw level
void UpdateLevel(Level* level, float deltaTime);
void DrawLevel(Level* level);

// Level difficulty configuration
LevelConfig GetDifficultyConfig(int difficultyLevel);
```

### Level Creation and Setup

```c
Level* CreateGameLevel(int difficultyLevel, Player* playerOne, Player* playerTwo) {
    // Get difficulty-based configuration
    LevelConfig config = GetDifficultyConfig(difficultyLevel);
    
    // Initialize level
    Level* level = InitLevel(&config);
    
    // Create blocks based on arrangement type
    CreateLevelBlocks(level);
    
    // Setup player paddles
    SetupLevelPaddles(level, playerOne, playerTwo);
    
    // Initialize starting ball
    Ball* initialBall = CreateBall(
        (Vector2){ level->bounds.width / 2, level->bounds.height / 2 },
        (Vector2){ GetRandomValue(-100, 100) / 100.0f, GetRandomValue(-100, 100) / 100.0f },
        BALL_DEFAULT_SPEED
    );
    AddBallToLevel(level, initialBall);
    
    return level;
}
```

### Block Arrangement Implementations

```c
void CreateGridBlockArrangement(Level* level) {
    float blockWidth = level->config.width / level->config.blockColumns;
    float blockHeight = 30.0f; // Default block height
    
    // Calculate actual usable width with spacing
    float totalBlockWidth = blockWidth - level->config.blockSpacing;
    
    for (int row = 0; row < level->config.blockRows; row++) {
        for (int col = 0; col < level->config.blockColumns; col++) {
            // Calculate position
            float x = col * blockWidth + level->config.blockSpacing / 2;
            float y = row * (blockHeight + level->config.blockSpacing) + level->config.blockSpacing;
            
            // Determine block type based on probability
            float random = GetRandomValue(0, 100) / 100.0f;
            BlockType type;
            
            if (random < level->config.weakBlockChance) {
                type = BLOCK_WEAK;
            } else if (random < level->config.weakBlockChance + level->config.strongBlockChance) {
                type = BLOCK_STRONG;
            } else {
                type = BLOCK_NORMAL;
            }
            
            // Create block
            Block* block = CreateBlock(
                (Vector2){ x, y },
                (Vector2){ totalBlockWidth, blockHeight },
                type
            );
            
            // Add to level
            AddBlockToLevel(level, block);
        }
    }
}
```

### Diagonal Block Arrangement

```c
void CreateDiagonalBlockArrangement(Level* level) {
    float blockWidth = level->config.width / level->config.blockColumns;
    float blockHeight = 30.0f;
    float totalBlockWidth = blockWidth - level->config.blockSpacing;
    
    int maxDiagonalLength = level->config.blockRows < level->config.blockColumns ? 
                            level->config.blockRows : level->config.blockColumns;
    
    for (int diagonal = 0; diagonal < maxDiagonalLength * 2; diagonal++) {
        for (int i = 0; i <= diagonal; i++) {
            int row = i;
            int col = diagonal - i;
            
            if (row < level->config.blockRows && col < level->config.blockColumns) {
                // Calculate position
                float x = col * blockWidth + level->config.blockSpacing / 2;
                float y = row * (blockHeight + level->config.blockSpacing) + level->config.blockSpacing;
                
                // Determine block type
                BlockType type = BLOCK_NORMAL;
                if ((row + col) % 3 == 0) type = BLOCK_STRONG;
                if ((row + col) % 5 == 0) type = BLOCK_WEAK;
                
                // Create block
                Block* block = CreateBlock(
                    (Vector2){ x, y },
                    (Vector2){ totalBlockWidth, blockHeight },
                    type
                );
                
                // Add to level
                AddBlockToLevel(level, block);
            }
        }
    }
}
```

### Circular Block Arrangement

```c
void CreateCircularBlockArrangement(Level* level) {
    float blockWidth = 60.0f;
    float blockHeight = 30.0f;
    
    // Calculate center of the level
    float centerX = level->config.width / 2;
    float centerY = level->config.height / 3; // Top third
    
    int rings = 4; // Number of concentric rings
    int blocksPerRing = 8; // Base number of blocks in innermost ring
    
    for (int ring = 0; ring < rings; ring++) {
        float radius = (ring + 1) * blockWidth * 1.2f;
        int numBlocks = blocksPerRing + (ring * 4); // More blocks in outer rings
        
        for (int i = 0; i < numBlocks; i++) {
            float angle = (2 * PI * i) / numBlocks;
            float x = centerX + cosf(angle) * radius - blockWidth / 2;
            float y = centerY + sinf(angle) * radius - blockHeight / 2;
            
            // Alternate block types in rings
            BlockType type;
            if (ring % 3 == 0) type = BLOCK_NORMAL;
            else if (ring % 3 == 1) type = BLOCK_STRONG;
            else type = BLOCK_WEAK;
            
            // Create block
            Block* block = CreateBlock(
                (Vector2){ x, y },
                (Vector2){ blockWidth, blockHeight },
                type
            );
            
            // Add to level
            AddBlockToLevel(level, block);
        }
    }
}
```

### Level Difficulty Configuration

```c
LevelConfig GetDifficultyConfig(int difficultyLevel) {
    LevelConfig config;
    
    // Base configuration
    config.width = LEVEL_WIDTH;
    config.height = LEVEL_HEIGHT;
    config.blockSpacing = 5.0f;
    config.arrangement = BLOCK_ARRANGEMENT_GRID;
    config.difficultyLevel = difficultyLevel;
    
    // Adjust based on difficulty level
    switch (difficultyLevel) {
        case 1: // Easiest
            config.blockRows = 3;
            config.blockColumns = 8;
            config.normalBlockChance = 0.8f;
            config.strongBlockChance = 0.1f;
            config.weakBlockChance = 0.1f;
            config.powerupSpawnChance = 0.3f;
            break;
            
        case 2:
            config.blockRows = 4;
            config.blockColumns = 9;
            config.normalBlockChance = 0.7f;
            config.strongBlockChance = 0.2f;
            config.weakBlockChance = 0.1f;
            config.powerupSpawnChance = 0.25f;
            break;
            
        // ... other difficulty levels
            
        case 10: // Hardest
            config.blockRows = 8;
            config.blockColumns = 12;
            config.normalBlockChance = 0.4f;
            config.strongBlockChance = 0.5f;
            config.weakBlockChance = 0.1f;
            config.powerupSpawnChance = 0.1f;
            config.arrangement = BLOCK_ARRANGEMENT_RANDOM;
            break;
            
        default: // Medium difficulty
            config.blockRows = 5;
            config.blockColumns = 10;
            config.normalBlockChance = 0.6f;
            config.strongBlockChance = 0.3f;
            config.weakBlockChance = 0.1f;
            config.powerupSpawnChance = 0.2f;
            break;
    }
    
    return config;
}
```

## Level Management

### Adding and Removing Blocks

```c
void AddBlockToLevel(Level* level, Block* block) {
    // Check if we need to expand capacity
    if (level->blockCount >= level->blockCapacity) {
        level->blockCapacity *= 2;
        level->blocks = (Block**)realloc(level->blocks, 
                                        level->blockCapacity * sizeof(Block*));
    }
    
    // Add block to array
    level->blocks[level->blockCount++] = block;
}

void RemoveBlockFromLevel(Level* level, int blockIndex) {
    if (blockIndex >= 0 && blockIndex < level->blockCount) {
        // Free block resources
        FreeBlock(level->blocks[blockIndex]);
        
        // Shift remaining blocks
        for (int i = blockIndex; i < level->blockCount - 1; i++) {
            level->blocks[i] = level->blocks[i + 1];
        }
        
        level->blockCount--;
    }
}
```

### Level Update Logic

```c
void UpdateLevel(Level* level, float deltaTime) {
    // Update all blocks
    for (int i = 0; i < level->blockCount; i++) {
        UpdateBlock(level->blocks[i], deltaTime);
        
        // Check if block is destroyed
        if (!level->blocks[i]->active) {
            // Check for powerup spawn
            if (GetRandomValue(0, 100) / 100.0f < level->config.powerupSpawnChance) {
                SpawnPowerup(level, level->blocks[i]->position);
            }
            
            // Remove block
            RemoveBlockFromLevel(level, i);
            i--; // Adjust index
        }
    }
    
    // Update paddles
    UpdatePaddle(&level->playerOnePaddle, deltaTime);
    UpdatePaddle(&level->playerTwoPaddle, deltaTime);
    
    // Update balls
    for (int i = 0; i < level->ballCount; i++) {
        UpdateBall(level->balls[i], deltaTime);
        
        // Check ball collisions with blocks
        CheckBallBlockCollisions(level->balls[i], level->blocks, level->blockCount);
        
        // Check ball collisions with paddles
        CheckBallPaddleCollision(level->balls[i], &level->playerOnePaddle);
        CheckBallPaddleCollision(level->balls[i], &level->playerTwoPaddle);
        
        // Check ball collisions with level bounds
        CheckBallBoundaryCollision(level->balls[i], level->bounds);
        
        // Check if ball is out of bounds
        if (!IsBallInBounds(level->balls[i], level->bounds)) {
            // Remove ball
            RemoveBallFromLevel(level, i);
            i--; // Adjust index
        }
    }
}
```

### Level Rendering

```c
void DrawLevel(Level* level) {
    // Draw background
    DrawRectangleRec(level->bounds, RAYWHITE);
    
    // Draw blocks
    for (int i = 0; i < level->blockCount; i++) {
        DrawBlock(level->blocks[i]);
    }
    
    // Draw paddles
    DrawPaddle(&level->playerOnePaddle);
    DrawPaddle(&level->playerTwoPaddle);
    
    // Draw balls
    for (int i = 0; i < level->ballCount; i++) {
        DrawBall(level->balls[i]);
    }
}
```

## Level Events and Callbacks

```c
typedef void (*BlockDestroyedCallback)(Block* block, Vector2 position);
typedef void (*BallLostCallback)(Ball* ball, int playerSide);

typedef struct LevelEventHandlers {
    BlockDestroyedCallback onBlockDestroyed;
    BallLostCallback onBallLost;
} LevelEventHandlers;

void SetLevelEventHandlers(Level* level, LevelEventHandlers handlers) {
    // Store event handlers
    level->eventHandlers = handlers;
}
```

## Level Loading and Saving

For future expansion, the level system could support saving and loading custom levels:

```c
bool SaveLevelToFile(Level* level, const char* filePath) {
    FILE* file = fopen(filePath, "wb");
    if (!file) return false;
    
    // Write level configuration
    fwrite(&level->config, sizeof(LevelConfig), 1, file);
    
    // Write number of blocks
    fwrite(&level->blockCount, sizeof(int), 1, file);
    
    // Write block data
    for (int i = 0; i < level->blockCount; i++) {
        // Save block position, size, type, health, etc.
        fwrite(&level->blocks[i]->position, sizeof(Vector2), 1, file);
        fwrite(&level->blocks[i]->size, sizeof(Vector2), 1, file);
        fwrite(&level->blocks[i]->type, sizeof(BlockType), 1, file);
        fwrite(&level->blocks[i]->health, sizeof(int), 1, file);
    }
    
    fclose(file);
    return true;
}

Level* LoadLevelFromFile(const char* filePath) {
    FILE* file = fopen(filePath, "rb");
    if (!file) return NULL;
    
    // Read level configuration
    LevelConfig config;
    fread(&config, sizeof(LevelConfig), 1, file);
    
    // Create level with this configuration
    Level* level = InitLevel(&config);
    
    // Read number of blocks
    int blockCount;
    fread(&blockCount, sizeof(int), 1, file);
    
    // Read and create blocks
    for (int i = 0; i < blockCount; i++) {
        Vector2 position, size;
        BlockType type;
        int health;
        
        fread(&position, sizeof(Vector2), 1, file);
        fread(&size, sizeof(Vector2), 1, file);
        fread(&type, sizeof(BlockType), 1, file);
        fread(&health, sizeof(int), 1, file);
        
        // Create block with loaded data
        Block* block = CreateBlock(position, size, type);
        block->health = health;
        
        // Add to level
        AddBlockToLevel(level, block);
    }
    
    fclose(file);
    return level;
}
```

## Level Editor Integration

For development purposes, a simple level editor interface could be implemented:

```c
typedef struct LevelEditor {
    Level* level;
    BlockType currentBlockType;
    Vector2 gridSize;
    bool editMode;
    bool placementMode;
    Vector2 cursorPosition;
} LevelEditor;

LevelEditor* InitLevelEditor(Level* level) {
    LevelEditor* editor = (LevelEditor*)malloc(sizeof(LevelEditor));
    editor->level = level;
    editor->currentBlockType = BLOCK_NORMAL;
    editor->gridSize = (Vector2){ 20.0f, 20.0f };
    editor->editMode = true;
    editor->placementMode = true;
    editor->cursorPosition = (Vector2){ 0.0f, 0.0f };
    return editor;
}

void UpdateLevelEditor(LevelEditor* editor) {
    if (editor->editMode) {
        // Update cursor position to mouse position
        editor->cursorPosition = GetMousePosition();
        
        // Snap to grid
        editor->cursorPosition.x = floorf(editor->cursorPosition.x / editor->gridSize.x) * editor->gridSize.x;
        editor->cursorPosition.y = floorf(editor->cursorPosition.y / editor->gridSize.y) * editor->gridSize.y;
        
        // Handle mouse input
        if (IsMouseButtonPressed(MOUSE_LEFT_BUTTON)) {
            if (editor->placementMode) {
                // Place block at cursor position
                Block* block = CreateBlock(
                    editor->cursorPosition,
                    (Vector2){ editor->gridSize.x, editor->gridSize.y },
                    editor->currentBlockType
                );
                AddBlockToLevel(editor->level, block);
            } else {
                // Remove block at cursor position
                int blockIndex = GetBlockAtPosition(editor->level, editor->cursorPosition);
                if (blockIndex >= 0) {
                    RemoveBlockFromLevel(editor->level, blockIndex);
                }
            }
        }
        
        // Toggle placement/removal mode
        if (IsKeyPressed(KEY_TAB)) {
            editor->placementMode = !editor->placementMode;
        }
        
        // Change block type
        if (IsKeyPressed(KEY_ONE)) editor->currentBlockType = BLOCK_NORMAL;
        if (IsKeyPressed(KEY_TWO)) editor->currentBlockType = BLOCK_STRONG;
        if (IsKeyPressed(KEY_THREE)) editor->currentBlockType = BLOCK_WEAK;
    }
}

void DrawLevelEditor(LevelEditor* editor) {
    // Draw the level
    DrawLevel(editor->level);
    
    if (editor->editMode) {
        // Draw grid
        for (int x = 0; x < editor->level->config.width; x += (int)editor->gridSize.x) {
            DrawLine(x, 0, x, editor->level->config.height, GRAY);
        }
        
        for (int y = 0; y < editor->level->config.height; y += (int)editor->gridSize.y) {
            DrawLine(0, y, editor->level->config.width, y, GRAY);
        }
        
        // Draw cursor
        Color cursorColor = editor->placementMode ? GREEN : RED;
        DrawRectangleLines(
            editor->cursorPosition.x, 
            editor->cursorPosition.y,
            editor->gridSize.x,
            editor->gridSize.y,
            cursorColor
        );
        
        // Draw UI
        DrawText(editor->placementMode ? "Mode: Place" : "Mode: Remove", 10, 10, 20, BLACK);
        DrawText(GetBlockTypeName(editor->currentBlockType), 10, 40, 20, BLACK);
    }
}
```

## Performance Considerations

1. **Block Storage Optimization**:
   - Use a spatial partitioning system (grid or quadtree) for large numbers of blocks
   - Implement culling for off-screen blocks

2. **Collision Optimization**:
   - Use broad-phase collision detection first
   - Only perform detailed collision tests on potentially colliding objects

3. **Memory Usage**:
   - Pre-allocate block arrays with reasonable capacity
   - Reuse block objects when possible instead of creating/destroying

## Level Design Considerations

1. **Balanced Difficulty**:
   - Easy levels: Fewer and simpler blocks, more powerups
   - Hard levels: More blocks, more strong blocks, fewer powerups

2. **Visual Appeal**:
   - Use different block arrangements for visual interest
   - Consider color schemes and visual themes for different difficulty levels

3. **Gameplay Flow**:
   - Ensure levels have a good rhythm of destruction
   - Avoid unreachable blocks or unfair arrangements 