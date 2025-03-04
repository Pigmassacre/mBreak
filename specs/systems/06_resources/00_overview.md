# Resource System Overview

## Directory Structure

### Core Resource Types
```c
typedef enum ResourceType {
    RES_TEXTURE,
    RES_SOUND,
    RES_MUSIC,
    RES_FONT,
    RES_SHADER,
    RES_DATA
} ResourceType;
```

### Resource Paths
```c
typedef struct ResourcePaths {
    // Base paths
    const char* texturesPath;
    const char* soundsPath;
    const char* musicPath;
    const char* fontsPath;
    const char* shadersPath;
    const char* dataPath;
    
    // Asset packs
    const char* uiAssets;
    const char* gameAssets;
    const char* effectsAssets;
} ResourcePaths;
```

## Resource Categories

### Textures
```c
typedef struct TextureResource {
    // Core properties
    const char* id;
    const char* path;
    bool isLoaded;
    
    // Texture data
    Texture2D texture;
    Rectangle source;
    Vector2 origin;
    
    // Animation
    bool isAnimated;
    int frameCount;
    float frameTime;
    
    // Atlas data
    bool isAtlas;
    AtlasRegion* regions;
    int regionCount;
} TextureResource;
```

### Audio
```c
typedef struct AudioResource {
    // Core properties
    const char* id;
    const char* path;
    bool isLoaded;
    
    // Audio data
    union {
        Sound sound;
        Music music;
    } audio;
    
    // Properties
    float duration;
    float volume;
    bool isStreamed;
    bool isLooped;
} AudioResource;
```

### Fonts
```c
typedef struct FontResource {
    // Core properties
    const char* id;
    const char* path;
    bool isLoaded;
    
    // Font data
    Font font;
    float baseSize;
    
    // Glyph info
    GlyphInfo* glyphs;
    int glyphCount;
    
    // Cache
    bool useCache;
    FontCache* cache;
} FontResource;
```

### Shaders
```c
typedef struct ShaderResource {
    // Core properties
    const char* id;
    const char* path;
    bool isLoaded;
    
    // Shader data
    Shader shader;
    
    // Uniforms
    UniformInfo* uniforms;
    int uniformCount;
    
    // Attributes
    AttributeInfo* attributes;
    int attributeCount;
} ShaderResource;
```

## Resource Loading

### Load Pipeline
```c
void LoadResource(const char* id, ResourceType type) {
    // Check if already loaded
    if (IsResourceLoaded(id)) {
        return;
    }
    
    // Get resource path
    const char* path = GetResourcePath(id, type);
    
    // Load based on type
    switch (type) {
        case RES_TEXTURE:
            LoadTextureResource(id, path);
            break;
        case RES_SOUND:
            LoadSoundResource(id, path);
            break;
        case RES_MUSIC:
            LoadMusicResource(id, path);
            break;
        case RES_FONT:
            LoadFontResource(id, path);
            break;
        case RES_SHADER:
            LoadShaderResource(id, path);
            break;
        case RES_DATA:
            LoadDataResource(id, path);
            break;
    }
}
```

### Resource Packing
```c
void PackResources(const char* packFile) {
    // Create resource pack
    ResourcePack pack;
    InitResourcePack(&pack);
    
    // Add resources
    AddTexturesToPack(&pack);
    AddSoundsToPack(&pack);
    AddMusicToPack(&pack);
    AddFontsToPack(&pack);
    AddShadersToPack(&pack);
    AddDataToPack(&pack);
    
    // Write pack file
    WriteResourcePack(&pack, packFile);
}
```

## Resource Management

### Resource Cache
```c
typedef struct ResourceCache {
    // Cache entries
    struct {
        const char* id;
        ResourceType type;
        void* data;
        size_t size;
        time_t lastUsed;
    }* entries;
    
    int count;
    int capacity;
    
    // Memory limits
    size_t currentSize;
    size_t maxSize;
} ResourceCache;
```

### Resource Streaming
```c
void StreamResources() {
    // Check memory usage
    if (IsMemoryLow()) {
        // Unload unused resources
        UnloadUnusedResources();
    }
    
    // Stream high priority resources
    StreamHighPriorityResources();
    
    // Queue low priority resources
    QueueLowPriorityResources();
}
```

## Debug Features

### Resource Monitor
```c
void MonitorResources() {
    // Track memory usage
    TrackResourceMemory();
    
    // Monitor load times
    TrackLoadTimes();
    
    // Check resource states
    CheckResourceStates();
    
    // Generate report
    GenerateResourceReport();
}
```

### Debug Visualization
```c
void DrawResourceDebug() {
    // Draw memory usage
    DrawMemoryUsage();
    
    // Draw resource counts
    DrawResourceCounts();
    
    // Draw load queue
    DrawLoadQueue();
    
    // Draw cache info
    DrawCacheInfo();
}
``` 