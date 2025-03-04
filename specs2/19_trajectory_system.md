# Trajectory System Specification

## Overview

The Trajectory System is responsible for predicting and visualizing the future path of balls in the game. It provides a visual guide showing where a ball will travel, including bounces off walls, paddles, and blocks. This enhances gameplay by allowing players to anticipate ball movement and plan their strategies accordingly.

The trajectory is represented as a dotted line that fades in opacity over distance, making it easy to see the immediate path while not overwhelming the player with too much visual information. The system supports predicting multiple bounces with accurate physics simulation, taking into account the game's collision mechanics.

## Core Architecture

```c
// Main trajectory structure
typedef struct Trajectory {
    int id;                   // Unique identifier
    Ball* ball;               // Reference to the ball being tracked
    float predictionTime;     // How far into the future to predict (in seconds)
    Vector2* points;          // Array of points representing the path
    int pointCount;           // Number of points in the path
    int maxPoints;            // Capacity of the points array
    Color color;              // Color of the trajectory line
    Texture2D dotTexture;     // Optional texture for dots (can be null)
    bool visible;             // Whether the trajectory is currently visible
} Trajectory;

// Trajectory system that manages all trajectories
typedef struct TrajectorySystem {
    Trajectory* trajectories;    // Array of all trajectories
    int count;                   // Number of active trajectories
    int capacity;                // Maximum capacity
    float updateInterval;        // How often to update predictions (seconds)
    float timeSinceLastUpdate;   // Time tracking for updates
    bool enabled;                // Whether the system is enabled globally
} TrajectorySystem;
```

## System Initialization

```c
// Initialize the trajectory system
TrajectorySystem* InitTrajectorySystem(int maxTrajectories, float updateInterval) {
    TrajectorySystem* system = MemAlloc(sizeof(TrajectorySystem));
    
    system->trajectories = MemAlloc(sizeof(Trajectory) * maxTrajectories);
    system->count = 0;
    system->capacity = maxTrajectories;
    system->updateInterval = updateInterval;
    system->timeSinceLastUpdate = 0;
    system->enabled = true;
    
    return system;
}

// Free trajectory system resources
void FreeTrajectorySystem(TrajectorySystem* system) {
    // Free all active trajectories
    for (int i = 0; i < system->count; i++) {
        FreeTrajectory(&system->trajectories[i]);
    }
    
    // Free the system itself
    MemFree(system->trajectories);
    MemFree(system);
}
```

## Core Functionality

### Trajectory Creation

```c
// Create a new trajectory for a ball
int CreateTrajectory(TrajectorySystem* system, Ball* ball, float predictionTime, Color color) {
    if (system->count >= system->capacity) {
        return -1; // System is full
    }
    
    int index = system->count++;
    Trajectory* trajectory = &system->trajectories[index];
    
    trajectory->id = GetNextTrajectoryId();
    trajectory->ball = ball;
    trajectory->predictionTime = predictionTime;
    trajectory->maxPoints = 100; // Initial capacity
    trajectory->points = MemAlloc(sizeof(Vector2) * trajectory->maxPoints);
    trajectory->pointCount = 0;
    trajectory->color = color;
    trajectory->dotTexture = LoadTexture("res/dot.png"); // Optional, can be null
    trajectory->visible = true;
    
    // Initial calculation of trajectory path
    PredictTrajectoryPath(trajectory);
    
    return trajectory->id;
}

// Free a trajectory's resources
void FreeTrajectory(Trajectory* trajectory) {
    if (trajectory->points) {
        MemFree(trajectory->points);
        trajectory->points = NULL;
    }
    
    if (trajectory->dotTexture.id > 0) {
        UnloadTexture(trajectory->dotTexture);
    }
}
```

### Path Prediction

