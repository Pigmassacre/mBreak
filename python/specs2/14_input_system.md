# Input System Specification

## Overview

The Input System is responsible for handling and managing all user input in the game, including keyboard, mouse, gamepad, and touch interactions. It serves as a centralized system that processes raw input events from Raylib, manages input context for the current game state, handles input mapping and configuration, and provides a clean interface for other game systems to query input states.

The Input System aims to be flexible, efficient, and provide consistent behavior across different input methods, allowing players to use their preferred input device while maintaining a unified code interface for game systems that consume input.

## Core Architecture

The Input System is designed around several interconnected components:

1. **Input Manager**: The central hub that coordinates all input handling, maintains device states, processes input, and dispatches events.
2. **Input States**: Structures that track the current and previous states of input devices (keyboard, mouse, gamepad).
3. **Input Mapping**: A configurable system to map physical inputs to logical game actions and axes.
4. **Input Context**: Context-sensitive input handling based on the current game state.
5. **Input Event System**: A queue-based event system for processing input-related events.
6. **Input Recording and Playback**: Facilities for recording and replaying input sequences (useful for debugging and demos).

### Input Manager Structure

```c
typedef struct InputManager {
    // Core properties
    bool enabled;                           // Whether input processing is enabled
    float updateRate;                       // How often input is processed (in seconds)
    
    // Input states
    KeyboardState keyboard;                 // Current keyboard state
    MouseState mouse;                       // Current mouse state
    GamepadState gamepads[MAX_GAMEPADS];    // Current gamepad states
    int activeGamepads;                     // Number of active gamepads
    
    // Input mapping
    InputMap* actionMap;                    // Maps inputs to boolean actions
    InputMap* axisMap;                      // Maps inputs to float axes
    
    // Input processing
    float deadZone;                         // Deadzone for analog inputs
    bool blockRepeatKeys;                   // Whether to block key repeats
    
    // Input context
    InputContext* currentContext;           // Current active input context
    Stack* contextStack;                    // Stack of input contexts
    
    // Input events
    InputEventQueue* eventQueue;            // Queue of input events
    
    // Input recording/playback
    InputRecorder* recorder;                // For recording/playing input
    
    // Timing
    float lastUpdateTime;                   // Time of last input update
    float deltaTime;                        // Time since last update
} InputManager;
```

### Input States

```c
typedef struct KeyboardState {
    // Key states
    bool keys[MAX_KEYS];                    // Current key states
    bool previousKeys[MAX_KEYS];            // Previous frame key states
    bool keyPressed[MAX_KEYS];              // Keys that were pressed this frame
    bool keyReleased[MAX_KEYS];             // Keys that were released this frame
    
    // Text input
    char inputBuffer[256];                  // Text input buffer
    int inputLength;                        // Length of text in buffer
    bool textMode;                          // Whether text input mode is active
    
    // Modifiers
    bool shift;                             // Shift key state
    bool ctrl;                              // Ctrl key state
    bool alt;                               // Alt key state
} KeyboardState;

typedef struct MouseState {
    // Position
    Vector2 position;                       // Current position
    Vector2 previousPosition;               // Previous frame position
    Vector2 delta;                          // Position change since last frame
    Vector2 worldPosition;                  // Position in world coordinates
    
    // Buttons
    bool buttons[MAX_MOUSE_BUTTONS];        // Current button states
    bool previousButtons[MAX_MOUSE_BUTTONS]; // Previous frame button states
    bool buttonPressed[MAX_MOUSE_BUTTONS];  // Buttons pressed this frame
    bool buttonReleased[MAX_MOUSE_BUTTONS]; // Buttons released this frame
    
    // Wheel
    float wheelMove;                        // Mouse wheel movement this frame
    
    // State
    bool isVisible;                         // Whether mouse cursor is visible
    bool isLocked;                          // Whether mouse position is locked
} MouseState;

typedef struct GamepadState {
    // Connection
    bool connected;                         // Whether gamepad is connected
    int id;                                 // Gamepad ID
    
    // Buttons
    bool buttons[MAX_GAMEPAD_BUTTONS];      // Current button states
    bool previousButtons[MAX_GAMEPAD_BUTTONS]; // Previous frame button states
    bool buttonPressed[MAX_GAMEPAD_BUTTONS]; // Buttons pressed this frame
    bool buttonReleased[MAX_GAMEPAD_BUTTONS]; // Buttons released this frame
    
    // Axes
    float axes[MAX_GAMEPAD_AXES];           // Current axis values
    float previousAxes[MAX_GAMEPAD_AXES];   // Previous frame axis values
    float axesDelta[MAX_GAMEPAD_AXES];      // Change in axis values
    
    // Triggers (optional, could be mapped to axes)
    float triggers[2];                      // Left and right trigger values
    float previousTriggers[2];              // Previous trigger values
    
    // Info
    char name[64];                          // Controller name
    int vendorId;                           // Controller vendor ID
    int productId;                          // Controller product ID
} GamepadState;
```

