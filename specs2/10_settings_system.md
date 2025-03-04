# Settings System Specification

## Overview

The Settings System is responsible for managing game configuration, user preferences, and ensuring settings persistence across game sessions. It provides a centralized way to access and modify game settings, handle their serialization to and from disk, and maintain consistency across the application.

This specification outlines the design and implementation of the Settings System for the C/Raylib port, translating the existing Python/Pygame implementation while enhancing it with additional features and optimizations possible in C and Raylib.

## Core Architecture

### Settings Categories

The settings system will be organized into several categories:

1. **Core Settings**: Basic game settings like version, debug mode, and performance-related settings
2. **Graphics Settings**: Visual options for shadows, particles, resolution, etc.
3. **Sound Settings**: Audio-related options for music and sound effects volumes
4. **Input Settings**: Player control mappings and input device configurations
5. **Game Settings**: Gameplay-specific settings and configurations

### Settings Structure

```c
// Enums for setting types
typedef enum SettingType {
    SETTING_TYPE_BOOL,
    SETTING_TYPE_INT,
    SETTING_TYPE_FLOAT,
    SETTING_TYPE_STRING,
    SETTING_TYPE_VECTOR2,
    SETTING_TYPE_COLOR,
    SETTING_TYPE_KEY
} SettingType;

// Setting structure
typedef struct Setting {
    char name[64];           // Name of the setting (used as key)
    char display_name[64];   // User-friendly display name
    char description[256];   // Description of the setting
    SettingType type;        // Type of the setting value
    
    // Union for different value types
    union {
        bool bool_value;
        int int_value;
        float float_value;
        char string_value[128];
        Vector2 vector2_value;
        Color color_value;
        int key_value;
    };
    
    // Default values (for reset functionality)
    union {
        bool default_bool;
        int default_int;
        float default_float;
        char default_string[128];
        Vector2 default_vector2;
        Color default_color;
        int default_key;
    };
    
    // Constraints for numeric values
    float min_value;
    float max_value;
    
    // Category information
    int category;            // Category this setting belongs to
    bool hidden;             // Whether to hide from settings UI
    bool requires_restart;   // Whether changes require game restart
    
    // Callback when value changes
    void (*on_change)(struct Setting*);
} Setting;

// Settings manager structure
typedef struct SettingsManager {
    Setting* settings;       // Array of settings
    int settings_count;      // Number of settings
    int settings_capacity;   // Capacity of settings array
    
    char filename[256];      // File to save/load settings
    bool dirty;              // Whether settings have unsaved changes
} SettingsManager;
```

### Core Functions

```c
// Initialization and cleanup
SettingsManager* InitSettingsManager(const char* filename);
void DestroySettingsManager(SettingsManager* manager);

// Settings registration
void RegisterBoolSetting(SettingsManager* manager, const char* name, const char* display_name, const char* description, bool default_value, int category, bool hidden, bool requires_restart, void (*on_change)(Setting*));
void RegisterIntSetting(SettingsManager* manager, const char* name, const char* display_name, const char* description, int default_value, int min_value, int max_value, int category, bool hidden, bool requires_restart, void (*on_change)(Setting*));
void RegisterFloatSetting(SettingsManager* manager, const char* name, const char* display_name, const char* description, float default_value, float min_value, float max_value, int category, bool hidden, bool requires_restart, void (*on_change)(Setting*));
void RegisterStringSetting(SettingsManager* manager, const char* name, const char* display_name, const char* description, const char* default_value, int category, bool hidden, bool requires_restart, void (*on_change)(Setting*));
void RegisterVector2Setting(SettingsManager* manager, const char* name, const char* display_name, const char* description, Vector2 default_value, int category, bool hidden, bool requires_restart, void (*on_change)(Setting*));
void RegisterColorSetting(SettingsManager* manager, const char* name, const char* display_name, const char* description, Color default_value, int category, bool hidden, bool requires_restart, void (*on_change)(Setting*));
void RegisterKeySetting(SettingsManager* manager, const char* name, const char* display_name, const char* description, int default_value, int category, bool hidden, bool requires_restart, void (*on_change)(Setting*));

// Value getters and setters
bool GetBoolSetting(SettingsManager* manager, const char* name);
int GetIntSetting(SettingsManager* manager, const char* name);
float GetFloatSetting(SettingsManager* manager, const char* name);
const char* GetStringSetting(SettingsManager* manager, const char* name);
Vector2 GetVector2Setting(SettingsManager* manager, const char* name);
Color GetColorSetting(SettingsManager* manager, const char* name);
int GetKeySetting(SettingsManager* manager, const char* name);

void SetBoolSetting(SettingsManager* manager, const char* name, bool value);
void SetIntSetting(SettingsManager* manager, const char* name, int value);
void SetFloatSetting(SettingsManager* manager, const char* name, float value);
void SetStringSetting(SettingsManager* manager, const char* name, const char* value);
void SetVector2Setting(SettingsManager* manager, const char* name, Vector2 value);
void SetColorSetting(SettingsManager* manager, const char* name, Color value);
void SetKeySetting(SettingsManager* manager, const char* name, int value);

// Setting reset
void ResetSetting(SettingsManager* manager, const char* name);
void ResetAllSettings(SettingsManager* manager);
void ResetCategorySettings(SettingsManager* manager, int category);

// File operations
bool LoadSettings(SettingsManager* manager);
bool SaveSettings(SettingsManager* manager);
```

