/**
 * @file logo.c
 * @brief Implementation of the Logo UI component.
 */

#include "ui/logo.h"
#include <stdlib.h>
#include <math.h>  // For floorf

// Default scale for the logo
#define LOGO_DEFAULT_SCALE 2.0f

// Animation frame definitions
typedef struct {
    const char* path;
    float duration;
} LogoFrameDefinition;

// Define the animation frames
static const LogoFrameDefinition LOGO_FRAMES[] = {
    {"resources/logo/mBreakTitle_01.png", 1550.0f},
    {"resources/logo/mBreakTitle_02.png", 75.0f},
    {"resources/logo/mBreakTitle_03.png", 75.0f},
    {"resources/logo/mBreakTitle_04.png", 75.0f},
    {"resources/logo/mBreakTitle_05.png", 75.0f},
    {"resources/logo/mBreakTitle_06.png", 75.0f},
    {"resources/logo/mBreakTitle_07.png", 75.0f},
    {"resources/logo/mBreakTitle_01.png", 1550.0f},
    {"resources/logo/mBreakTitle_07.png", 75.0f},
    {"resources/logo/mBreakTitle_06.png", 75.0f},
    {"resources/logo/mBreakTitle_05.png", 75.0f},
    {"resources/logo/mBreakTitle_04.png", 75.0f},
    {"resources/logo/mBreakTitle_03.png", 75.0f},
    {"resources/logo/mBreakTitle_02.png", 75.0f}
};

// Number of frames in the animation
#define LOGO_FRAME_COUNT (sizeof(LOGO_FRAMES) / sizeof(LOGO_FRAMES[0]))

Logo InitLogo(void) {
    Logo logo;
    
    // Initialize position
    logo.x = 0;
    logo.y = 0;
    
    // Initialize scale
    logo.scale = LOGO_DEFAULT_SCALE;
    
    // Initialize animation state
    logo.current_frame = 0;
    logo.time_accumulator = 0;
    logo.playing = false;
    logo.paused = false;
    
    // Allocate memory for frames
    logo.frame_count = LOGO_FRAME_COUNT;
    logo.frames = (LogoFrame*)malloc(logo.frame_count * sizeof(LogoFrame));
    
    // Initialize maximum dimensions
    logo.max_width = 0;
    logo.max_height = 0;
    
    // Load all frames
    for (int i = 0; i < logo.frame_count; i++) {
        logo.frames[i].texture = LoadTexture(LOGO_FRAMES[i].path);
        logo.frames[i].duration = LOGO_FRAMES[i].duration;
        
        // Set texture filter to point (nearest-neighbor) for pixel-perfect rendering
        SetTextureFilter(logo.frames[i].texture, TEXTURE_FILTER_POINT);
        
        // Update maximum dimensions
        if (logo.frames[i].texture.width > logo.max_width) {
            logo.max_width = (float)logo.frames[i].texture.width;
        }
        if (logo.frames[i].texture.height > logo.max_height) {
            logo.max_height = (float)logo.frames[i].texture.height;
        }
    }
    
    return logo;
}

void UnloadLogo(Logo* logo) {
    // Unload all frame textures
    for (int i = 0; i < logo->frame_count; i++) {
        UnloadTexture(logo->frames[i].texture);
    }
    
    // Free the frames array
    free(logo->frames);
    logo->frames = NULL;
    logo->frame_count = 0;
}

void PlayLogo(Logo* logo) {
    logo->playing = true;
    logo->paused = false;
}

void PauseLogo(Logo* logo) {
    logo->paused = true;
}

void StopLogo(Logo* logo) {
    logo->playing = false;
    logo->paused = false;
    logo->current_frame = 0;
    logo->time_accumulator = 0;
}

float GetLogoWidth(const Logo* logo) {
    return logo->max_width * logo->scale;
}

float GetLogoHeight(const Logo* logo) {
    return logo->max_height * logo->scale;
}

void UpdateLogo(Logo* logo, float delta_time) {
    // Only update if playing and not paused
    if (logo->playing && !logo->paused) {
        // Accumulate time
        logo->time_accumulator += delta_time * 1000.0f; // Convert to milliseconds
        
        // Check if it's time to advance to the next frame
        if (logo->time_accumulator >= logo->frames[logo->current_frame].duration) {
            // Subtract the duration of the current frame
            logo->time_accumulator -= logo->frames[logo->current_frame].duration;
            
            // Advance to the next frame
            logo->current_frame = (logo->current_frame + 1) % logo->frame_count;
        }
    }
}

void DrawLogo(const Logo* logo) {
    // Get the current frame texture
    Texture2D texture = logo->frames[logo->current_frame].texture;
    
    // Define source and destination rectangles for pixel-perfect rendering
    Rectangle source = { 
        0.0f, 
        0.0f, 
        (float)texture.width, 
        (float)texture.height 
    };
    
    // Ensure we're drawing at integer pixel positions to avoid sub-pixel rendering issues
    Rectangle dest = { 
        floorf(logo->x), 
        floorf(logo->y), 
        (float)texture.width * logo->scale, 
        (float)texture.height * logo->scale
    };
    
    // Draw using DrawTexturePro for more precise rendering control
    DrawTexturePro(texture, source, dest, (Vector2){ 0, 0 }, 0, WHITE);
} 