### Input Mapping System

```c
typedef enum InputBindingType {
    BINDING_KEYBOARD,
    BINDING_MOUSE_BUTTON,
    BINDING_MOUSE_AXIS,
    BINDING_GAMEPAD_BUTTON,
    BINDING_GAMEPAD_AXIS,
    BINDING_GAMEPAD_TRIGGER,
} InputBindingType;

typedef struct InputBinding {
    InputBindingType type;                  // Type of binding
    int deviceId;                           // Device ID (for multiple gamepads)
    int code;                               // Key/button/axis code
    float scale;                            // Scale factor for axis input
    bool invert;                            // Whether to invert axis value
    float deadZone;                         // Custom deadzone for this binding
} InputBinding;

typedef struct InputMapEntry {
    const char* name;                       // Name of action/axis
    InputBinding* bindings;                 // List of bindings
    int bindingCount;                       // Number of bindings
    float value;                            // Current value (0-1 for actions, -1 to 1 for axes)
    bool active;                            // Whether action is active
    bool justActivated;                     // Whether action just became active
    bool justDeactivated;                   // Whether action just became inactive
} InputMapEntry;

typedef struct InputMap {
    InputMapEntry* entries;                 // List of map entries
    int count;                              // Number of entries
    int capacity;                           // Capacity of entries array
} InputMap;
```

### Input Context System

```c
typedef struct InputContext {
    const char* name;                       // Context name
    InputMap* actionMap;                    // Action map for this context
    InputMap* axisMap;                      // Axis map for this context
    bool blocksPrevious;                    // Whether this context blocks input to previous contexts
    InputProcessor* processor;              // Custom input processor for this context
} InputContext;

typedef struct InputContextStack {
    InputContext** contexts;                // Stack of contexts
    int count;                              // Number of contexts
    int capacity;                           // Capacity of contexts array
} InputContextStack;
```

### Input Event System

```c
typedef enum InputEventType {
    EVENT_KEY,                              // Keyboard event
    EVENT_MOUSE_BUTTON,                     // Mouse button event
    EVENT_MOUSE_MOVE,                       // Mouse movement event
    EVENT_MOUSE_WHEEL,                      // Mouse wheel event
    EVENT_GAMEPAD_BUTTON,                   // Gamepad button event
    EVENT_GAMEPAD_AXIS,                     // Gamepad axis event
    EVENT_GAMEPAD_CONNECTION,               // Gamepad connection/disconnection
    EVENT_ACTION,                           // Input action event
    EVENT_AXIS,                             // Input axis event
    EVENT_TEXT,                             // Text input event
} InputEventType;

typedef struct InputEvent {
    InputEventType type;                    // Type of event
    float timestamp;                        // Time event occurred
    
    union {
        struct {
            int keyCode;                    // Key code
            bool pressed;                   // Whether key was pressed
        } key;
        
        struct {
            int button;                     // Button index
            bool pressed;                   // Whether button was pressed
            Vector2 position;               // Mouse position
        } mouseButton;
        
        struct {
            Vector2 position;               // New position
            Vector2 delta;                  // Position change
        } mouseMove;
        
        struct {
            float value;                    // Wheel delta
        } mouseWheel;
        
        struct {
            int gamepadId;                  // Gamepad ID
            int button;                     // Button index
            bool pressed;                   // Whether button was pressed
        } gamepadButton;
        
        struct {
            int gamepadId;                  // Gamepad ID
            int axis;                       // Axis index
            float value;                    // New axis value
            float delta;                    // Value change
        } gamepadAxis;
        
        struct {
            int gamepadId;                  // Gamepad ID
            bool connected;                 // Whether gamepad was connected
        } gamepadConnection;
        
        struct {
            const char* actionName;         // Action name
            bool activated;                 // Whether action was activated
        } action;
        
        struct {
            const char* axisName;           // Axis name
            float value;                    // New axis value
            float delta;                    // Value change
        } axis;
        
        struct {
            char character;                 // Input character
        } text;
    } data;
} InputEvent;

typedef struct InputEventQueue {
    InputEvent* events;                     // Array of events
    int count;                              // Number of events
    int capacity;                           // Capacity of events array
    int head;                               // Head index
    int tail;                               // Tail index
} InputEventQueue;
```