```c
// Predict the path of a ball
void PredictTrajectoryPath(Trajectory* trajectory) {
    // Reset point count
    trajectory->pointCount = 0;
    
    // Starting point is current ball position
    AddPointToTrajectory(trajectory, 
        (Vector2){
            trajectory->ball->position.x + trajectory->ball->size.x/2, 
            trajectory->ball->position.y + trajectory->ball->size.y/2
        }
    );
    
    // Calculate velocities
    float speedX = trajectory->ball->speed * cosf(trajectory->ball->angle);
    float speedY = trajectory->ball->speed * sinf(trajectory->ball->angle);
    
    // Current position
    float currentX = trajectory->ball->position.x;
    float currentY = trajectory->ball->position.y;
    
    // Physics simulation variables
    const float dt = 1.0f / 60.0f; // Time step (60fps)
    float timeSimulated = 0;
    int bounceCount = 0;
    const int maxBounces = 3;
    
    // Create a temporary rectangle for collision detection
    Rectangle ballRect = {
        currentX, currentY,
        trajectory->ball->size.x, trajectory->ball->size.y
    };
    
    // Main simulation loop
    while (timeSimulated < trajectory->predictionTime && bounceCount < maxBounces) {
        // Calculate next position
        float nextX = currentX + speedX * dt;
        float nextY = currentY + speedY * dt;
        
        // Check for collisions with walls
        if (nextX < LEVEL_X) {
            // Hit left wall
            nextX = LEVEL_X;
            speedX = -speedX;
            bounceCount++;
        } else if (nextX + trajectory->ball->size.x > LEVEL_MAX_X) {
            // Hit right wall
            nextX = LEVEL_MAX_X - trajectory->ball->size.x;
            speedX = -speedX;
            bounceCount++;
        }
        
        if (nextY < LEVEL_Y) {
            // Hit top wall
            nextY = LEVEL_Y;
            speedY = -speedY;
            bounceCount++;
        } else if (nextY + trajectory->ball->size.y > LEVEL_MAX_Y) {
            // Hit bottom wall
            nextY = LEVEL_MAX_Y - trajectory->ball->size.y;
            speedY = -speedY;
            bounceCount++;
        }
        
        // Update temporary rectangle for collision detection
        ballRect.x = nextX;
        ballRect.y = nextY;
        
        // Check for collisions with paddles
        for (int i = 0; i < paddleSystem->count; i++) {
            Paddle* paddle = &paddleSystem->paddles[i];
            if (CheckCollisionRecs(ballRect, paddle->rect)) {
                bounceCount++;
                
                // Add collision point
                AddPointToTrajectory(trajectory, 
                    (Vector2){
                        nextX + trajectory->ball->size.x/2, 
                        nextY + trajectory->ball->size.y/2
                    }
                );
                
                if (bounceCount >= maxBounces) break;
                
                // Handle paddle collision physics (simplified version)
                HandlePaddleCollision(paddle, &nextX, &nextY, &speedX, &speedY, trajectory->ball);
                
                // Skip block collision check for this iteration
                goto SkipBlockCheck;
            }
        }
        
        // Check for collisions with blocks
        for (int i = 0; i < blockSystem->count; i++) {
            Block* block = &blockSystem->blocks[i];
            if (block->active && CheckCollisionRecs(ballRect, block->rect)) {
                bounceCount++;
                
                // Add collision point
                AddPointToTrajectory(trajectory, 
                    (Vector2){
                        nextX + trajectory->ball->size.x/2, 
                        nextY + trajectory->ball->size.y/2
                    }
                );
                
                if (bounceCount >= maxBounces) break;
                
                // Handle block collision physics (simplified version)
                HandleBlockCollision(block, &nextX, &nextY, &speedX, &speedY);
                break;
            }
        }
        
    SkipBlockCheck:
        // Add point to trajectory
        AddPointToTrajectory(trajectory, 
            (Vector2){
                nextX + trajectory->ball->size.x/2, 
                nextY + trajectory->ball->size.y/2
            }
        );
        
        // Update position
        currentX = nextX;
        currentY = nextY;
        
        // Update simulation time
        timeSimulated += dt;
    }
}

// Add a point to the trajectory path
void AddPointToTrajectory(Trajectory* trajectory, Vector2 point) {
    // Resize points array if needed
    if (trajectory->pointCount >= trajectory->maxPoints) {
        trajectory->maxPoints *= 2;
        trajectory->points = MemRealloc(trajectory->points, sizeof(Vector2) * trajectory->maxPoints);
    }
    
    // Add the point
    trajectory->points[trajectory->pointCount++] = point;
}
```

### Trajectory Rendering

