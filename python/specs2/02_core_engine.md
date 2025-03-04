# Core Engine Systems

This document details the core engine systems that power the game, focusing on the technical infrastructure rather than gameplay mechanics. Each section describes the current Python/Pygame implementation followed by considerations for porting to C/Raylib.

## Initialization System

### Current Implementation Details
- Pygame initialization with `pygame.init()`
- Clock creation with `gameclock.GameClock()`
- Settings loaded from `settings.txt` via separate modules:
  - `settings/settings.py`: Core game settings
  - `settings/graphics.py`: Graphics-specific settings
- Display mode setup with double buffering and hardware acceleration flags
- Window surface creation with `pygame.display.set_mode()`
- Camera initialization via `camera.create_camera()`
- Joystick initialization and enumeration
- Event filtering with `pygame.event.set_allowed()`
- Window caption setup
- Splash screen launch as first game state

### Port Considerations (C/Raylib)
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

## Game Clock System

### Current Implementation Details
- Simple clock wrapper in `objects/gameclock.py` around Pygame's time functionality
- Tracks time between frames with `delta_time` property
- Supports game speed modification via `time_scale` property
- Provides methods for getting frame time and FPS
- Used for frame-rate independent movement via `delta_time`
- No explicit pause functionality in the current implementation (just time scale manipulation)

### Port Considerations (C/Raylib)
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

double GetDeltaTime(GameClock *clock) {
    return clock->delta_time;
}

void SetGameSpeed(GameClock *clock, float speed) {
    clock->game_speed = speed;
}

// Add pause functionality for the port
void PauseGameClock(GameClock *clock) {
    clock->paused = true;
}

void ResumeGameClock(GameClock *clock) {
    clock->paused = false;
}
```

## Camera System

### Current Implementation Details
- Simple camera system in `objects/camera.py`
- Global camera instance created via `create_camera()` function
- Stores view position (x, y) and boundaries (width, height)
- Supports camera shake effect through `CameraShake` class
- Camera shake has duration and intensity parameters
- No explicit zoom or rotation functionality in current implementation
- Used to calculate view offsets when drawing game elements

### Port Considerations (C/Raylib)
```c
typedef struct GameCamera {
    Camera2D camera;
    Rectangle bounds;
    Vector2 target;
    float zoom;
    bool follow_target;
    
    // Camera shake properties
    float shake_intensity;
    float shake_duration;
    float shake_time_left;
    bool is_shaking;
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
        .follow_target = false,
        .shake_intensity = 0.0f,
        .shake_duration = 0.0f,
        .shake_time_left = 0.0f,
        .is_shaking = false
    };
    return game_camera;
}

void UpdateCamera(GameCamera *camera, float delta_time) {
    if (camera->follow_target) {
        camera->camera.target = camera->target;
    }
    
    // Update camera shake
    if (camera->is_shaking) {
        camera->shake_time_left -= delta_time;
        
        if (camera->shake_time_left > 0) {
            // Apply random shake offset
            camera->camera.target.x += GetRandomValue(-100, 100) / 100.0f * camera->shake_intensity;
            camera->camera.target.y += GetRandomValue(-100, 100) / 100.0f * camera->shake_intensity;
        } else {
            camera->is_shaking = false;
        }
    }
}

void ShakeCamera(GameCamera *camera, float duration, float intensity) {
    camera->shake_intensity = intensity;
    camera->shake_duration = duration;
    camera->shake_time_left = duration;
    camera->is_shaking = true;
}

void BeginCameraMode(GameCamera *camera) {
    BeginMode2D(camera->camera);
}

void EndCameraMode(void) {
    EndMode2D();
}
```

## Settings System

### Current Implementation Details
- Settings stored in plain text file (`settings.txt`)
- Two separate modules for settings management:
  - `settings/settings.py`: Core game settings (player names, level dimensions, audio volumes, etc.)
  - `settings/graphics.py`: Graphics-specific settings (shadows, particles, fullscreen, etc.)
- Default values provided for missing settings
- Settings loaded at startup and can be saved back to file
- Simple format with key-value pairs (e.g., "debugmode 0")
- No error checking for invalid values

### Port Considerations (C/Raylib)
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
    
    // Graphics settings
    bool shadows;
    bool particles;
    bool flashes;
    bool traces;
    bool background;
    int max_fps;
    bool trajectory;
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
    
    // Graphics defaults
    settings.shadows = true;
    settings.particles = true;
    settings.flashes = true;
    settings.traces = true;
    settings.background = true;
    settings.max_fps = 60;
    settings.trajectory = true;
    
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
    return true;
}
```

## Resource Management

### Current Implementation Details
- No centralized resource management system in current implementation
- Resources loaded directly in each class that needs them
- Images loaded with `pygame.image.load()` within class definition or initialization
- Sound initialization in individual classes
- No explicit resource unloading or caching

### Port Considerations (C/Raylib)
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
    Music backgroundMusic[10]; // Array for multiple tracks
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
    resources.backgroundMusic[0] = LoadMusicStream("res/music/background.ogg");
    // ... load more music tracks
    
    return resources;
}

