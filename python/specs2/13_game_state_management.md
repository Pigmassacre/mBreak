# Game State Management System Specification

## Overview

The Game State Management System is responsible for controlling the flow of the game by managing different states (screens) and the transitions between them. It provides a structured framework for handling various game phases such as splash screens, menus, gameplay, pause states, and game over screens.

This specification outlines the design and implementation of the Game State Management System for the C/Raylib port, translating the existing Python/Pygame scene-based approach while enhancing it with additional features and optimizations possible in C and Raylib.

## Core Architecture

The Game State Management System is built around a state machine pattern with the following key components:

1. **State Manager**: Central controller that manages state transitions and updates
2. **Game States**: Individual screens or modes with specific behaviors
3. **Transition System**: Handles smooth visual transitions between states
4. **State Stack**: Manages state hierarchy and history

### State Manager Structure

```c
typedef struct StateManager {
    // State tracking
    GameState** states;              // Array of all registered states
    int state_count;                 // Number of registered states
    int state_capacity;              // Maximum number of states
    
    // State stack (for hierarchical states)
    GameState** state_stack;         // Stack of active states (for overlays/popups)
    int stack_size;                  // Current size of the stack
    int stack_capacity;              // Maximum stack size
    
    // Transition control
    bool transitioning;              // Whether a transition is in progress
    GameState* from_state;           // State transitioning from
    GameState* to_state;             // State transitioning to
    TransitionEffect current_transition; // Current transition effect
    float transition_progress;       // Transition progress (0.0-1.0)
    float transition_duration;       // Total transition duration in seconds
    
    // Global resources
    Sound* global_sounds;            // Sounds available to all states
    Texture2D* global_textures;      // Textures available to all states
    Font* global_fonts;              // Fonts available to all states
    
    // Global game data
    void* global_data;               // Shared data accessible by all states
    
    // Performance monitoring
    float avg_frame_time;            // Moving average of frame time
    float peak_frame_time;           // Peak frame time
    int frame_count;                 // Total frames processed
} StateManager;
```

### Game State Interface

```c
typedef enum GameStateType {
    STATE_SPLASH,                    // Splash/intro screen
    STATE_MAIN_MENU,                 // Main menu
    STATE_OPTIONS,                   // Options/settings menu
    STATE_GAMEPLAY,                  // Main gameplay
    STATE_PAUSE,                     // Pause menu
    STATE_GAME_OVER,                 // Game over screen
    STATE_LEVEL_TRANSITION,          // Level transition
    STATE_CREDITS,                   // Credits screen
    STATE_CUSTOM                     // Custom state type
} GameStateType;

typedef enum GameStateStatus {
    STATUS_INACTIVE,                 // State is not active
    STATUS_ACTIVATING,               // State is being activated
    STATUS_ACTIVE,                   // State is active and updating
    STATUS_DEACTIVATING,             // State is being deactivated
    STATUS_PAUSED,                   // State is paused (not updating but still in stack)
    STATUS_OVERLAY                   // State is an overlay on top of another state
} GameStateStatus;

typedef struct GameState {
    // State identification
    char name[64];                   // State name for debugging and management
    GameStateType type;              // Type of state
    GameStateStatus status;          // Current status of the state
    int state_id;                    // Unique identifier
    
    // State lifecycle methods (function pointers)
    void (*init)(struct GameState* state, void* params);       // Initialize state
    void (*enter)(struct GameState* state, struct GameState* previous_state);  // Called when entering state
    void (*exit)(struct GameState* state, struct GameState* next_state);       // Called when exiting state
    void (*pause)(struct GameState* state);                    // Called when state is paused
    void (*resume)(struct GameState* state);                   // Called when state is resumed
    void (*update)(struct GameState* state, float delta_time); // Update state logic
    void (*draw)(struct GameState* state);                     // Draw state
    void (*handle_input)(struct GameState* state);             // Process input
    void (*cleanup)(struct GameState* state);                  // Free resources
    
    // Resources specific to this state
    void* state_data;                // State-specific data
    
    // Reference to state manager
    StateManager* manager;           // Reference to the state manager
} GameState;
```

### Transition Effect Structure

