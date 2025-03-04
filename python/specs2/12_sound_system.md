# Sound System Specification

## Overview

The Sound System is responsible for managing all audio aspects of the game, including sound effects, background music, and audio settings. It provides a centralized way to load, play, and control sounds while ensuring efficient resource management and a consistent audio experience across the game.

This specification outlines the design and implementation of the Sound System for the C/Raylib port, translating the existing Python/Pygame implementation while enhancing it with additional features and optimizations possible in C and Raylib.

## Core Architecture

The Sound System is divided into two main components:

1. **Sound Effects Subsystem**: Manages short audio clips like explosions, collisions, and UI sounds
2. **Music Subsystem**: Handles background music, including transitions, playlists, and continuous playback

### Sound Manager Structure

```c
typedef struct SoundManager {
    // Sound effects management
    Sound* sounds;                  // Array of loaded sound effects
    int sound_count;                // Number of loaded sounds
    int sound_capacity;             // Maximum number of sounds
    
    // Sound categories for volume control
    float master_volume;            // Master volume multiplier (0.0-1.0)
    float sfx_volume;               // Sound effects volume multiplier (0.0-1.0)
    float ui_volume;                // UI sound volume multiplier (0.0-1.0)
    
    // Sound mapping
    char** sound_names;             // Array of sound identifiers
    int* sound_indices;             // Mapping from identifiers to sound array indices
    
    // Sound pools for variations
    SoundPool* sound_pools;         // Pools of similar sounds for variation
    int pool_count;                 // Number of sound pools
    
    // Settings
    bool sounds_enabled;            // Global toggle for sound effects
    int max_concurrent_sounds;      // Maximum number of sounds playing simultaneously
    
    // Spatial audio
    Vector2 listener_position;      // Position of the audio listener (usually camera)
    float distance_model_scale;     // Scaling factor for distance-based attenuation
} SoundManager;
```

### Music Manager Structure

```c
typedef struct MusicManager {
    // Currently loaded music
    Music* music_tracks;            // Array of loaded music tracks
    int music_count;                // Number of loaded tracks
    int music_capacity;             // Maximum number of tracks
    
    // Playback control
    int current_track_index;        // Index of currently playing track
    bool is_playing;                // Whether music is currently playing
    float play_time;                // Current play position in seconds
    
    // Playlists
    char*** playlists;              // Array of playlists (each playlist is array of track names)
    int* playlist_lengths;          // Length of each playlist
    int playlist_count;             // Number of playlists
    int current_playlist;           // Currently active playlist
    
    // Transition control
    bool crossfading;               // Whether a crossfade is in progress
    int fade_track_index;           // Index of track being faded in/out
    float fade_duration;            // Duration of current fade in seconds
    float fade_progress;            // Progress of current fade (0.0-1.0)
    
    // Volume control
    float music_volume;             // Music volume multiplier (0.0-1.0)
    
    // Settings
    bool music_enabled;             // Global toggle for music
    bool shuffle_playlist;          // Whether to shuffle playlist when playing
    bool auto_advance;              // Whether to automatically advance to next track
} MusicManager;
```

### Sound Pool Structure

```c
typedef struct SoundPool {
    char name[64];                  // Name identifier for the pool
    Sound* sounds;                  // Array of similar sound variations
    int count;                      // Number of sounds in the pool
    int last_played;                // Index of the last played sound (to avoid repeats)
    float min_interval;             // Minimum time between playing sounds from this pool
    float last_play_time;           // When the last sound was played
} SoundPool;
```

## Core Functions

### Sound Effects Functions