```c
// Draw all trajectories
void DrawTrajectories(TrajectorySystem* system) {
    if (!system->enabled) return;
    
    for (int i = 0; i < system->count; i++) {
        Trajectory* trajectory = &system->trajectories[i];
        if (trajectory->visible && trajectory->pointCount > 1) {
            DrawTrajectoryPath(trajectory);
        }
    }
}

// Draw a single trajectory
void DrawTrajectoryPath(Trajectory* trajectory) {
    // Skip if insufficient points
    if (trajectory->pointCount < 2) return;
    
    // Calculate segment properties based on path length
    float totalLength = 0;
    for (int i = 0; i < trajectory->pointCount - 1; i++) {
        Vector2 current = trajectory->points[i];
        Vector2 next = trajectory->points[i + 1];
        totalLength += Vector2Distance(current, next);
    }
    
    // Draw evenly spaced segments with fading opacity
    const float segmentLength = 4.0f; // Length of each segment (drawn + gap)
    const int numSegments = (int)(totalLength / segmentLength);
    
    for (int i = 0; i < numSegments; i++) {
        // Calculate start and end positions for this segment
        float startPos = (float)i * segmentLength / totalLength;
        float endPos = (float)i * segmentLength + segmentLength/2.0f / totalLength;
        
        if (startPos >= 1.0f) break;
        endPos = fminf(endPos, 1.0f);
        
        // Find the start and end points for this segment
        Vector2 segStart = GetPointAlongPath(trajectory, startPos);
        Vector2 segEnd = GetPointAlongPath(trajectory, endPos);
        
        // Calculate alpha value that fades over distance
        unsigned char alpha = (unsigned char)(255 - (230 * startPos)); // 255 -> 25 linear fade
        alpha = alpha < 25 ? 25 : alpha; // Minimum alpha of 25
        
        // Draw the segment
        Color segColor = trajectory->color;
        segColor.a = alpha;
        
        if (trajectory->dotTexture.id > 0) {
            // Draw textured dot
            float size = 3.0f * (1.0f - 0.7f * startPos); // Size decreases with distance
            DrawTexturePro(
                trajectory->dotTexture,
                (Rectangle){ 0, 0, trajectory->dotTexture.width, trajectory->dotTexture.height },
                (Rectangle){ segStart.x, segStart.y, size, size },
                (Vector2){ size/2, size/2 },
                0.0f,
                segColor
            );
        } else {
            // Draw line segment
            DrawLineEx(segStart, segEnd, 2.0f, segColor);
        }
    }
}

// Get a point along the path at a specific percentage (0.0 to 1.0)
Vector2 GetPointAlongPath(Trajectory* trajectory, float percentage) {
    // Calculate total path length
    float totalLength = 0;
    float* segmentLengths = MemAlloc(sizeof(float) * (trajectory->pointCount - 1));
    
    for (int i = 0; i < trajectory->pointCount - 1; i++) {
        Vector2 current = trajectory->points[i];
        Vector2 next = trajectory->points[i + 1];
        segmentLengths[i] = Vector2Distance(current, next);
        totalLength += segmentLengths[i];
    }
    
    // Find the point at the given percentage
    float targetLength = totalLength * percentage;
    float currentLength = 0;
    
    for (int i = 0; i < trajectory->pointCount - 1; i++) {
        float nextLength = currentLength + segmentLengths[i];
        
        if (currentLength <= targetLength && targetLength < nextLength) {
            // Interpolate between points
            float t = (targetLength - currentLength) / segmentLengths[i];
            Vector2 start = trajectory->points[i];
            Vector2 end = trajectory->points[i + 1];
            
            Vector2 result = {
                start.x + (end.x - start.x) * t,
                start.y + (end.y - start.y) * t
            };
            
            MemFree(segmentLengths);
            return result;
        }
        
        currentLength = nextLength;
    }
    
    // If not found, return the last point
    MemFree(segmentLengths);
    return trajectory->points[trajectory->pointCount - 1];
}
```

### System Update

```c
// Update the trajectory system
void UpdateTrajectorySystem(TrajectorySystem* system, float deltaTime) {
    if (!system->enabled) return;
    
    // Update timer
    system->timeSinceLastUpdate += deltaTime;
    
    // Check if it's time to update predictions
    if (system->timeSinceLastUpdate >= system->updateInterval) {
        system->timeSinceLastUpdate = 0;
        
        // Update all trajectories
        for (int i = 0; i < system->count; i++) {
            if (system->trajectories[i].visible) {
                PredictTrajectoryPath(&system->trajectories[i]);
            }
        }
    }
}
```

## Helper Functions

