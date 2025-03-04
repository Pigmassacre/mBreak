# Core Engine Systems

This document details the core engine systems that power the game, focusing on the technical infrastructure rather than gameplay mechanics.

## Initialization System

### Main Initialization (mBreak.py)
```c
// Main initialization function
void InitGame(void) {
    // Initialize raylib
    InitWindow(SCREEN_WIDTH, SCREEN_HEIGHT, WINDOW_CAPTION);
    
    // Initialize audio
    InitAudioDevice();
    
    // Load settings
    LoadSettings();
    LoadGraphicsSettings();
    
    // Set display modes
    if (FULLSCREEN) {
        ToggleFullscreen();
        SetWindowState(FLAG_WINDOW_RESIZABLE);
    }
    
    // Initialize camera
    Camera2D camera = { 0 };
    camera.target = (Vector2){ 0, 0 };
    camera.offset = (Vector2){ 0, 0 };
    camera.rotation = 0.0f;
    camera.zoom = 1.0f;
    
    // Initialize joysticks
    for (int i = 0; i < GetGamepadCount(); i++) {
        // Initialize each gamepad
    }
    
    // Start with splash screen
    SetGameScreen(SCREEN_SPLASH);
}
```

### Current Implementation Details
- Pygame initialization with `pygame.init()`
- Clock creation with `gameclock.GameClock()`
- Settings loaded from `settings.txt`
- Display mode setup with double buffering and hardware acceleration
- Window surface creation with `pygame.display.set_mode()`
- Camera initialization
- Joystick initialization and enumeration
- Event filtering to only process relevant events
- Window caption setup
- Splash screen launch

### Port Considerations
- Replace Pygame initialization with Raylib's `InitWindow()` and `InitAudioDevice()`
- Use Raylib's timing functions instead of Pygame's clock
- Implement settings loading function for `settings.txt`
- Set up Raylib window with appropriate flags
- Create a Camera2D for the viewport
- Use Raylib's gamepad functions for controller support
- Create a screen state management system

## Game Clock System

### Game Clock Implementation
```c
typedef struct GameClock {
    double last_tick;
    double time_passed;
    double delta_time;
    float game_speed;
    bool paused;
} GameClock;

GameClock CreateGameClock(void) {
    GameClock clock = {
        .last_tick = GetTime(),
        .time_passed = 0.0,
        .delta_time = 0.0,
        .game_speed = 1.0f,
        .paused = false
    };
    return clock;
}

void UpdateGameClock(GameClock *clock) {
    double current_time = GetTime();
    clock->delta_time = current_time - clock->last_tick;
    clock->last_tick = current_time;
    
    if (!clock->paused) {
        clock->time_passed += clock->delta_time * clock->game_speed;
    }
}

double GetGameTime(GameClock *clock) {
    return clock->time_passed;
}

double GetDeltaTime(GameClock *clock) {
    return clock->delta_time;
}

void SetGameSpeed(GameClock *clock, float speed) {
    clock->game_speed = speed;
}

void PauseGameClock(GameClock *clock) {
    clock->paused = true;
}

void ResumeGameClock(GameClock *clock) {
    clock->paused = false;
}
```

### Current Implementation Details
- Custom `GameClock` class in `objects/gameclock.py`
- Tracks time between updates
- Supports game speed modification
- Handles pausing
- Returns ticks and delta time for frame-rate independent movement

### Port Considerations
- Use Raylib's timing functions (`GetTime()`, `GetFrameTime()`)
- Create a similar struct for time management
- Ensure consistent timing behavior across platforms
- Maintain support for speed modification and pausing

## Camera System

### Camera Implementation
```c
typedef struct GameCamera {
    Camera2D camera;
    Rectangle bounds;
    Vector2 target;
    float zoom;
    bool follow_target;
} GameCamera;

GameCamera CreateCamera(float x, float y, float width, float height) {
    GameCamera game_camera = {
        .camera = {
            .offset = { SCREEN_WIDTH/2.0f, SCREEN_HEIGHT/2.0f },
            .target = { x + width/2.0f, y + height/2.0f },
            .rotation = 0.0f,
            .zoom = 1.0f
        },
        .bounds = { x, y, width, height },
        .target = { x + width/2.0f, y + height/2.0f },
        .zoom = 1.0f,
        .follow_target = false
    };
    return game_camera;
}

void UpdateCamera(GameCamera *camera) {
    if (camera->follow_target) {
        camera->camera.target = camera->target;
    }
}

void SetCameraTarget(GameCamera *camera, Vector2 target) {
    camera->target = target;
}

void SetCameraPosition(GameCamera *camera, float x, float y) {
    camera->camera.target = (Vector2){ x, y };
}

void BeginCameraMode(GameCamera *camera) {
    BeginMode2D(camera->camera);
}

void EndCameraMode(void) {
    EndMode2D();
}
```