```c
// Initialization and cleanup
SoundManager* InitSoundManager(int max_sounds);
void DestroySoundManager(SoundManager* manager);

// Sound loading
int LoadSound(SoundManager* manager, const char* name, const char* filename);
int LoadSoundFromMemory(SoundManager* manager, const char* name, const void* data, int data_size);
void UnloadSound(SoundManager* manager, const char* name);

// Sound pools
int CreateSoundPool(SoundManager* manager, const char* name, float min_interval);
void AddSoundToPool(SoundManager* manager, const char* pool_name, const char* sound_name);
int PlaySoundFromPool(SoundManager* manager, const char* pool_name);

// Sound playback
int PlaySound(SoundManager* manager, const char* name);
int PlaySoundWithVolume(SoundManager* manager, const char* name, float volume);
int PlaySoundWithPan(SoundManager* manager, const char* name, float pan);
int PlaySoundAt(SoundManager* manager, const char* name, Vector2 position, float max_distance);
void StopSound(SoundManager* manager, int sound_id);
void StopAllSounds(SoundManager* manager);

// Volume control
void SetMasterVolume(SoundManager* manager, float volume);
void SetSFXVolume(SoundManager* manager, float volume);
void SetUIVolume(SoundManager* manager, float volume);
```

### Music Functions

```c
// Initialization and cleanup
MusicManager* InitMusicManager(int max_tracks);
void DestroyMusicManager(MusicManager* manager);

// Music loading
int LoadMusic(MusicManager* manager, const char* name, const char* filename);
void UnloadMusic(MusicManager* manager, const char* name);

// Playlist management
int CreatePlaylist(MusicManager* manager, const char* name);
void AddTrackToPlaylist(MusicManager* manager, int playlist_id, const char* track_name);
void SetCurrentPlaylist(MusicManager* manager, int playlist_id);
void ShuffleCurrentPlaylist(MusicManager* manager);

// Music playback
void PlayMusic(MusicManager* manager, const char* name);
void PlayMusicFadeIn(MusicManager* manager, const char* name, float fade_duration);
void StopMusic(MusicManager* manager);
void StopMusicFadeOut(MusicManager* manager, float fade_duration);
void PauseMusic(MusicManager* manager);
void ResumeMusic(MusicManager* manager);
void PlayNextTrack(MusicManager* manager);
void PlayPreviousTrack(MusicManager* manager);

// Volume control
void SetMusicVolume(MusicManager* manager, float volume);
```

### Unified Audio System Functions

```c
// Complete audio system
typedef struct AudioSystem {
    SoundManager* sound_manager;
    MusicManager* music_manager;
} AudioSystem;

// Initialization and update
AudioSystem* InitAudioSystem();
void UpdateAudioSystem(AudioSystem* system, float delta_time);
void DestroyAudioSystem(AudioSystem* system);

// Common operations
void MuteAll(AudioSystem* system);
void UnmuteAll(AudioSystem* system);
void PauseAll(AudioSystem* system);
void ResumeAll(AudioSystem* system);
```

## Sound Categories and Preloading

The Sound System will include predefined categories for sound effects to simplify usage across the game:

```c
// Sound category definitions
typedef enum SoundCategory {
    SOUND_CATEGORY_UI,          // UI interaction sounds
    SOUND_CATEGORY_GAMEPLAY,    // Gameplay-related sounds
    SOUND_CATEGORY_AMBIENT,     // Ambient/environment sounds
    SOUND_CATEGORY_PLAYER,      // Player-specific sounds
    SOUND_CATEGORY_BLOCKS,      // Block-related sounds
    SOUND_CATEGORY_EFFECTS,     // Visual effect sounds
    SOUND_CATEGORY_POWERUPS     // Powerup-related sounds
} SoundCategory;

// Preload common sounds
void PreloadCommonSounds(SoundManager* manager);
```

### Predefined Sound Pools

The Sound System will include predefined sound pools for common game events:

```c
// Initialize standard sound pools
void InitializeStandardSoundPools(SoundManager* manager) {
    // Create standard sound pools
    CreateSoundPool(manager, "powerup", 0.1f);
    CreateSoundPool(manager, "explosion", 0.05f);
    CreateSoundPool(manager, "block_hit", 0.02f);
    CreateSoundPool(manager, "block_break", 0.02f);
    CreateSoundPool(manager, "ball_bounce", 0.02f);
    
    // Add sounds to the pools
    AddSoundToPool(manager, "powerup", "powerup1");
    AddSoundToPool(manager, "powerup", "powerup2");
    AddSoundToPool(manager, "powerup", "powerup3");
    AddSoundToPool(manager, "powerup", "powerup4");
    
    AddSoundToPool(manager, "explosion", "explosion1");
    AddSoundToPool(manager, "explosion", "explosion2");
    AddSoundToPool(manager, "explosion", "explosion3");
    AddSoundToPool(manager, "explosion", "explosion4");
    
    // ... Add more sounds to other pools
}
```

## Music System Features

### Playlist System

The Music System will include a playlist system to manage different music sets for various game states:

```c
// Standard playlists
void InitializeStandardPlaylists(MusicManager* manager) {
    // Title screen music
    int title_playlist = CreatePlaylist(manager, "title");
    AddTrackToPlaylist(manager, title_playlist, "title_track1");
    AddTrackToPlaylist(manager, title_playlist, "title_track2");
    AddTrackToPlaylist(manager, title_playlist, "title_track3");
    
    // Gameplay music
    int game_playlist = CreatePlaylist(manager, "game");
    AddTrackToPlaylist(manager, game_playlist, "game_track1");
    AddTrackToPlaylist(manager, game_playlist, "game_track2");
    AddTrackToPlaylist(manager, game_playlist, "game_track3");
    AddTrackToPlaylist(manager, game_playlist, "game_track4");
    
    // Post-game music
    int postgame_playlist = CreatePlaylist(manager, "postgame");
    AddTrackToPlaylist(manager, postgame_playlist, "postgame_track1");
    AddTrackToPlaylist(manager, postgame_playlist, "postgame_track2");
    
    // Post-match music
    int postmatch_playlist = CreatePlaylist(manager, "postmatch");
    AddTrackToPlaylist(manager, postmatch_playlist, "postmatch_track1");
    AddTrackToPlaylist(manager, postmatch_playlist, "postmatch_track2");
}
```

### Music Transitions

The Music System will support smooth transitions between tracks:

```c
// Transition types
typedef enum MusicTransitionType {
    TRANSITION_NONE,           // Instant switch
    TRANSITION_CROSSFADE,      // Smooth crossfade
    TRANSITION_FADE_OUT_IN     // Fade out then fade in
} MusicTransitionType;

// Transition functions
void TransitionToTrack(MusicManager* manager, const char* track_name, MusicTransitionType transition, float duration);
void TransitionToPlaylist(MusicManager* manager, const char* playlist_name, MusicTransitionType transition, float duration);
```

## Spatial Audio Support

The Sound System will include support for positional audio:

```c
// Set listener position (usually camera position)
void SetListenerPosition(SoundManager* manager, Vector2 position);

// Play sound with position parameters
int PlaySoundAt(SoundManager* manager, const char* name, Vector2 position, float max_distance);

// Set distance model
void SetDistanceModel(SoundManager* manager, float scale);
```

## Integration with Settings System

The Sound System will be integrated with the Settings System to allow users to adjust audio settings:

```c
// Apply settings to sound system
void ApplySoundSettings(AudioSystem* system, SettingsManager* settings_manager);

// Settings callback functions
void OnMasterVolumeChanged(Setting* setting, AudioSystem* system);
void OnSFXVolumeChanged(Setting* setting, AudioSystem* system);
void OnMusicVolumeChanged(Setting* setting, AudioSystem* system);
void OnSoundEnabledChanged(Setting* setting, AudioSystem* system);
void OnMusicEnabledChanged(Setting* setting, AudioSystem* system);
```

## Game Integration Helpers

Functions to simplify the integration of sounds with game elements:

