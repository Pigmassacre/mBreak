# Resource Management System

## Overview

The resource management system in mBreak handles loading, storing, and accessing various game assets including textures, sounds, fonts, and other data. This specification details how resources are managed in the Python implementation and provides guidelines for implementing a robust resource management system in the C/Raylib port.

## Current Implementation (Python + Pygame)

### Core Components

#### Resource Loading

In the Python implementation, resources are loaded directly as needed, often at module initialization or during object creation:

- Textures are loaded via `pygame.image.load()`
- Sounds are loaded through `pygame.mixer.Sound()`
- Fonts are loaded with `pygame.font.Font()`

Resources are stored in the following key directories:
- `res/`: Contains images, sounds, and other media files
- `fonts/`: Contains font files

#### Resource Organization

The game resources are organized into subdirectories by type and usage:
- `res/effect/`: Effect-related images
- `res/powerup/`: Powerup-related images
- `res/block/`: Block-related images
- `res/paddle/`: Paddle-related images
- `res/sound/`: Sound files
- `fonts/`: Font files

#### Resource Management Approach

The current approach has some limitations:
- No centralized resource management system
- Resources are loaded when needed, often multiple times
- Limited resource sharing between objects
- No explicit resource unloading in most cases

## Port Implementation (C + Raylib)

### Core Resource Manager

```c
// Resource types
typedef enum ResourceType {
    RESOURCE_TEXTURE,
    RESOURCE_SOUND,
    RESOURCE_MUSIC,
    RESOURCE_FONT,
    RESOURCE_SHADER,
    RESOURCE_MODEL
} ResourceType;

// Resource data structure
typedef struct Resource {
    char* id;               // Resource identifier
    ResourceType type;      // Type of resource
    void* data;             // Pointer to the resource data
    int refCount;           // Reference count for memory management
    bool persistent;        // Whether the resource should persist between screen transitions
} Resource;

// Resource manager
typedef struct ResourceManager {
    Resource** resources;   // Array of resource pointers
    int count;              // Current number of resources
    int capacity;           // Maximum capacity
    char* basePath;         // Base path for resource loading
} ResourceManager;
```

### Core Functions

```c
// Initialize the resource manager
ResourceManager* InitResourceManager(int initialCapacity, const char* basePath);

// Free the resource manager and all resources
void FreeResourceManager(ResourceManager* manager);

// Resource loading functions
int LoadTexture(ResourceManager* manager, const char* id, const char* filePath);
int LoadSound(ResourceManager* manager, const char* id, const char* filePath);
int LoadMusic(ResourceManager* manager, const char* id, const char* filePath);
int LoadFont(ResourceManager* manager, const char* id, const char* filePath, int fontSize);
int LoadShader(ResourceManager* manager, const char* id, const char* vsFilePath, const char* fsFilePath);

// Resource retrieval functions
Texture2D* GetTexture(ResourceManager* manager, const char* id);
Sound* GetSound(ResourceManager* manager, const char* id);
Music* GetMusic(ResourceManager* manager, const char* id);
Font* GetFont(ResourceManager* manager, const char* id);
Shader* GetShader(ResourceManager* manager, const char* id);

// Resource reference counting
void AcquireResource(ResourceManager* manager, const char* id);
void ReleaseResource(ResourceManager* manager, const char* id);

// Resource management
void UnloadUnusedResources(ResourceManager* manager);
void UnloadAllResources(ResourceManager* manager);
void SetResourcePersistent(ResourceManager* manager, const char* id, bool persistent);
```

### Implementation Details

#### Resource Loading and Caching