void UnloadGameResources(GameResources resources) {
    // Unload textures, fonts, sounds, and music
    // ...
}
```

## Game Loop and Screen Management

### Current Implementation Details
- Main loop handled in the base `Scene` class in `screens/scene.py`
- All screens inherit from the Scene class
- Each screen takes full control of the game flow during its execution
- Update and draw steps separated into methods
- Clock object passed to update methods
- Transitions between screens handled by direct function calls in the `on_exit()` method
- Each scene creates and starts the next scene when transitioning
- Pygame events handled in the main loop and passed to screen's event handler
- Music is managed within the screen class with auto-restart when a track ends

### Port Considerations (C/Raylib)
```c
// Screen states enumeration
typedef enum {
    SCREEN_SPLASH,
    SCREEN_TITLE,
    SCREEN_GAMEPLAY,
    SCREEN_PAUSE,
    SCREEN_ENDING,
    // ... more screens
} GameScreen;

// Global state
GameScreen currentScreen = SCREEN_SPLASH;
GameScreen nextScreen = SCREEN_SPLASH;
bool transitioning = false;

void UpdateCurrentScreen(GameClock *clock) {
    switch (currentScreen) {
        case SCREEN_SPLASH:
            UpdateSplashScreen(clock);
            break;
        case SCREEN_TITLE:
            UpdateTitleScreen(clock);
            break;
        // ... update more screens
    }
    
    // Check for screen transitions
    if (nextScreen != currentScreen && !transitioning) {
        StartTransition(currentScreen, nextScreen);
        transitioning = true;
    }
    
    // Update transition if active
    if (transitioning) {
        if (UpdateTransition()) {
            currentScreen = nextScreen;
            transitioning = false;
        }
    }
}

void DrawCurrentScreen(void) {
    switch (currentScreen) {
        case SCREEN_SPLASH:
            DrawSplashScreen();
            break;
        case SCREEN_TITLE:
            DrawTitleScreen();
            break;
        // ... draw more screens
    }
    
    // Draw transition if active
    if (transitioning) {
        DrawTransition();
    }
}

void SetGameScreen(GameScreen screen) {
    nextScreen = screen;
}

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

## Event Handling System

### Current Implementation Details
- Pygame event system used directly with `pygame.event.get()`
- Focus on keyboard and joystick inputs
- Event filtering with `pygame.event.set_allowed()` to limit processed events
- Events processed in the main loop and passed to screen's event handler
- Specific handling for QUIT, KEYDOWN, KEYUP, joystick events
- Player controls managed via key constants in settings (e.g., `PLAYER_ONE_KEY_UP`)
- Menu traversal handled by a separate module (`gui.traversal`)

### Port Considerations (C/Raylib)
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
    
    // Gamepad handling for multiple controllers
    // ...
    
    return state;
}
```

## Music System

### Current Implementation Details
- Music handled in the base Scene class
- Each screen defines a music_list with paths to music files
- Random track selection from the list
- Pygame mixer used for music playback
- End-of-track detection with custom event (MUSIC_EVENT)
- Auto-restart of music when track ends
- Volume control via settings

### Port Considerations (C/Raylib)
```c
typedef struct MusicSystem {
    Music* tracks;
    int trackCount;
    int currentTrack;
    bool isPlaying;
    float volume;
} MusicSystem;

MusicSystem CreateMusicSystem(void) {
    MusicSystem system = {
        .tracks = NULL,
        .trackCount = 0,
        .currentTrack = -1,
        .isPlaying = false,
        .volume = 1.0f
    };
    return system;
}

void LoadMusicForScreen(MusicSystem* system, GameScreen screen) {
    // Unload any existing music
    UnloadMusicTracks(system);
    
    // Load tracks based on screen
    switch (screen) {
        case SCREEN_TITLE:
            system->trackCount = 3;
            system->tracks = (Music*)MemAlloc(sizeof(Music) * system->trackCount);
            system->tracks[0] = LoadMusicStream("res/music/title/track1.ogg");
            system->tracks[1] = LoadMusicStream("res/music/title/track2.ogg");
            system->tracks[2] = LoadMusicStream("res/music/title/track3.ogg");
            break;
            
        case SCREEN_GAMEPLAY:
            // Load gameplay music
            break;
            
        // ... other screens
    }
    
    // Set volume for all tracks
    for (int i = 0; i < system->trackCount; i++) {
        SetMusicVolume(system->tracks[i], system->volume);
    }
}

void PlayRandomTrack(MusicSystem* system) {
    if (system->trackCount <= 0) return;
    
    system->currentTrack = GetRandomValue(0, system->trackCount - 1);
    PlayMusicStream(system->tracks[system->currentTrack]);
    system->isPlaying = true;
}

void UpdateMusicSystem(MusicSystem* system) {
    if (!system->isPlaying || system->currentTrack < 0) return;
    
    // Update current music stream
    UpdateMusicStream(system->tracks[system->currentTrack]);
    
    // Check if music has ended
    if (!IsMusicStreamPlaying(system->tracks[system->currentTrack])) {
        PlayRandomTrack(system);
    }
}