### Player Input Configuration

```c
typedef struct PlayerInputConfig {
    // Core properties
    int playerIndex;                         // Player number (1-4)
    int gamepadId;                           // Assigned gamepad ID or -1 if none
    bool isAI;                               // Whether player is AI-controlled
    int aiDifficulty;                        // AI difficulty level (0-3)
    
    // Key bindings
    int keyUp;                               // Key for up movement
    int keyDown;                             // Key for down movement
    int keyAction;                           // Key for primary action
    
    // Gamepad bindings
    int padUp;                               // Button/axis for up
    int padDown;                             // Button/axis for down
    int padAction;                           // Button for primary action
    
    // Custom settings
    char name[32];                           // Player name
    bool vibrationEnabled;                   // Whether gamepad vibration is enabled
    float vibrationStrength;                 // Strength of vibration effects
} PlayerInputConfig;
```

## Core Functions

### Input Manager Functions

```c
// Initialization and lifecycle
InputManager* InitInputManager(void);
void ShutdownInputManager(InputManager* manager);
void UpdateInputManager(InputManager* manager);
void EnableInput(InputManager* manager, bool enable);
void SetInputUpdateRate(InputManager* manager, float updateRate);

// Device queries
bool IsKeyDown(InputManager* manager, int key);
bool IsKeyPressed(InputManager* manager, int key);
bool IsKeyReleased(InputManager* manager, int key);
bool IsMouseButtonDown(InputManager* manager, int button);
bool IsMouseButtonPressed(InputManager* manager, int button);
bool IsMouseButtonReleased(InputManager* manager, int button);
Vector2 GetMousePosition(InputManager* manager);
Vector2 GetMouseDelta(InputManager* manager);
float GetMouseWheelMove(InputManager* manager);
bool IsGamepadConnected(InputManager* manager, int gamepadId);
bool IsGamepadButtonDown(InputManager* manager, int gamepadId, int button);
bool IsGamepadButtonPressed(InputManager* manager, int gamepadId, int button);
bool IsGamepadButtonReleased(InputManager* manager, int gamepadId, int button);
float GetGamepadAxisValue(InputManager* manager, int gamepadId, int axis);

// Action/axis queries
bool IsActionActive(InputManager* manager, const char* actionName);
bool IsActionJustActivated(InputManager* manager, const char* actionName);
bool IsActionJustDeactivated(InputManager* manager, const char* actionName);
float GetAxisValue(InputManager* manager, const char* axisName);

// Input context management
void PushInputContext(InputManager* manager, InputContext* context);
void PopInputContext(InputManager* manager);
void SetActiveInputContext(InputManager* manager, const char* contextName);
InputContext* GetInputContext(InputManager* manager, const char* contextName);

// Player configuration
void ConfigurePlayerInput(InputManager* manager, PlayerInputConfig* config);
```

### Input Mapping Functions

```c
// Map management
InputMap* CreateInputMap(int initialCapacity);
void DestroyInputMap(InputMap* map);
void ClearInputMap(InputMap* map);

// Map entries
int AddActionMapping(InputMap* map, const char* actionName);
int AddAxisMapping(InputMap* map, const char* axisName);
void RemoveMapping(InputMap* map, const char* name);

// Binding configuration
void AddActionBinding(InputMap* map, const char* actionName, InputBinding binding);
void AddAxisBinding(InputMap* map, const char* axisName, InputBinding binding);
void RemoveAllBindings(InputMap* map, const char* name);
void RemoveBinding(InputMap* map, const char* name, int bindingIndex);

// Default mapping configuration
void ConfigureDefaultKeyboardMappings(InputMap* actionMap, InputMap* axisMap);
void ConfigureDefaultGamepadMappings(InputMap* actionMap, InputMap* axisMap);
```

### Input Context Functions