### Current Implementation Details
- Simple camera system in `objects/camera.py`
- Provides a viewport offset for rendering
- Supports level boundary tracking
- Used for positioning rendered elements

### Port Considerations
- Replace with Raylib's Camera2D system
- Implement a wrapper to maintain the existing functionality
- Add support for camera transitions and effects
- Ensure proper scaling and resolution handling

## Settings System

### Settings Implementation
```c
typedef struct GameSettings {
    // Display settings
    int screen_width;
    int screen_height;
    int level_width;
    int level_height;
    bool fullscreen;
    char window_caption[64];
    
    // Game settings
    int game_fps;
    float sound_volume;
    float music_volume;
    bool debug_mode;
    
    // Control settings
    KeyboardKey player1_up;
    KeyboardKey player1_down;
    KeyboardKey player1_action;
    // ... more controls
} GameSettings;

bool LoadSettings(void) {
    GameSettings settings = { 0 };
    
    // Default values
    settings.screen_width = 900;
    settings.screen_height = 500;
    settings.level_width = 900;
    settings.level_height = 500;
    settings.fullscreen = false;
    strcpy(settings.window_caption, "mBreak");
    settings.game_fps = 60;
    settings.sound_volume = 1.0f;
    settings.music_volume = 0.5f;
    settings.debug_mode = false;
    
    // Load from file
    FILE *file = fopen("settings.txt", "r");
    if (file == NULL) {
        TraceLog(LOG_WARNING, "Failed to open settings file, using defaults");
        return false;
    }
    
    // Parse settings file
    char line[256];
    while (fgets(line, sizeof(line), file)) {
        // Parse line and update settings
        // ...
    }
    
    fclose(file);
    return true;
}

bool SaveSettings(void) {
    // Save settings to file
    // ...
}
```

### Current Implementation Details
- Settings stored in text file (`settings.txt`)
- Two modules:
  - `settings/settings.py`: Core game settings
  - `settings/graphics.py`: Graphics-specific settings
- Support for fullscreen toggle, resolution, sound volume, etc.
- Default values provided for missing settings

### Port Considerations
- Create a structured settings system
- Implement text file parsing
- Support runtime modification and saving
- Separate graphics settings from gameplay settings

## Resource Management

### Resource Management Implementation
```c
typedef struct GameResources {
    // Textures
    Texture2D ballTexture;
    Texture2D paddleTopTexture;
    Texture2D paddleMiddleTexture;
    Texture2D paddleBottomTexture;
    Texture2D blockTexture;
    // ... more textures
    
    // Fonts
    Font mainFont;
    Font titleFont;
    
    // Sounds
    Sound ballHitSound;
    Sound explosionSound;
    Sound powerupSound[3]; // Array for multiple variants
    // ... more sounds
    
    // Music
    Music backgroundMusic;
} GameResources;

GameResources LoadGameResources(void) {
    GameResources resources = { 0 };
    
    // Load textures
    resources.ballTexture = LoadTexture("res/ball/ball.png");
    resources.paddleTopTexture = LoadTexture("res/paddle/paddle_top.png");
    resources.paddleMiddleTexture = LoadTexture("res/paddle/paddle_middle.png");
    resources.paddleBottomTexture = LoadTexture("res/paddle/paddle_bottom.png");
    resources.blockTexture = LoadTexture("res/block/block.png");
    // ... load more textures
    
    // Load fonts
    resources.mainFont = LoadFont("fonts/main_font.ttf");
    resources.titleFont = LoadFont("fonts/title_font.ttf");
    
    // Load sounds
    resources.ballHitSound = LoadSound("res/sounds/ball_hit.wav");
    resources.explosionSound = LoadSound("res/sounds/explosion.wav");
    resources.powerupSound[0] = LoadSound("res/sounds/powerup1.wav");
    resources.powerupSound[1] = LoadSound("res/sounds/powerup2.wav");
    resources.powerupSound[2] = LoadSound("res/sounds/powerup3.wav");
    // ... load more sounds
    
    // Load music
    resources.backgroundMusic = LoadMusicStream("res/music/background.ogg");
    
    return resources;
}

void UnloadGameResources(GameResources resources) {
    // Unload textures
    UnloadTexture(resources.ballTexture);
    UnloadTexture(resources.paddleTopTexture);
    UnloadTexture(resources.paddleMiddleTexture);
    UnloadTexture(resources.paddleBottomTexture);
    UnloadTexture(resources.blockTexture);
    // ... unload more textures
    
    // Unload fonts
    UnloadFont(resources.mainFont);
    UnloadFont(resources.titleFont);
    
    // Unload sounds
    UnloadSound(resources.ballHitSound);
    UnloadSound(resources.explosionSound);
    for (int i = 0; i < 3; i++) {
        UnloadSound(resources.powerupSound[i]);
    }
    // ... unload more sounds
    
    // Unload music
    UnloadMusicStream(resources.backgroundMusic);
}
```