```c
typedef enum TransitionType {
    TRANSITION_NONE,                 // No transition effect
    TRANSITION_FADE,                 // Simple fade transition
    TRANSITION_SLIDE_LEFT,           // Slide from right to left
    TRANSITION_SLIDE_RIGHT,          // Slide from left to right
    TRANSITION_SLIDE_UP,             // Slide from bottom to top
    TRANSITION_SLIDE_DOWN,           // Slide from top to bottom
    TRANSITION_ZOOM_IN,              // Zoom in transition
    TRANSITION_ZOOM_OUT,             // Zoom out transition
    TRANSITION_RADIAL,               // Radial transition
    TRANSITION_PIXELATE,             // Pixelation effect
    TRANSITION_GRID,                 // Grid-based transition
    TRANSITION_CUSTOM                // Custom transition effect
} TransitionType;

typedef struct TransitionEffect {
    TransitionType type;             // Type of transition
    float duration;                  // Duration in seconds
    bool blocking;                   // If true, states won't update during transition
    RenderTexture2D from_texture;    // Texture for the from state
    RenderTexture2D to_texture;      // Texture for the to state
    Color tint;                      // Tint color for the transition
    void* custom_data;               // Data for custom transitions
    void (*custom_draw)(struct TransitionEffect* effect, float progress); // Custom draw function
} TransitionEffect;
```

## Core Functions

### State Manager Functions

```c
// Initialization and cleanup
StateManager* InitStateManager(int max_states, int max_stack_size);
void DestroyStateManager(StateManager* manager);

// State registration
int RegisterState(StateManager* manager, GameState* state);
GameState* CreateState(StateManager* manager, GameStateType type, const char* name);
void UnregisterState(StateManager* manager, int state_id);

// State transitions
void GotoState(StateManager* manager, int state_id, TransitionType transition_type, float duration);
void PushState(StateManager* manager, int state_id, TransitionType transition_type, float duration);
void PopState(StateManager* manager, TransitionType transition_type, float duration);
void ReplaceState(StateManager* manager, int state_id, TransitionType transition_type, float duration);

// State stack operations
GameState* GetCurrentState(StateManager* manager);
GameState* GetPreviousState(StateManager* manager);
int GetStateStackSize(StateManager* manager);
bool IsStateInStack(StateManager* manager, int state_id);

// Main update loop
void UpdateStateManager(StateManager* manager, float delta_time);
void DrawStateManager(StateManager* manager);
```

### Game State Functions

```c
// Initialize with default behaviors
GameState* InitDefaultState(GameStateType type, const char* name);

// Default implementations that can be overridden
void DefaultStateInit(GameState* state, void* params);
void DefaultStateEnter(GameState* state, GameState* previous_state);
void DefaultStateExit(GameState* state, GameState* next_state);
void DefaultStatePause(GameState* state);
void DefaultStateResume(GameState* state);
void DefaultStateUpdate(GameState* state, float delta_time);
void DefaultStateDraw(GameState* state);
void DefaultStateHandleInput(GameState* state);
void DefaultStateCleanup(GameState* state);

// Helper functions
void SetStateData(GameState* state, void* data);
void* GetStateData(GameState* state);
```

### Transition System Functions

```c
// Create and destroy transitions
TransitionEffect* CreateTransition(TransitionType type, float duration, bool blocking);
void DestroyTransition(TransitionEffect* effect);

// Update and draw transitions
bool UpdateTransition(TransitionEffect* effect, float delta_time);
void DrawTransition(TransitionEffect* effect, float progress);

// Custom transition helpers
void RegisterCustomTransitionEffect(TransitionType custom_id, void (*draw_func)(TransitionEffect*, float));
```

## Game States

### Splash Screen State

```c
typedef struct SplashStateData {
    Texture2D logo;                  // Logo texture
    float display_time;              // How long to display the splash
    float accumulated_time;          // Time accumulated so far
    bool skip_on_input;              // Whether to allow skipping
    int next_state_id;               // ID of next state to transition to
    TransitionType exit_transition;  // Transition to use when exiting
} SplashStateData;

// Specialized functions
void SplashStateInit(GameState* state, void* params);
void SplashStateUpdate(GameState* state, float delta_time);
void SplashStateDraw(GameState* state);
void SplashStateHandleInput(GameState* state);
```