```c
int LoadTexture(ResourceManager* manager, const char* id, const char* filePath) {
    // Check if resource already exists
    for (int i = 0; i < manager->count; i++) {
        if (strcmp(manager->resources[i]->id, id) == 0) {
            // Resource exists, increment reference count
            manager->resources[i]->refCount++;
            return i;
        }
    }
    
    // Full path construction
    char fullPath[256];
    sprintf(fullPath, "%s/%s", manager->basePath, filePath);
    
    // Load the texture
    Texture2D* texture = (Texture2D*)malloc(sizeof(Texture2D));
    *texture = LoadTexture(fullPath);
    
    if (texture->id == 0) {
        // Failed to load
        free(texture);
        return -1;
    }
    
    // Create new resource entry
    Resource* resource = (Resource*)malloc(sizeof(Resource));
    resource->id = strdup(id);
    resource->type = RESOURCE_TEXTURE;
    resource->data = texture;
    resource->refCount = 1;
    resource->persistent = false;
    
    // Add to resource array
    if (manager->count >= manager->capacity) {
        // Expand capacity
        manager->capacity *= 2;
        manager->resources = (Resource**)realloc(manager->resources, 
                                                manager->capacity * sizeof(Resource*));
    }
    
    manager->resources[manager->count] = resource;
    return manager->count++;
}
```

#### Resource Retrieval

```c
Texture2D* GetTexture(ResourceManager* manager, const char* id) {
    for (int i = 0; i < manager->count; i++) {
        if (strcmp(manager->resources[i]->id, id) == 0 && 
            manager->resources[i]->type == RESOURCE_TEXTURE) {
            return (Texture2D*)manager->resources[i]->data;
        }
    }
    return NULL;
}
```

#### Resource Reference Counting

```c
void AcquireResource(ResourceManager* manager, const char* id) {
    for (int i = 0; i < manager->count; i++) {
        if (strcmp(manager->resources[i]->id, id) == 0) {
            manager->resources[i]->refCount++;
            return;
        }
    }
}

void ReleaseResource(ResourceManager* manager, const char* id) {
    for (int i = 0; i < manager->count; i++) {
        if (strcmp(manager->resources[i]->id, id) == 0) {
            manager->resources[i]->refCount--;
            return;
        }
    }
}
```

#### Resource Cleanup

```c
void UnloadUnusedResources(ResourceManager* manager) {
    for (int i = 0; i < manager->count; i++) {
        if (manager->resources[i]->refCount <= 0 && !manager->resources[i]->persistent) {
            // Unload resource based on type
            switch (manager->resources[i]->type) {
                case RESOURCE_TEXTURE:
                    UnloadTexture(*(Texture2D*)manager->resources[i]->data);
                    break;
                case RESOURCE_SOUND:
                    UnloadSound(*(Sound*)manager->resources[i]->data);
                    break;
                case RESOURCE_MUSIC:
                    UnloadMusicStream(*(Music*)manager->resources[i]->data);
                    break;
                case RESOURCE_FONT:
                    UnloadFont(*(Font*)manager->resources[i]->data);
                    break;
                case RESOURCE_SHADER:
                    UnloadShader(*(Shader*)manager->resources[i]->data);
                    break;
            }
            
            // Free memory
            free(manager->resources[i]->data);
            free(manager->resources[i]->id);
            free(manager->resources[i]);
            
            // Remove from array (shift remaining elements)
            for (int j = i; j < manager->count - 1; j++) {
                manager->resources[j] = manager->resources[j + 1];
            }
            
            manager->count--;
            i--; // Adjust index after removal
        }
    }
}
```

## Resource Loading Patterns

### Preloading Resources

```c
void PreloadGameResources(ResourceManager* manager) {
    // Preload commonly used textures
    LoadTexture(manager, "paddle_blue", "res/paddle/paddle_blue.png");
    LoadTexture(manager, "paddle_red", "res/paddle/paddle_red.png");
    LoadTexture(manager, "ball", "res/ball.png");
    
    // Preload commonly used sounds
    LoadSound(manager, "ball_hit", "res/sound/ball_hit.wav");
    LoadSound(manager, "block_break", "res/sound/block_break.wav");
    
    // Preload fonts
    LoadFont(manager, "main_font", "fonts/main_font.ttf", 16);
    LoadFont(manager, "title_font", "fonts/title_font.ttf", 32);
    
    // Set critical resources as persistent
    SetResourcePersistent(manager, "main_font", true);
    SetResourcePersistent(manager, "title_font", true);
}
```

### Screen-specific Resource Loading