### Current Implementation Details
- Resources loaded directly in each class (sprite, sound, etc.)
- Static image loading within class definitions
- Sound initialization in individual classes
- Minimal resource caching

### Port Considerations
- Centralize resource loading to prevent duplication
- Implement proper resource unloading
- Create a robust asset management system
- Add support for resource caching and reuse
- Handle errors gracefully if resources are missing

## Game Loop

### Game Loop Implementation
```c
void GameLoop(void) {
    // Initialize
    InitGame();
    
    // Load resources
    GameResources resources = LoadGameResources();
    
    // Create game clock
    GameClock clock = CreateGameClock();
    
    // Main game loop
    while (!WindowShouldClose()) {
        // Update game clock
        UpdateGameClock(&clock);
        
        // Update current screen
        UpdateCurrentScreen(&clock);
        
        // Draw
        BeginDrawing();
        ClearBackground(BLACK);
        
        // Draw current screen
        DrawCurrentScreen();
        
        EndDrawing();
    }
    
    // Cleanup
    UnloadGameResources(resources);
    CloseWindow();
}
```

### Current Implementation Details
- Main loop handled in each screen object
- Screens take control of the game flow
- Update and draw steps separated
- Clock object passed to update methods
- Transitions handled by screens

### Port Considerations
- Implement a screen stack or state machine for managing game states
- Separate update and draw logic clearly
- Maintain consistent frame timing
- Handle window events and exit conditions
- Implement clean shutdown and resource cleanup

## Event Handling System

### Event Handling Implementation
```c
typedef enum {
    INPUT_NONE,
    INPUT_UP,
    INPUT_DOWN,
    INPUT_LEFT,
    INPUT_RIGHT,
    INPUT_ACTION,
    INPUT_BACK,
    INPUT_START,
    INPUT_QUIT
} InputType;

typedef struct {
    bool keys[INPUT_COUNT];
    bool keysPressed[INPUT_COUNT];
    bool keysReleased[INPUT_COUNT];
    Vector2 mousePosition;
    bool mouseLeftPressed;
    bool mouseLeftReleased;
    bool mouseRightPressed;
    bool mouseRightReleased;
} InputState;

InputState UpdateInput(void) {
    InputState state = { 0 };
    
    // Keyboard
    state.keys[INPUT_UP] = IsKeyDown(KEY_UP) || IsKeyDown(KEY_W);
    state.keys[INPUT_DOWN] = IsKeyDown(KEY_DOWN) || IsKeyDown(KEY_S);
    state.keys[INPUT_LEFT] = IsKeyDown(KEY_LEFT) || IsKeyDown(KEY_A);
    state.keys[INPUT_RIGHT] = IsKeyDown(KEY_RIGHT) || IsKeyDown(KEY_D);
    state.keys[INPUT_ACTION] = IsKeyDown(KEY_SPACE) || IsKeyDown(KEY_ENTER);
    state.keys[INPUT_BACK] = IsKeyDown(KEY_ESCAPE) || IsKeyDown(KEY_BACKSPACE);
    state.keys[INPUT_START] = IsKeyDown(KEY_ENTER);
    state.keys[INPUT_QUIT] = WindowShouldClose();
    
    state.keysPressed[INPUT_UP] = IsKeyPressed(KEY_UP) || IsKeyPressed(KEY_W);
    state.keysPressed[INPUT_DOWN] = IsKeyPressed(KEY_DOWN) || IsKeyPressed(KEY_S);
    // ... same for other keys
    
    state.keysReleased[INPUT_UP] = IsKeyReleased(KEY_UP) || IsKeyReleased(KEY_W);
    state.keysReleased[INPUT_DOWN] = IsKeyReleased(KEY_DOWN) || IsKeyReleased(KEY_S);
    // ... same for other keys
    
    // Mouse
    state.mousePosition = GetMousePosition();
    state.mouseLeftPressed = IsMouseButtonPressed(MOUSE_LEFT_BUTTON);
    state.mouseLeftReleased = IsMouseButtonReleased(MOUSE_LEFT_BUTTON);
    state.mouseRightPressed = IsMouseButtonPressed(MOUSE_RIGHT_BUTTON);
    state.mouseRightReleased = IsMouseButtonReleased(MOUSE_RIGHT_BUTTON);
    
    // Gamepad (can be added based on current implementation)
    
    return state;
}
```