### Main Menu State

```c
typedef struct MainMenuStateData {
    // Menu structure
    Menu* main_menu;                 // Main menu component
    Texture2D background;            // Background texture
    Texture2D logo;                  // Game logo
    
    // Animation
    Vector2 logo_position;           // Current logo position
    Vector2 logo_target_position;    // Target logo position
    float animation_time;            // Time for animations
    
    // State references
    int options_state_id;            // ID of options state
    int game_state_id;               // ID of game state
    int help_state_id;               // ID of help state
} MainMenuStateData;

// Specialized functions
void MainMenuStateInit(GameState* state, void* params);
void MainMenuStateUpdate(GameState* state, float delta_time);
void MainMenuStateDraw(GameState* state);
void MainMenuStateHandleInput(GameState* state);
```

### Game State

```c
typedef struct GameStateData {
    // Game objects
    Level* current_level;            // Current level data
    Player* players[2];              // Player objects
    Camera2D camera;                 // Game camera
    
    // Game state
    int score[2];                    // Player scores
    int round;                       // Current round
    int total_rounds;                // Total rounds to play
    float round_time;                // Time elapsed in current round
    bool game_over;                  // Whether the round is over
    
    // Screens
    CountdownScreen* countdown;      // Countdown before round starts
    
    // References to other states
    int pause_state_id;              // ID of pause state
    int game_over_state_id;          // ID of game over state
} GameStateData;

// Specialized functions
void GameStateInit(GameState* state, void* params);
void GameStateUpdate(GameState* state, float delta_time);
void GameStateDraw(GameState* state);
void GameStateHandleInput(GameState* state);
```

### Pause State

```c
typedef struct PauseStateData {
    Menu* pause_menu;                // Pause menu
    RenderTexture2D game_snapshot;   // Snapshot of the game screen
    bool resume_selected;            // Whether resume is selected
    bool return_to_menu_selected;    // Whether return to menu is selected
    int game_state_id;               // ID of the game state
    int main_menu_state_id;          // ID of main menu state
} PauseStateData;

// Specialized functions
void PauseStateInit(GameState* state, void* params);
void PauseStateEnter(GameState* state, GameState* previous_state);
void PauseStateExit(GameState* state, GameState* next_state);
void PauseStateUpdate(GameState* state, float delta_time);
void PauseStateDraw(GameState* state);
void PauseStateHandleInput(GameState* state);
```

## Visual Transition System

The Visual Transition System provides smooth transitions between game states:

### Pre-defined Transitions

```c
// Fade transition
void FadeTransitionDraw(TransitionEffect* effect, float progress);

// Slide transitions
void SlideLeftTransitionDraw(TransitionEffect* effect, float progress);
void SlideRightTransitionDraw(TransitionEffect* effect, float progress);
void SlideUpTransitionDraw(TransitionEffect* effect, float progress);
void SlideDownTransitionDraw(TransitionEffect* effect, float progress);

// Zoom transitions
void ZoomInTransitionDraw(TransitionEffect* effect, float progress);
void ZoomOutTransitionDraw(TransitionEffect* effect, float progress);

// Grid transition (similar to the existing screen transition)
void GridTransitionDraw(TransitionEffect* effect, float progress);
```

### Custom Transition System

```c
// Register a custom transition
void RegisterCustomTransition(TransitionType custom_id, 
                              void (*draw_func)(TransitionEffect*, float),
                              void* custom_data);

// Create a custom transition
TransitionEffect* CreateCustomTransition(TransitionType custom_id, 
                                        float duration, 
                                        bool blocking,
                                        void* custom_data);
```

## State Data Management

### Global Game Data

```c
// Set and retrieve global data
void SetGlobalData(StateManager* manager, void* data);
void* GetGlobalData(StateManager* manager);

// Helper functions for common data types
void SetGlobalValue(StateManager* manager, const char* key, void* value);
void* GetGlobalValue(StateManager* manager, const char* key);
int GetGlobalIntValue(StateManager* manager, const char* key, int default_value);
float GetGlobalFloatValue(StateManager* manager, const char* key, float default_value);
const char* GetGlobalStringValue(StateManager* manager, const char* key, const char* default_value);
```