```c
void LoadGameplayResources(ResourceManager* manager) {
    // Load gameplay-specific resources
    LoadTexture(manager, "background", "res/background.png");
    LoadTexture(manager, "block_normal", "res/block/normal.png");
    LoadTexture(manager, "block_strong", "res/block/strong.png");
    
    // Load powerup textures
    LoadTexture(manager, "powerup_multiball", "res/powerup/multiball.png");
    LoadTexture(manager, "powerup_enlarge", "res/powerup/enlarge.png");
    // ... other powerups
    
    // Load effect textures
    LoadTexture(manager, "effect_explosion", "res/effect/explosion_sheet.png");
    LoadTexture(manager, "effect_spark", "res/effect/spark.png");
    
    // Load gameplay sounds
    LoadSound(manager, "powerup_collect", "res/sound/powerup_collect.wav");
    LoadSound(manager, "game_start", "res/sound/game_start.wav");
    LoadSound(manager, "game_over", "res/sound/game_over.wav");
}
```

### Resource Unloading

```c
void UnloadGameplayResources(ResourceManager* manager) {
    // Release gameplay-specific resources
    ReleaseResource(manager, "background");
    ReleaseResource(manager, "block_normal");
    ReleaseResource(manager, "block_strong");
    
    // Release powerup textures
    ReleaseResource(manager, "powerup_multiball");
    ReleaseResource(manager, "powerup_enlarge");
    // ... other powerups
    
    // Release effect textures
    ReleaseResource(manager, "effect_explosion");
    ReleaseResource(manager, "effect_spark");
    
    // Release gameplay sounds
    ReleaseResource(manager, "powerup_collect");
    ReleaseResource(manager, "game_start");
    ReleaseResource(manager, "game_over");
    
    // Clean up unused resources
    UnloadUnusedResources(manager);
}
```

## Integration with Game Systems

### Game Initialization

```c
void InitGame(Game* game) {
    // Initialize resource manager
    game->resourceManager = InitResourceManager(100, ".");
    
    // Preload common resources
    PreloadGameResources(game->resourceManager);
    
    // Initialize other game systems
    // ...
}
```

### Screen Transitions

```c
void TransitionToGameplayScreen(Game* game) {
    // Load gameplay resources
    LoadGameplayResources(game->resourceManager);
    
    // Initialize gameplay screen
    // ...
}

void ExitGameplayScreen(Game* game) {
    // Unload gameplay resources
    UnloadGameplayResources(game->resourceManager);
    
    // Clean up gameplay screen
    // ...
}
```

### Game Objects Using Resources

```c
void CreatePaddle(Game* game, int playerId, Vector2 position) {
    Paddle* paddle = (Paddle*)malloc(sizeof(Paddle));
    
    // Set paddle properties
    paddle->position = position;
    // ...
    
    // Get paddle texture based on player ID
    const char* textureId = (playerId == 1) ? "paddle_blue" : "paddle_red";
    paddle->texture = GetTexture(game->resourceManager, textureId);
    
    // Acquire resource reference
    AcquireResource(game->resourceManager, textureId);
    
    // Add paddle to game objects
    // ...
}

void DestroyPaddle(Game* game, Paddle* paddle) {
    // Determine texture ID
    const char* textureId = (paddle->texture == GetTexture(game->resourceManager, "paddle_blue")) 
                          ? "paddle_blue" : "paddle_red";
    
    // Release resource reference
    ReleaseResource(game->resourceManager, textureId);
    
    // Free paddle memory
    free(paddle);
}
```

## Memory Management

### Resource Pooling

For frequently loaded/unloaded resources:

```c
typedef struct ResourcePool {
    ResourceManager* manager;
    char** resourceIds;
    int count;
} ResourcePool;

ResourcePool* CreateResourcePool(ResourceManager* manager, int capacity) {
    ResourcePool* pool = (ResourcePool*)malloc(sizeof(ResourcePool));
    pool->manager = manager;
    pool->resourceIds = (char**)malloc(capacity * sizeof(char*));
    pool->count = 0;
    return pool;
}

void PoolAcquireResource(ResourcePool* pool, const char* id) {
    AcquireResource(pool->manager, id);
    pool->resourceIds[pool->count++] = strdup(id);
}

void ReleaseResourcePool(ResourcePool* pool) {
    for (int i = 0; i < pool->count; i++) {
        ReleaseResource(pool->manager, pool->resourceIds[i]);
        free(pool->resourceIds[i]);
    }
    pool->count = 0;
}
```