```c
// Context management
InputContext* CreateInputContext(const char* name, bool blocksPrevious);
void DestroyInputContext(InputContext* context);
void CopyInputContext(InputContext* dest, const InputContext* src);

// Context configuration
void SetContextBlocksPrevious(InputContext* context, bool blocks);
void SetContextProcessor(InputContext* context, InputProcessor* processor);
```

### Input Recording Functions

```c
// Recording control
void StartInputRecording(InputManager* manager);
void StopInputRecording(InputManager* manager);
void SaveInputRecording(InputManager* manager, const char* filename);
void LoadInputRecording(InputManager* manager, const char* filename);

// Playback control
void StartInputPlayback(InputManager* manager);
void PauseInputPlayback(InputManager* manager);
void StopInputPlayback(InputManager* manager);
```

## Input Mappings

### Default Action Mappings

These standard actions will be mapped to appropriate keys/buttons:

```c
// Core actions
#define ACTION_CONFIRM      "Confirm"        // Select/OK/Accept
#define ACTION_CANCEL       "Cancel"         // Back/Cancel/No
#define ACTION_MENU         "Menu"           // Open menu/Show options
#define ACTION_PAUSE        "Pause"          // Pause game

// Game-specific actions
#define ACTION_PLAYER1_UP   "Player1Up"      // Player 1 paddle up
#define ACTION_PLAYER1_DOWN "Player1Down"    // Player 1 paddle down
#define ACTION_PLAYER1_ACTION "Player1Action"// Player 1 special action
#define ACTION_PLAYER2_UP   "Player2Up"      // Player 2 paddle up
#define ACTION_PLAYER2_DOWN "Player2Down"    // Player 2 paddle down
#define ACTION_PLAYER2_ACTION "Player2Action"// Player 2 special action

// Debug actions
#define ACTION_DEBUG_TOGGLE "DebugToggle"    // Toggle debug display
#define ACTION_DEBUG_NEXT   "DebugNext"      // Next debug page
#define ACTION_DEBUG_PREV   "DebugPrev"      // Previous debug page
```

### Default Axis Mappings

```c
// Player movement axes
#define AXIS_PLAYER1_VERTICAL "Player1Vertical"  // Player 1 vertical movement
#define AXIS_PLAYER2_VERTICAL "Player2Vertical"  // Player 2 vertical movement

// UI navigation axes
#define AXIS_UI_HORIZONTAL "UIHorizontal"        // UI horizontal navigation
#define AXIS_UI_VERTICAL   "UIVertical"          // UI vertical navigation
```

## Input Contexts

The Input System will include several pre-defined contexts for different game states:

### Menu Context

```c
// Pre-defined input context for menus
void CreateMenuInputContext(void) {
    InputContext* context = CreateInputContext("Menu", true);
    
    // Configure action mappings
    AddActionMapping(context->actionMap, ACTION_CONFIRM);
    AddActionMapping(context->actionMap, ACTION_CANCEL);
    AddActionMapping(context->actionMap, ACTION_MENU);
    
    // Configure axis mappings
    AddAxisMapping(context->axisMap, AXIS_UI_HORIZONTAL);
    AddAxisMapping(context->axisMap, AXIS_UI_VERTICAL);
    
    // Configure bindings
    // Keyboard bindings
    AddActionBinding(context->actionMap, ACTION_CONFIRM, (InputBinding){BINDING_KEYBOARD, 0, KEY_ENTER});
    AddActionBinding(context->actionMap, ACTION_CANCEL, (InputBinding){BINDING_KEYBOARD, 0, KEY_ESCAPE});
    AddActionBinding(context->actionMap, ACTION_MENU, (InputBinding){BINDING_KEYBOARD, 0, KEY_TAB});
    
    AddAxisBinding(context->axisMap, AXIS_UI_HORIZONTAL, (InputBinding){BINDING_KEYBOARD, 0, KEY_RIGHT, 1.0f});
    AddAxisBinding(context->axisMap, AXIS_UI_HORIZONTAL, (InputBinding){BINDING_KEYBOARD, 0, KEY_LEFT, -1.0f});
    AddAxisBinding(context->axisMap, AXIS_UI_VERTICAL, (InputBinding){BINDING_KEYBOARD, 0, KEY_UP, -1.0f});
    AddAxisBinding(context->axisMap, AXIS_UI_VERTICAL, (InputBinding){BINDING_KEYBOARD, 0, KEY_DOWN, 1.0f});
    
    // Gamepad bindings
    AddActionBinding(context->actionMap, ACTION_CONFIRM, (InputBinding){BINDING_GAMEPAD_BUTTON, 0, GAMEPAD_BUTTON_A});
    AddActionBinding(context->actionMap, ACTION_CANCEL, (InputBinding){BINDING_GAMEPAD_BUTTON, 0, GAMEPAD_BUTTON_B});
    AddActionBinding(context->actionMap, ACTION_MENU, (InputBinding){BINDING_GAMEPAD_BUTTON, 0, GAMEPAD_BUTTON_START});
    
    AddAxisBinding(context->axisMap, AXIS_UI_HORIZONTAL, (InputBinding){BINDING_GAMEPAD_AXIS, 0, GAMEPAD_AXIS_LEFT_X});
    AddAxisBinding(context->axisMap, AXIS_UI_VERTICAL, (InputBinding){BINDING_GAMEPAD_AXIS, 0, GAMEPAD_AXIS_LEFT_Y});
    
    return context;
}
```