### State Data Inheritance

```c
// Pass data between states
void PassDataToState(GameState* from_state, GameState* to_state, const char* key, void* data);

// Retrieve passed data
void* GetPassedData(GameState* state, const char* key);
```

## Input Handling

Each game state can handle input separately, but the system also provides a way to block input during transitions:

```c
// Process input for the current state
void ProcessStateInput(StateManager* manager);

// Check if input should be processed
bool ShouldProcessInput(StateManager* manager);

// Handle global inputs (like debug keys) that work in any state
void HandleGlobalInputs(StateManager* manager);
```

## Debug Support

```c
// Draw debug information about the state manager
void DrawStateManagerDebug(StateManager* manager, Rectangle bounds);

// Log state transitions
void LogStateTransition(StateManager* manager, GameState* from_state, GameState* to_state);

// Toggle debug rendering
void SetStateManagerDebug(StateManager* manager, bool enabled);
```

## Integration with Other Systems

### Settings System Integration

```c
// Apply settings to state manager
void ApplySettingsToStateManager(StateManager* manager, SettingsManager* settings_manager);

// Register state-specific settings
void RegisterStateSettings(GameState* state, SettingsManager* settings_manager);
```

### Sound System Integration

```c
// Play state-specific sounds
void PlayStateSound(GameState* state, const char* sound_name);
void PlayStateMusic(GameState* state, const char* music_name);

// Set state-specific volume levels
void SetStateSoundVolume(GameState* state, float volume);
void SetStateMusicVolume(GameState* state, float volume);
```

## Performance Optimization

```c
// State loading and unloading strategies
void PreloadState(StateManager* manager, int state_id);
void UnloadState(StateManager* manager, int state_id);

// Resource management
void SetStateResourcePriority(GameState* state, int priority);
void OptimizeStateResources(StateManager* manager);
```

## Error Handling

```c
// Error codes for state manager operations
typedef enum StateManagerError {
    STATE_ERROR_NONE,                // No error
    STATE_ERROR_INVALID_STATE,       // Invalid state ID
    STATE_ERROR_STACK_OVERFLOW,      // Stack overflow
    STATE_ERROR_STACK_UNDERFLOW,     // Stack underflow
    STATE_ERROR_ALREADY_REGISTERED,  // State already registered
    STATE_ERROR_NOT_REGISTERED,      // State not registered
    STATE_ERROR_TRANSITION_FAILED,   // Transition failed
    STATE_ERROR_MEMORY_ALLOCATION    // Memory allocation failed
} StateManagerError;

// Error handling functions
StateManagerError GetLastStateError(StateManager* manager);
const char* GetStateErrorString(StateManagerError error);
void SetStateErrorCallback(StateManager* manager, void (*callback)(StateManagerError, const char*));
```

## Implementation Notes

1. **Raylib Integration**: The State Management System will utilize Raylib's rendering and input functions to create a smooth and responsive game flow.

2. **Memory Management**: States and resources will be carefully managed to minimize memory usage, with strategies for loading and unloading resources as needed.

3. **Transition Rendering**: Transitions will use Raylib's render textures to capture the current state of the screen before transitioning to a new state.

4. **Stack-Based Architecture**: The stack-based approach allows for nested states and easy implementation of overlays like pause menus and popups.

5. **Function Pointers**: The use of function pointers for state callbacks allows for flexible and reusable state behaviors.

6. **Global Event System**: Integration with an event system would allow states to communicate with each other without direct coupling.

7. **State Reuse**: The system is designed to allow states to be reused with different parameters, reducing code duplication.

## Conclusion

The Game State Management System for the C/Raylib port builds upon the existing Python/Pygame scene-based architecture while enhancing it with additional features and optimizations. The design provides a flexible, efficient way to manage game flow, with a clear separation of concerns between different game states. 

The stack-based approach allows for complex state hierarchies, while the transition system ensures smooth visual transitions between states. The integration with other systems, such as the Settings System and Sound System, ensures a cohesive game experience. Performance optimizations, such as resource management and state preloading, ensure that the game runs smoothly even on lower-end hardware. 