## Settings File Format

The settings file format will be a simple text-based format similar to the original implementation, but with improved structure and readability:

```
# mBreak Settings File
# Generated by mBreak version X.X

[Core]
debug_mode = 0
game_version = 1.0

[Players]
player1_name = Player One
player2_name = Player Two

[Graphics]
shadows = 1
particles = 1
flashes = 1
traces = 1
background = 1
fullscreen = 0
resolution = 1366x768
max_fps = 60
trajectory = 1

[Audio]
sound_volume = 1.0
music_volume = 1.0

[Controls]
player1_key_up = 26          # W key
player1_key_down = 22        # S key
player1_key_action = 18      # R key
player2_key_up = 73          # Up arrow
player2_key_down = 74        # Down arrow
player2_key_action = 77      # Right shift
```

### File Parser Implementation

```c
// File parsing and writing
bool ParseSettingsFile(SettingsManager* manager, const char* filename);
bool WriteSettingsFile(SettingsManager* manager, const char* filename);

// Helper functions for parsing
Setting* FindSettingByName(SettingsManager* manager, const char* name);
bool ParseSettingValue(Setting* setting, const char* value);
const char* SettingValueToString(Setting* setting);
```

## Default Settings Initialization

The settings system will initialize with reasonable defaults for all settings, ensuring the game is playable without requiring a settings file to exist:

```c
// Initialize default settings
void InitializeDefaultSettings(SettingsManager* manager) {
    // Core settings
    RegisterBoolSetting(manager, "debug_mode", "Debug Mode", "Enable debug information display", false, 0, false, false, NULL);
    RegisterStringSetting(manager, "game_version", "Game Version", "Current game version", "1.0", 0, true, false, NULL);
    
    // Graphics settings
    RegisterBoolSetting(manager, "shadows", "Show Shadows", "Display shadows under game objects", true, 1, false, false, OnGraphicsSettingChanged);
    RegisterBoolSetting(manager, "particles", "Show Particles", "Display particle effects", true, 1, false, false, OnGraphicsSettingChanged);
    RegisterBoolSetting(manager, "flashes", "Show Flashes", "Display flash effects", true, 1, false, false, OnGraphicsSettingChanged);
    RegisterBoolSetting(manager, "traces", "Show Traces", "Display trace effects", true, 1, false, false, OnGraphicsSettingChanged);
    RegisterBoolSetting(manager, "background", "Show Background", "Display background elements", true, 1, false, false, OnGraphicsSettingChanged);
    RegisterBoolSetting(manager, "fullscreen", "Fullscreen", "Run the game in fullscreen mode", false, 1, false, true, OnFullscreenChanged);
    RegisterStringSetting(manager, "resolution", "Resolution", "Screen resolution", "1366x768", 1, false, true, OnResolutionChanged);
    RegisterIntSetting(manager, "max_fps", "Maximum FPS", "Cap frames per second to this value", 60, 30, 240, 1, false, false, OnMaxFpsChanged);
    RegisterBoolSetting(manager, "trajectory", "Show Trajectory", "Display ball trajectory prediction", true, 1, false, false, NULL);
    
    // Audio settings
    RegisterFloatSetting(manager, "sound_volume", "Sound Volume", "Volume for sound effects", 1.0f, 0.0f, 1.0f, 2, false, false, OnSoundVolumeChanged);
    RegisterFloatSetting(manager, "music_volume", "Music Volume", "Volume for background music", 1.0f, 0.0f, 1.0f, 2, false, false, OnMusicVolumeChanged);
    
    // Player settings
    RegisterStringSetting(manager, "player1_name", "Player 1 Name", "Name for Player 1", "Player One", 3, false, false, NULL);
    RegisterStringSetting(manager, "player2_name", "Player 2 Name", "Name for Player 2", "Player Two", 3, false, false, NULL);
    
    // Controls
    RegisterKeySetting(manager, "player1_key_up", "Player 1 Up", "Key for Player 1 to move up", KEY_W, 4, false, false, NULL);
    RegisterKeySetting(manager, "player1_key_down", "Player 1 Down", "Key for Player 1 to move down", KEY_S, 4, false, false, NULL);
    RegisterKeySetting(manager, "player1_key_action", "Player 1 Action", "Key for Player 1 to perform action", KEY_R, 4, false, false, NULL);
    RegisterKeySetting(manager, "player2_key_up", "Player 2 Up", "Key for Player 2 to move up", KEY_UP, 4, false, false, NULL);
    RegisterKeySetting(manager, "player2_key_down", "Player 2 Down", "Key for Player 2 to move down", KEY_DOWN, 4, false, false, NULL);
    RegisterKeySetting(manager, "player2_key_action", "Player 2 Action", "Key for Player 2 to perform action", KEY_RIGHT_SHIFT, 4, false, false, NULL);
}
```