### Game Context

```c
// Pre-defined input context for gameplay
void CreateGameInputContext(void) {
    InputContext* context = CreateInputContext("Game", true);
    
    // Configure action mappings
    AddActionMapping(context->actionMap, ACTION_PAUSE);
    AddActionMapping(context->actionMap, ACTION_PLAYER1_UP);
    AddActionMapping(context->actionMap, ACTION_PLAYER1_DOWN);
    AddActionMapping(context->actionMap, ACTION_PLAYER1_ACTION);
    AddActionMapping(context->actionMap, ACTION_PLAYER2_UP);
    AddActionMapping(context->actionMap, ACTION_PLAYER2_DOWN);
    AddActionMapping(context->actionMap, ACTION_PLAYER2_ACTION);
    
    // Configure axis mappings
    AddAxisMapping(context->axisMap, AXIS_PLAYER1_VERTICAL);
    AddAxisMapping(context->axisMap, AXIS_PLAYER2_VERTICAL);
    
    // Configure default bindings based on settings
    
    return context;
}
```

## Player Input Configuration

The Input System allows for configuring player-specific input settings:

```c
// Configure input for a player (either from settings or defaults)
void ConfigurePlayerInput(InputManager* manager, PlayerInputConfig* config) {
    // Set up action bindings
    if (config->gamepadId >= 0) {
        // Player has a gamepad - configure gamepad bindings
        AddActionBinding(manager->actionMap, GetPlayerActionName(config->playerIndex, "Up"), 
                         (InputBinding){BINDING_GAMEPAD_BUTTON, config->gamepadId, config->padUp});
        AddActionBinding(manager->actionMap, GetPlayerActionName(config->playerIndex, "Down"), 
                         (InputBinding){BINDING_GAMEPAD_BUTTON, config->gamepadId, config->padDown});
        AddActionBinding(manager->actionMap, GetPlayerActionName(config->playerIndex, "Action"), 
                         (InputBinding){BINDING_GAMEPAD_BUTTON, config->gamepadId, config->padAction});
    } else {
        // Player using keyboard - configure keyboard bindings
        AddActionBinding(manager->actionMap, GetPlayerActionName(config->playerIndex, "Up"), 
                         (InputBinding){BINDING_KEYBOARD, 0, config->keyUp});
        AddActionBinding(manager->actionMap, GetPlayerActionName(config->playerIndex, "Down"), 
                         (InputBinding){BINDING_KEYBOARD, 0, config->keyDown});
        AddActionBinding(manager->actionMap, GetPlayerActionName(config->playerIndex, "Action"), 
                         (InputBinding){BINDING_KEYBOARD, 0, config->keyAction});
    }
    
    // Set up axis bindings (for analog movement)
    if (config->gamepadId >= 0) {
        AddAxisBinding(manager->axisMap, GetPlayerAxisName(config->playerIndex, "Vertical"), 
                      (InputBinding){BINDING_GAMEPAD_AXIS, config->gamepadId, GAMEPAD_AXIS_LEFT_Y});
    } else {
        // Simulate axis with keyboard buttons
        AddAxisBinding(manager->axisMap, GetPlayerAxisName(config->playerIndex, "Vertical"), 
                      (InputBinding){BINDING_KEYBOARD, 0, config->keyUp, -1.0f});
        AddAxisBinding(manager->axisMap, GetPlayerAxisName(config->playerIndex, "Vertical"), 
                      (InputBinding){BINDING_KEYBOARD, 0, config->keyDown, 1.0f});
    }
}
```