void SetMusicVolume(MusicSystem* system, float volume) {
    system->volume = volume;
    
    if (system->currentTrack >= 0) {
        SetMusicVolume(system->tracks[system->currentTrack], volume);
    }
}

void UnloadMusicTracks(MusicSystem* system) {
    if (system->tracks) {
        for (int i = 0; i < system->trackCount; i++) {
            UnloadMusicStream(system->tracks[i]);
        }
        MemFree(system->tracks);
        system->tracks = NULL;
        system->trackCount = 0;
        system->currentTrack = -1;
        system->isPlaying = false;
    }
}
```

## Transition System

### Current Implementation Details
- Transition effects handled by `transition.Transition` class in `gui/transition.py`
- Used for smooth transitions between scenes
- Each scene has its own transition object
- Simple fade-in/fade-out effects

### Port Considerations (C/Raylib)
```c
typedef enum {
    TRANSITION_NONE,
    TRANSITION_FADE,
    TRANSITION_SLIDE,
    // ... other transition effects
} TransitionType;

typedef struct {
    TransitionType type;
    float alpha;
    float time;
    float duration;
    bool active;
    Color color;
    bool fadeOut;
} Transition;

Transition CreateTransition(void) {
    Transition transition = {
        .type = TRANSITION_FADE,
        .alpha = 0.0f,
        .time = 0.0f,
        .duration = 1.0f,
        .active = false,
        .color = BLACK,
        .fadeOut = false
    };
    return transition;
}

void StartTransition(Transition* transition, float duration, bool fadeOut) {
    transition->duration = duration;
    transition->time = 0.0f;
    transition->active = true;
    transition->fadeOut = fadeOut;
    transition->alpha = fadeOut ? 0.0f : 1.0f;
}

bool UpdateTransition(Transition* transition, float deltaTime) {
    if (!transition->active) return false;
    
    transition->time += deltaTime;
    
    if (transition->fadeOut) {
        transition->alpha = transition->time / transition->duration;
    } else {
        transition->alpha = 1.0f - (transition->time / transition->duration);
    }
    
    // Clamp alpha
    if (transition->alpha < 0.0f) transition->alpha = 0.0f;
    if (transition->alpha > 1.0f) transition->alpha = 1.0f;
    
    // Check if transition is complete
    if (transition->time >= transition->duration) {
        transition->active = false;
        return true;
    }
    
    return false;
}

void DrawTransition(Transition* transition) {
    if (!transition->active) return;
    
    switch (transition->type) {
        case TRANSITION_FADE:
            {
                Color color = transition->color;
                color.a = (unsigned char)(transition->alpha * 255.0f);
                DrawRectangle(0, 0, GetScreenWidth(), GetScreenHeight(), color);
            }
            break;
            
        // ... other transition types
    }
}
```

## Debug System

### Current Implementation Details
- Basic debug mode toggle via settings (`DEBUG_MODE` in settings.py)
- Debug class in `other/debug.py` with FPS display
- Debug key commands for spawning balls, powerups, time scale changes
- Simple text overlay in top-left corner
- No comprehensive performance metrics
- Debug mode enabled through settings.txt

### Port Considerations (C/Raylib)
```c
typedef struct DebugSystem {
    bool enabled;
    Font debugFont;
    int frameCounter;
    float frameTime;
    float fps;
    int entityCount;
} DebugSystem;

DebugSystem CreateDebugSystem(void) {
    DebugSystem debug = {
        .enabled = false,
        .debugFont = GetFontDefault(),
        .frameCounter = 0,
        .frameTime = 0.0f,
        .fps = 0.0f,
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
    
    // Track entities (enhanced feature for the port)
    // This would be updated from game systems
}

void DrawDebugInfo(DebugSystem *debug) {
    if (!debug->enabled) return;
    
    // Draw FPS counter (matches current implementation)
    DrawText(TextFormat("FPS: %0.1f", debug->fps), 10, 10, 20, GREEN);
    
    // Enhanced debug displays for the port
    DrawText(TextFormat("Frame Time: %0.4f ms", debug->frameTime * 1000.0f), 10, 35, 20, GREEN);
    DrawText(TextFormat("Entities: %d", debug->entityCount), 10, 60, 20, GREEN);
    
    // Additional debug commands help
    DrawText("Debug Controls:", 10, GetScreenHeight() - 100, 15, YELLOW);
    DrawText("P: Spawn powerup | N/M: Create ball | T: Change timescale", 10, GetScreenHeight() - 80, 13, YELLOW);
}

void ToggleDebugMode(DebugSystem *debug) {
    debug->enabled = !debug->enabled;
}

// Debug keyboard handling (similar to current implementation)
void HandleDebugKeys(void) {
    if (IsKeyPressed(KEY_P)) {
        // Spawn random powerup
    }
    
    if (IsKeyPressed(KEY_T)) {
        // Change time scale
    }
    
    // ... other debug commands
}
```

This specification details both the current Python/Pygame implementation and the proposed C/Raylib port considerations for each core engine system. The port considerations build upon the current implementation while suggesting improvements and adaptations to take advantage of Raylib's features. 