### Current Implementation Details
- Pygame event system with `pygame.event.get()`
- Focus on keyboard and joystick inputs
- Event filtering to limit processed events
- Specific handling for QUIT, KEYDOWN, KEYUP, etc.
- Controls managed per-player

### Port Considerations
- Create an abstraction layer for inputs
- Map Pygame event handling to Raylib's input functions
- Maintain support for keyboard, mouse, and gamepad
- Implement configurable controls
- Add support for multiple control schemes

## Debug System

### Debug Implementation
```c
typedef struct DebugSystem {
    bool enabled;
    Font debugFont;
    int frameCounter;
    float frameTime;
    float fps;
    int drawCalls;
    int entityCount;
} DebugSystem;

DebugSystem CreateDebugSystem(void) {
    DebugSystem debug = {
        .enabled = false,
        .debugFont = GetFontDefault(),
        .frameCounter = 0,
        .frameTime = 0.0f,
        .fps = 0.0f,
        .drawCalls = 0,
        .entityCount = 0
    };
    return debug;
}

void UpdateDebugInfo(DebugSystem *debug) {
    if (!debug->enabled) return;
    
    debug->frameCounter++;
    debug->frameTime = GetFrameTime();
    
    // Update FPS counter once per second
    static float fpsUpdateTime = 0.0f;
    fpsUpdateTime += debug->frameTime;
    if (fpsUpdateTime >= 1.0f) {
        debug->fps = debug->frameCounter;
        debug->frameCounter = 0;
        fpsUpdateTime = 0.0f;
    }
    
    // Update entity count
    // This would be updated from game systems
}

void DrawDebugInfo(DebugSystem *debug) {
    if (!debug->enabled) return;
    
    // Save drawing state to not affect game rendering
    Color savedColor = WHITE;  // GetFontColor();
    
    // Draw debug overlay
    DrawText(TextFormat("FPS: %0.1f", debug->fps), 10, 10, 20, GREEN);
    DrawText(TextFormat("Frame Time: %0.4f ms", debug->frameTime * 1000.0f), 10, 35, 20, GREEN);
    DrawText(TextFormat("Entities: %d", debug->entityCount), 10, 60, 20, GREEN);
    DrawText(TextFormat("Draw Calls: %d", debug->drawCalls), 10, 85, 20, GREEN);
    
    // Additional debug rendering for hitboxes, paths, etc. would go here
    
    // Restore drawing state
    // SetFontColor(savedColor);
}

void ToggleDebugMode(DebugSystem *debug) {
    debug->enabled = !debug->enabled;
}
```

### Current Implementation Details
- Basic debug mode toggle via settings
- Debug visualization for certain components
- Performance metrics not clearly implemented
- Some debug messages to console

### Port Considerations
- Implement a comprehensive debug overlay
- Add frame rate and performance metrics
- Add visualization for colliders and physics
- Add logging system
- Make debug views togglable at runtime

This specification details the core engine systems required for the C + Raylib port, based on the current Python implementation. Each system is described with its purpose, structure, and key considerations for porting. 