```c
// Handle collisions with paddles for prediction
void HandlePaddleCollision(Paddle* paddle, float* x, float* y, float* speedX, float* speedY, Ball* ball) {
    Rectangle paddleRect = paddle->rect;
    Rectangle ballRect = { *x, *y, ball->size.x, ball->size.y };
    
    // Calculate centers
    float ballCenterX = *x + ball->size.x / 2;
    float ballCenterY = *y + ball->size.y / 2;
    float paddleCenterX = paddleRect.x + paddleRect.width / 2;
    float paddleCenterY = paddleRect.y + paddleRect.height / 2;
    
    // Calculate vector from paddle center to ball center
    float deltaX = ballCenterX - paddleCenterX;
    float deltaY = ballCenterY - paddleCenterY;
    
    // Collision resolution based on the side of the paddle hit
    // Left or right side collision
    if (fabs(deltaX) / (paddleRect.width/2 + ball->size.x/2) > 
        fabs(deltaY) / (paddleRect.height/2 + ball->size.y/2)) {
        
        if (deltaX > 0) {
            // Right side collision
            *x = paddleRect.x + paddleRect.width;
            
            // Calculate bounce angle based on hit position
            float normalizedDist = (ballCenterY - paddleCenterY) / 
                                  (paddleRect.height/2 + ball->size.y/2);
            float angle = normalizedDist * (M_PI/3); // 60 degree range
            
            *speedX = ball->speed * cosf(angle);
            *speedY = ball->speed * sinf(angle);
        } else {
            // Left side collision
            *x = paddleRect.x - ball->size.x;
            
            // Calculate bounce angle based on hit position
            float normalizedDist = (ballCenterY - paddleCenterY) / 
                                  (paddleRect.height/2 + ball->size.y/2);
            float angle = M_PI - normalizedDist * (M_PI/3); // 60 degree range
            
            *speedX = ball->speed * cosf(angle);
            *speedY = ball->speed * sinf(angle);
        }
    }
    // Top or bottom collision
    else {
        if (deltaY > 0) {
            // Bottom collision
            *y = paddleRect.y + paddleRect.height;
            *speedY = fabs(*speedY);
        } else {
            // Top collision
            *y = paddleRect.y - ball->size.y;
            *speedY = -fabs(*speedY);
        }
    }
}

// Handle collisions with blocks for prediction
void HandleBlockCollision(Block* block, float* x, float* y, float* speedX, float* speedY) {
    Rectangle blockRect = block->rect;
    Rectangle ballRect = { *x, *y, ball->size.x, ball->size.y };
    
    // Calculate centers
    float ballCenterX = *x + ball->size.x / 2;
    float ballCenterY = *y + ball->size.y / 2;
    float blockCenterX = blockRect.x + blockRect.width / 2;
    float blockCenterY = blockRect.y + blockRect.height / 2;
    
    // Calculate vector from block center to ball center
    float deltaX = ballCenterX - blockCenterX;
    float deltaY = ballCenterY - blockCenterY;
    
    // Determine collision side by comparing normalized distances
    if (fabs(deltaX) / (blockRect.width/2 + ball->size.x/2) > 
        fabs(deltaY) / (blockRect.height/2 + ball->size.y/2)) {
        
        // Horizontal collision (left or right)
        *speedX = -(*speedX);
        
        if (deltaX > 0) {
            // Right side collision
            *x = blockRect.x + blockRect.width;
        } else {
            // Left side collision
            *x = blockRect.x - ball->size.x;
        }
    } else {
        // Vertical collision (top or bottom)
        *speedY = -(*speedY);
        
        if (deltaY > 0) {
            // Bottom collision
            *y = blockRect.y + blockRect.height;
        } else {
            // Top collision
            *y = blockRect.y - ball->size.y;
        }
    }
    
    // Apply minimum angle constraints
    const float minVerticalAngle = 0.3f;  // ~17 degrees from horizontal
    const float minHorizontalAngle = 0.3f; // ~17 degrees from vertical
    
    // Calculate current angle
    float angle = atan2f(*speedY, *speedX);
    
    // Check if too close to horizontal
    if (fabsf(*speedY) / ball->speed < sinf(minVerticalAngle)) {
        // Correct the angle while preserving direction
        if (*speedY > 0) {
            *speedY = ball->speed * sinf(minVerticalAngle);
        } else {
            *speedY = -ball->speed * sinf(minVerticalAngle);
        }
        
        // Recalculate speedX to maintain consistent speed
        *speedX = (*speedX > 0) ? 
            sqrtf(ball->speed*ball->speed - (*speedY)*(*speedY)) :
            -sqrtf(ball->speed*ball->speed - (*speedY)*(*speedY));
    }
    // Check if too close to vertical
    else if (fabsf(*speedX) / ball->speed < sinf(minHorizontalAngle)) {
        // Correct the angle while preserving direction
        if (*speedX > 0) {
            *speedX = ball->speed * sinf(minHorizontalAngle);
        } else {
            *speedX = -ball->speed * sinf(minHorizontalAngle);
        }
        
        // Recalculate speedY to maintain consistent speed
        *speedY = (*speedY > 0) ? 
            sqrtf(ball->speed*ball->speed - (*speedX)*(*speedX)) :
            -sqrtf(ball->speed*ball->speed - (*speedX)*(*speedX));
    }
}
```

## System Management