## Input Configuration and Settings System

The Input System includes functionality for saving and loading input configurations:

```c
// Load input configuration from a file
bool LoadInputConfiguration(const char* filename, InputManager* manager);

// Save current input configuration to a file
bool SaveInputConfiguration(const char* filename, InputManager* manager);

// Reset input configuration to defaults
void ResetInputConfigurationToDefaults(InputManager* manager);

// Show in-game input configuration screen
void ShowInputConfigurationScreen(void);
```

## Integration with Game State Management

The Input System integrates with the Game State Management System:

```c
// Input context switch based on game state
void OnGameStateChanged(GameState* oldState, GameState* newState) {
    // When state changes, update input context
    switch (newState->type) {
        case STATE_MAIN_MENU:
            SetActiveInputContext(inputManager, "Menu");
            break;
        case STATE_GAME:
            SetActiveInputContext(inputManager, "Game");
            break;
        case STATE_PAUSE:
            PushInputContext(inputManager, GetInputContext(inputManager, "Pause"));
            break;
        default:
            break;
    }
}

// When leaving a state
void OnGameStateExit(GameState* state) {
    if (state->type == STATE_PAUSE) {
        // When exiting pause menu, pop the context
        PopInputContext(inputManager);
    }
}
```

## Feedback and Response

The Input System includes haptic feedback functionality:

```c
// Trigger vibration on a gamepad
void TriggerGamepadVibration(int gamepadId, float intensity, float duration);

// Trigger directional vibration (if supported)
void TriggerDirectionalVibration(int gamepadId, float leftIntensity, float rightIntensity, float duration);

// Stop all vibration
void StopAllVibration(void);
```

## Debug Support

The Input System includes debugging functionality:

```c
// Toggle input debugging display
void ToggleInputDebug(void);

// Draw input debug information
void DrawInputDebugInfo(void);

// Log input events to console
void LogInputEvents(bool enabled);
```

## Performance Optimization

To ensure efficient input processing, the Input System employs several optimization strategies:

1. **Input Filtering**: Process only enabled input devices and active contexts.
2. **Update Rate Control**: Adjust input processing frequency based on game requirements.
3. **Event Batching**: Process multiple input events in a single batch to reduce overhead.
4. **Context-Sensitive Processing**: Only process input relevant to the current game state.
5. **Lazy Evaluation**: Only evaluate input mappings when queried, not on every update.

## Error Handling

The Input System includes robust error handling:

```c
// Error codes
#define INPUT_ERROR_NONE               0
#define INPUT_ERROR_INVALID_DEVICE     1
#define INPUT_ERROR_INVALID_BINDING    2
#define INPUT_ERROR_INVALID_MAPPING    3
#define INPUT_ERROR_FILE_IO            4
#define INPUT_ERROR_MEMORY             5

// Get last error
int GetInputSystemError(void);

// Get error message
const char* GetInputSystemErrorMessage(int errorCode);
```

## Implementation Notes

### Raylib Integration

The Input System builds on Raylib's input functions but adds additional functionality:

```c
// Update function processes Raylib input and updates our state
void UpdateInputManager(InputManager* manager) {
    float currentTime = GetTime();
    manager->deltaTime = currentTime - manager->lastUpdateTime;
    manager->lastUpdateTime = currentTime;
    
    // Only update at configured rate
    if (manager->deltaTime < manager->updateRate) {
        return;
    }
    
    // Update keyboard state
    for (int i = 0; i < MAX_KEYS; i++) {
        manager->keyboard.previousKeys[i] = manager->keyboard.keys[i];
        manager->keyboard.keys[i] = IsKeyDown(i);
        manager->keyboard.keyPressed[i] = IsKeyPressed(i);
        manager->keyboard.keyReleased[i] = IsKeyReleased(i);
    }
    
    // Update modifier keys
    manager->keyboard.shift = IsKeyDown(KEY_LEFT_SHIFT) || IsKeyDown(KEY_RIGHT_SHIFT);
    manager->keyboard.ctrl = IsKeyDown(KEY_LEFT_CONTROL) || IsKeyDown(KEY_RIGHT_CONTROL);
    manager->keyboard.alt = IsKeyDown(KEY_LEFT_ALT) || IsKeyDown(KEY_RIGHT_ALT);
    
    // Update mouse state
    manager->mouse.previousPosition = manager->mouse.position;
    manager->mouse.position = GetMousePosition();
    manager->mouse.delta = (Vector2){
        manager->mouse.position.x - manager->mouse.previousPosition.x,
        manager->mouse.position.y - manager->mouse.previousPosition.y
    };
    
    for (int i = 0; i < MAX_MOUSE_BUTTONS; i++) {
        manager->mouse.previousButtons[i] = manager->mouse.buttons[i];
        manager->mouse.buttons[i] = IsMouseButtonDown(i);
        manager->mouse.buttonPressed[i] = IsMouseButtonPressed(i);
        manager->mouse.buttonReleased[i] = IsMouseButtonReleased(i);
    }
    
    manager->mouse.wheelMove = GetMouseWheelMove();
    
    // Update gamepad states
    for (int i = 0; i < MAX_GAMEPADS; i++) {
        GamepadState* gamepad = &manager->gamepads[i];
        bool wasConnected = gamepad->connected;
        gamepad->connected = IsGamepadAvailable(i);
        
        // Handle connection/disconnection
        if (gamepad->connected != wasConnected) {
            // Process gamepad connection event
            if (gamepad->connected) {
                gamepad->id = i;
                GetGamepadName(i, gamepad->name, sizeof(gamepad->name));
            }
        }
        
        if (gamepad->connected) {
            // Update button states
            for (int j = 0; j < MAX_GAMEPAD_BUTTONS; j++) {
                gamepad->previousButtons[j] = gamepad->buttons[j];
                gamepad->buttons[j] = IsGamepadButtonDown(i, j);
                gamepad->buttonPressed[j] = IsGamepadButtonPressed(i, j);
                gamepad->buttonReleased[j] = IsGamepadButtonReleased(i, j);
            }
            
            // Update axes
            for (int j = 0; j < MAX_GAMEPAD_AXES; j++) {
                gamepad->previousAxes[j] = gamepad->axes[j];
                gamepad->axes[j] = GetGamepadAxisMovement(i, j);
                gamepad->axesDelta[j] = gamepad->axes[j] - gamepad->previousAxes[j];
                
                // Apply deadzone
                if (fabs(gamepad->axes[j]) < manager->deadZone) {
                    gamepad->axes[j] = 0.0f;
                }
            }
        }
    }
    
    // Update input mapping states
    UpdateInputMaps(manager);
    
    // Generate input events
    GenerateInputEvents(manager);
    
    // Record input if active
    if (manager->recorder->isRecording) {
        RecordInputFrame(manager->recorder, manager);
    }
}
```

### Memory Management

The Input System follows these memory management principles:

1. The `InputManager` is allocated once at initialization and freed at shutdown.
2. Input mappings are allocated dynamically and can be modified at runtime.
3. Input contexts may be created and destroyed as needed.
4. Input events are stored in a circular buffer to avoid frequent allocations.

### Input Prioritization

The Input System prioritizes input as follows:

1. First, apply any active input recordings or automated input.
2. Next, handle any direct input from connected devices.
3. Finally, process the input through the active context stack.

This allows for scripted input sequences to override user input when needed.

## Conclusion

The Input System for the C/Raylib port of mBreak builds upon the functionality of the original Python/Pygame implementation while adding several key enhancements:

1. **Improved Input Abstraction**: A flexible mapping system that decouples physical inputs from game actions.
2. **Multiple Input Methods**: Seamless support for keyboard, mouse, and gamepads, with easy extension to other devices.
3. **Context-Sensitive Input**: Input handling that changes based on the current game state.
4. **Enhanced Gamepad Support**: Better support for multiple gamepads, analog inputs, and haptic feedback.
5. **Input Recording and Playback**: Ability to record and replay input sequences for debugging and demos.
6. **Integration with Game State**: Tight integration with the Game State Management System.
7. **Performance Optimizations**: Efficient input processing that scales with game needs.
8. **Debug Support**: Comprehensive debugging tools for input visualization and testing.

These enhancements make the Input System more robust, flexible, and maintainable, providing a solid foundation for the C/Raylib port of mBreak. 