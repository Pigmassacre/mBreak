# Rendering System Overview

## System Components

### Renderer
```c
typedef struct Renderer {
    // Core properties
    int screenWidth;
    int screenHeight;
    bool vsyncEnabled;
    bool fullscreen;
    
    // Render targets
    RenderTexture2D* mainTarget;
    RenderTexture2D* postProcessTarget;
    
    // Shaders
    Shader* activeShader;
    Shader** shaderStack;
    int shaderCount;
    
    // Camera
    Camera2D* activeCamera;
    
    // Render queues
    RenderQueue* backgroundQueue;
    RenderQueue* worldQueue;
    RenderQueue* uiQueue;
    RenderQueue* debugQueue;
} Renderer;
```

### Render Queue
```c
typedef struct RenderQueue {
    // Batched sprites
    struct {
        Texture2D* textures;
        Rectangle* sourceRects;
        Rectangle* destRects;
        Color* colors;
        float* rotations;
        Vector2* origins;
        int count;
        int capacity;
    } spriteBatch;
    
    // Particle systems
    ParticleSystem** particleSystems;
    int particleSystemCount;
    
    // Custom render commands
    RenderCommand* commands;
    int commandCount;
} RenderQueue;
```

### Render Command
```c
typedef struct RenderCommand {
    RenderCommandType type;
    int priority;
    bool isTransparent;
    
    // Command data
    union {
        struct {
            Texture2D texture;
            Rectangle source;
            Rectangle dest;
            float rotation;
            Color tint;
        } sprite;
        
        struct {
            const char* text;
            Vector2 position;
            float fontSize;
            Color color;
        } text;
        
        struct {
            Vector2* vertices;
            Color* colors;
            int count;
        } primitive;
    } data;
} RenderCommand;
```

## Core Features

### Sprite Rendering
```c
void DrawSprite(Texture2D texture, Vector2 position, float rotation, float scale, Color tint) {
    // Create sprite command
    RenderCommand command = {
        .type = RENDER_SPRITE,
        .priority = CalculateRenderPriority(position.y),
        .isTransparent = HasTransparency(texture),
        .data.sprite = {
            .texture = texture,
            .source = (Rectangle){ 0, 0, texture.width, texture.height },
            .dest = (Rectangle){ position.x, position.y, texture.width * scale, texture.height * scale },
            .rotation = rotation,
            .tint = tint
        }
    };
    
    // Add to appropriate queue
    AddToRenderQueue(GetCurrentQueue(), command);
}
```

### Batch Processing
```c
void ProcessRenderQueue(RenderQueue* queue) {
    // Sort commands by priority
    SortRenderCommands(queue->commands, queue->commandCount);
    
    // Process opaque commands first
    for (int i = 0; i < queue->commandCount; i++) {
        if (!queue->commands[i].isTransparent) {
            ExecuteRenderCommand(&queue->commands[i]);
        }
    }
    
    // Process transparent commands
    for (int i = 0; i < queue->commandCount; i++) {
        if (queue->commands[i].isTransparent) {
            ExecuteRenderCommand(&queue->commands[i]);
        }
    }
}
```

### Camera System
```c
void UpdateCamera(Camera2D* camera, Vector2 target) {
    // Update camera position
    camera->target = target;
    
    // Apply camera bounds
    camera->target.x = Clamp(camera->target.x, camera->bounds.x, camera->bounds.width);
    camera->target.y = Clamp(camera->target.y, camera->bounds.y, camera->bounds.height);
    
    // Update camera matrix
    UpdateCameraMatrix(camera);
}
```

## Post-Processing

### Shader System
```c
void ApplyPostProcess(RenderTexture2D* source, RenderTexture2D* target, Shader shader) {
    // Begin drawing to target
    BeginTextureMode(*target);
    
    // Apply shader
    BeginShaderMode(shader);
    
    // Draw source texture
    DrawTexturePro(source->texture,
        (Rectangle){ 0, 0, source->texture.width, -source->texture.height },
        (Rectangle){ 0, 0, target->texture.width, target->texture.height },
        (Vector2){ 0, 0 }, 0.0f, WHITE);
    
    // End shader and target
    EndShaderMode();
    EndTextureMode();
}
```

### Effect Stack
```c
void PushPostEffect(Renderer* renderer, PostEffect effect) {
    // Create effect shader
    Shader shader = LoadPostEffectShader(effect);
    
    // Push to shader stack
    renderer->shaderStack[renderer->shaderCount++] = shader;
    
    // Update active shader
    UpdateShaderStack(renderer);
}
```

## Particle System

### Particle Management
```c
typedef struct ParticleSystem {
    // Particle data
    struct {
        Vector2* positions;
        Vector2* velocities;
        Color* colors;
        float* sizes;
        float* lifetimes;
        int count;
        int capacity;
    } particles;
    
    // Emitter properties
    struct {
        Vector2 position;
        float spawnRate;
        float spawnTimer;
        ParticleConfig config;
    } emitter;
} ParticleSystem;

void UpdateParticleSystem(ParticleSystem* system, float deltaTime) {
    // Spawn new particles
    system->emitter.spawnTimer += deltaTime;
    while (system->emitter.spawnTimer >= system->emitter.spawnRate) {
        SpawnParticle(system);
        system->emitter.spawnTimer -= system->emitter.spawnRate;
    }
    
    // Update existing particles
    for (int i = 0; i < system->particles.count; i++) {
        UpdateParticle(system, i, deltaTime);
        if (IsParticleDead(system, i)) {
            RemoveParticle(system, i--);
        }
    }
}
```

## Debug Features

### Debug Rendering
```c
void DrawDebugInfo(Renderer* renderer) {
    if (!IsDebugMode()) return;
    
    // Draw FPS
    DrawFPS(10, 10);
    
    // Draw render stats
    DrawRenderStats(renderer);
    
    // Draw debug shapes
    DrawDebugShapes();
    
    // Draw particle counts
    DrawParticleStats();
}
```

### Performance Monitoring
```c
void MonitorRenderPerformance(Renderer* renderer) {
    // Track frame time
    TrackFrameTime();
    
    // Monitor GPU memory
    TrackGPUMemory();
    
    // Track batch statistics
    TrackBatchStats();
    
    // Monitor shader performance
    TrackShaderPerformance();
}
``` 