## Settings UI Integration

The settings system will provide integration points for the GUI system to create a settings menu:

```c
// Get settings information for UI
int GetSettingsCategoryCount(SettingsManager* manager);
const char* GetSettingsCategoryName(int category);
int GetSettingsCountInCategory(SettingsManager* manager, int category);
Setting* GetSettingInCategory(SettingsManager* manager, int category, int index);

// UI helper functions
void RenderSettingControl(Setting* setting, Rectangle bounds);
bool UpdateSettingControl(Setting* setting, Rectangle bounds);
```

## Change Callbacks

The settings system will support callbacks for when settings change, allowing systems to respond immediately:

```c
// Example callback implementations
void OnGraphicsSettingChanged(Setting* setting) {
    // Update graphics system with new setting
    UpdateGraphicsSystem();
}

void OnSoundVolumeChanged(Setting* setting) {
    // Update sound system with new volume
    SetMasterSoundVolume(setting->float_value);
}

void OnMusicVolumeChanged(Setting* setting) {
    // Update music system with new volume
    SetMasterMusicVolume(setting->float_value);
}

void OnResolutionChanged(Setting* setting) {
    // Parse resolution string
    int width, height;
    sscanf(setting->string_value, "%dx%d", &width, &height);
    
    // Update window size
    SetWindowSize(width, height);
}

void OnFullscreenChanged(Setting* setting) {
    // Toggle fullscreen mode
    if (setting->bool_value) {
        SetWindowState(FLAG_FULLSCREEN_MODE);
    } else {
        ClearWindowState(FLAG_FULLSCREEN_MODE);
    }
}

void OnMaxFpsChanged(Setting* setting) {
    // Set target FPS
    SetTargetFPS(setting->int_value);
}
```

## Auto-save Feature

The settings system will include an auto-save feature to ensure settings aren't lost:

```c
// Auto-save settings after a delay when changes are made
void InitializeAutoSave(SettingsManager* manager);
void UpdateAutoSave(SettingsManager* manager);
```

## Settings Command Line Override

The system will support command-line overrides for settings:

```c
// Parse command line arguments for settings overrides
void ParseCommandLineSettings(SettingsManager* manager, int argc, char** argv);
```

## Multi-Profile Support

Enhanced from the original implementation, the C/Raylib version will support multiple settings profiles:

```c
// Profile management functions
void CreateSettingsProfile(SettingsManager* manager, const char* profile_name);
void LoadSettingsProfile(SettingsManager* manager, const char* profile_name);
void SaveSettingsProfile(SettingsManager* manager, const char* profile_name);
void DeleteSettingsProfile(SettingsManager* manager, const char* profile_name);
char** GetAvailableProfiles(SettingsManager* manager, int* count);
```

## Settings Validation

The settings system will include validation to ensure settings remain within acceptable ranges:

```c
// Validate settings when loading or changing
bool ValidateSetting(Setting* setting);
bool ValidateAllSettings(SettingsManager* manager);
```

## Integration with Other Systems

### Graphics System Integration

```c
// Apply settings to graphics system
void ApplyGraphicsSettings(SettingsManager* manager);
void UpdateGraphicsSystem();
```

### Sound System Integration

```c
// Apply settings to sound system
void ApplySoundSettings(SettingsManager* manager);
void SetMasterSoundVolume(float volume);
void SetMasterMusicVolume(float volume);
```

### Input System Integration

```c
// Apply settings to input system
void ApplyInputSettings(SettingsManager* manager);
void UpdateControlMappings();
```

## Migration Support

The settings system will include functionality to migrate settings from older versions:

```c
// Migrate settings from older versions
bool MigrateSettingsFromVersion(SettingsManager* manager, const char* old_version);
```

## Debugging Support

```c
// Debug visualization for settings
void PrintAllSettings(SettingsManager* manager);
void LogSettingsState(SettingsManager* manager);
```

## Implementation Notes

1. The Settings System will use a simple key-value structure for efficient lookup of settings.
2. File parsing will be handled with robust error checking to prevent crashes from malformed files.
3. Default values will ensure the game is playable even without a settings file.
4. Multiple profiles will allow different players to maintain their own preferences.
5. The system will provide a simple API for other systems to access and modify settings.
6. Callbacks will ensure that systems are updated immediately when relevant settings change.

## Conclusion

The Settings System specification for the C/Raylib port builds upon the existing Python/Pygame implementation while enhancing it with additional features and optimizations. The design provides a flexible, type-safe way to handle game configuration while ensuring consistent behavior across the application. The additions of profiles, validation, and improved UI integration will enhance the user experience and make the game more accessible to players with different preferences and hardware capabilities. 