### Hot Reloading Support

For development purposes:

```c
void ReloadTexture(ResourceManager* manager, const char* id) {
    for (int i = 0; i < manager->count; i++) {
        if (strcmp(manager->resources[i]->id, id) == 0 && 
            manager->resources[i]->type == RESOURCE_TEXTURE) {
            
            // Get filepath (in a real implementation, store this with the resource)
            char filepath[256];
            sprintf(filepath, "%s/%s", manager->basePath, GetResourceFilePath(id));
            
            // Unload current texture
            UnloadTexture(*(Texture2D*)manager->resources[i]->data);
            
            // Load new texture
            *(Texture2D*)manager->resources[i]->data = LoadTexture(filepath);
            
            break;
        }
    }
}
```

## Performance Considerations

1. **Asynchronous Loading**:
   - Implement a background thread for resource loading during loading screens
   - Use a job system to load resources without blocking the main thread

2. **Memory Usage Optimization**:
   - Implement resource compression/decompression as needed
   - Use texture atlases to reduce draw calls
   - Support different resolution assets based on system capabilities

3. **Resource Streaming**:
   - Load high-priority resources first
   - Stream in additional resources during gameplay
   - Implement level-of-detail systems for textures and models

## Error Handling

```c
typedef enum ResourceError {
    RESOURCE_ERROR_NONE,
    RESOURCE_ERROR_FILE_NOT_FOUND,
    RESOURCE_ERROR_INVALID_FORMAT,
    RESOURCE_ERROR_OUT_OF_MEMORY
} ResourceError;

ResourceError GetLastResourceError(ResourceManager* manager);

void LogResourceError(ResourceManager* manager, const char* id, const char* filePath) {
    ResourceError error = GetLastResourceError(manager);
    
    switch (error) {
        case RESOURCE_ERROR_FILE_NOT_FOUND:
            printf("Resource Error: File not found - %s (%s)\n", id, filePath);
            break;
        case RESOURCE_ERROR_INVALID_FORMAT:
            printf("Resource Error: Invalid format - %s (%s)\n", id, filePath);
            break;
        case RESOURCE_ERROR_OUT_OF_MEMORY:
            printf("Resource Error: Out of memory - %s\n", id);
            break;
        default:
            break;
    }
}
```

## Resource Tracking

For development and debugging:

```c
void PrintResourceStats(ResourceManager* manager) {
    int textureCount = 0;
    int soundCount = 0;
    int fontCount = 0;
    int otherCount = 0;
    
    size_t textureMemory = 0;
    size_t soundMemory = 0;
    size_t fontMemory = 0;
    size_t otherMemory = 0;
    
    for (int i = 0; i < manager->count; i++) {
        switch (manager->resources[i]->type) {
            case RESOURCE_TEXTURE:
                textureCount++;
                textureMemory += GetTextureMemorySize(*(Texture2D*)manager->resources[i]->data);
                break;
            case RESOURCE_SOUND:
                soundCount++;
                soundMemory += GetSoundMemorySize(*(Sound*)manager->resources[i]->data);
                break;
            case RESOURCE_FONT:
                fontCount++;
                fontMemory += GetFontMemorySize(*(Font*)manager->resources[i]->data);
                break;
            default:
                otherCount++;
                // Estimate other resource memory usage
                break;
        }
    }
    
    printf("Resource Stats:\n");
    printf("  Textures: %d (%.2f MB)\n", textureCount, textureMemory / (1024.0f * 1024.0f));
    printf("  Sounds: %d (%.2f MB)\n", soundCount, soundMemory / (1024.0f * 1024.0f));
    printf("  Fonts: %d (%.2f MB)\n", fontCount, fontMemory / (1024.0f * 1024.0f));
    printf("  Other: %d (%.2f MB)\n", otherCount, otherMemory / (1024.0f * 1024.0f));
    printf("  Total: %d (%.2f MB)\n", manager->count, 
           (textureMemory + soundMemory + fontMemory + otherMemory) / (1024.0f * 1024.0f));
}
``` 