```c
// Enable/disable a specific trajectory
void SetTrajectoryVisible(TrajectorySystem* system, int trajectoryId, bool visible) {
    for (int i = 0; i < system->count; i++) {
        if (system->trajectories[i].id == trajectoryId) {
            system->trajectories[i].visible = visible;
            return;
        }
    }
}

// Enable/disable the entire trajectory system
void SetTrajectorySystemEnabled(TrajectorySystem* system, bool enabled) {
    system->enabled = enabled;
}

// Remove a trajectory from the system
void RemoveTrajectory(TrajectorySystem* system, int trajectoryId) {
    for (int i = 0; i < system->count; i++) {
        if (system->trajectories[i].id == trajectoryId) {
            // Free resources
            FreeTrajectory(&system->trajectories[i]);
            
            // Move the last trajectory to this slot
            if (i < system->count - 1) {
                system->trajectories[i] = system->trajectories[system->count - 1];
            }
            
            // Decrease count
            system->count--;
            return;
        }
    }
}
```

## Integration

### Ball Integration

```c
// Create a trajectory for a ball (in ball.c)
void EnableBallTrajectory(Ball* ball, TrajectorySystem* system) {
    if (ball->trajectoryId == -1) {
        // Create new trajectory
        ball->trajectoryId = CreateTrajectory(system, ball, 0.25f, ball->color);
    } else {
        // Make existing trajectory visible
        SetTrajectoryVisible(system, ball->trajectoryId, true);
    }
}

// Disable a ball's trajectory (in ball.c)
void DisableBallTrajectory(Ball* ball, TrajectorySystem* system) {
    if (ball->trajectoryId != -1) {
        SetTrajectoryVisible(system, ball->trajectoryId, false);
    }
}

// Clean up a ball's trajectory (in ball.c)
void DestroyBallTrajectory(Ball* ball, TrajectorySystem* system) {
    if (ball->trajectoryId != -1) {
        RemoveTrajectory(system, ball->trajectoryId);
        ball->trajectoryId = -1;
    }
}
```

### Game Integration

```c
// In game.c - add to game initialization
void InitGame() {
    // ... other initialization ...
    
    // Initialize trajectory system
    trajectorySystem = InitTrajectorySystem(MAX_BALLS, 0.1f); // Update every 100ms
    
    // ... continue initialization ...
}

// In game.c - add to game update
void UpdateGame() {
    // ... other updates ...
    
    // Update trajectory system
    UpdateTrajectorySystem(trajectorySystem, GetFrameTime());
    
    // ... continue updates ...
}

// In game.c - add to game rendering
void DrawGame() {
    // ... other rendering ...
    
    // Draw trajectories
    DrawTrajectories(trajectorySystem);
    
    // ... continue rendering ...
}

// In game.c - add to game cleanup
void UnloadGame() {
    // ... other cleanup ...
    
    // Clean up trajectory system
    FreeTrajectorySystem(trajectorySystem);
    
    // ... continue cleanup ...
}
```

## Settings Integration

```c
// Integration with settings system
void ApplyTrajectorySettings(TrajectorySystem* system) {
    system->enabled = GetGameSettingBool("show_trajectories", true);
    system->updateInterval = GetGameSettingFloat("trajectory_update_interval", 0.1f);
}
```

## Performance Considerations

1. **Prediction Optimization**: The trajectory prediction is computationally intensive, especially with many objects. The system uses an update interval to avoid recalculating trajectories every frame.

2. **Memory Management**: The system pre-allocates memory for trajectory points and grows the array only when needed.

3. **Rendering Optimization**: The drawing system uses efficient line rendering with segment culling for off-screen portions.

4. **Collision Approximation**: For prediction purposes, collision handling is simplified compared to the actual game physics to improve performance.

5. **Visible-only Updates**: Trajectories are only updated when visible to save processing power.

## Implementation Notes

1. The trajectory system is entirely visual and does not affect game physics.

2. Trajectories are updated periodically rather than every frame.

3. Prediction physics should match the actual game physics as closely as possible without excessive computation.

4. The system supports optional textures for dot-based trajectories instead of lines.

5. Trajectory visibility can be toggled both per-trajectory and system-wide.

6. The prediction length and bounce count can be adjusted for performance vs. utility.

7. Trajectory color and opacity parameters allow for visual customization.

## Conclusion

The Trajectory System enhances gameplay by providing visual feedback about ball movement paths. It helps players anticipate ball movement and plan their strategies, adding depth to the gameplay without affecting the core mechanics. The system is designed to be efficient, visually appealing, and tightly integrated with the game's physics system to ensure accurate predictions. 