```c
// UI sound helpers
void PlayUISelectSound(SoundManager* manager);
void PlayUIConfirmSound(SoundManager* manager);
void PlayUIBackSound(SoundManager* manager);
void PlayUIErrorSound(SoundManager* manager);

// Gameplay sound helpers
void PlayBallBounceSound(SoundManager* manager, Vector2 position);
void PlayBlockHitSound(SoundManager* manager, Vector2 position);
void PlayBlockBreakSound(SoundManager* manager, Vector2 position);
void PlayPowerupCollectSound(SoundManager* manager, Vector2 position);
void PlayExplosionSound(SoundManager* manager, Vector2 position);

// Effect sound helpers
void PlayBurningSound(SoundManager* manager, Vector2 position);
void PlayFreezingSound(SoundManager* manager, Vector2 position);
void PlayElectricitySound(SoundManager* manager, Vector2 position);
```

## Performance Optimization

### Sound Prioritization

```c
// Set sound priority levels
typedef enum SoundPriority {
    PRIORITY_LOW,
    PRIORITY_MEDIUM,
    PRIORITY_HIGH,
    PRIORITY_CRITICAL
} SoundPriority;

// Play sound with priority
int PlaySoundWithPriority(SoundManager* manager, const char* name, SoundPriority priority);

// Internal prioritization system
void UpdateSoundPriorities(SoundManager* manager);
```

### Resource Management

```c
// Memory management
void TrimUnusedSounds(SoundManager* manager);
void PrecacheSounds(SoundManager* manager, const char** sound_names, int count);

// Streaming for large music files
void EnableMusicStreaming(MusicManager* manager, const char* track_name);
```

## Debugging Support

```c
// Debug visualization and monitoring
void DrawSoundDebug(SoundManager* manager, Rectangle bounds);
void DrawMusicDebug(MusicManager* manager, Rectangle bounds);
void LogAudioSystemStatus(AudioSystem* system);
```

## Error Handling

```c
// Error reporting and recovery
typedef enum AudioErrorCode {
    AUDIO_ERROR_NONE,
    AUDIO_ERROR_FILE_NOT_FOUND,
    AUDIO_ERROR_UNSUPPORTED_FORMAT,
    AUDIO_ERROR_OUT_OF_MEMORY,
    AUDIO_ERROR_DEVICE_BUSY,
    AUDIO_ERROR_DEVICE_NOT_AVAILABLE
} AudioErrorCode;

// Error handling functions
AudioErrorCode GetLastAudioError(AudioSystem* system);
const char* GetAudioErrorString(AudioErrorCode error);
void RegisterAudioErrorCallback(AudioSystem* system, void (*callback)(AudioErrorCode, const char*));
```

## Implementation Notes

1. **Raylib Integration**: The Sound System will utilize Raylib's audio functions for loading and playing sounds, with additional management layers for more complex features.

2. **Memory Management**: Sounds will be pre-loaded when possible and managed efficiently to minimize loading during gameplay.

3. **Concurrent Sound Limitations**: The system will manage the number of concurrent sounds to prevent audio distortion or performance issues.

4. **Music Transitions**: Smooth transitions between music tracks will be implemented using volume fading and timing controls.

5. **Thread Safety**: The audio system will ensure thread-safe operations for background music loading and streaming.

6. **Resource Optimization**: Sound files will be compressed and optimized for size while maintaining quality.

7. **Fallback Mechanisms**: The system will include fallback mechanisms for handling missing audio files or unsupported formats.

## Conclusion

The Sound System specification for the C/Raylib port builds upon the existing Python/Pygame implementation while enhancing it with additional features and optimizations. The design provides a flexible, efficient way to manage game audio, with separate systems for sound effects and music. The integration with the Settings System ensures that players can adjust audio settings based on their preferences, while the performance optimizations ensure smooth playback across different hardware capabilities. 