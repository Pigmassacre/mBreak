/**
 * @file logo.h
 * @brief Logo component for UI.
 */

#ifndef LOGO_H
#define LOGO_H

#include "raylib.h"

/**
 * @brief Animation frame structure for the logo.
 */
typedef struct LogoFrame {
    Texture2D texture;
    float duration;  // Duration in milliseconds
} LogoFrame;

/**
 * @brief Logo structure for displaying the animated mBreak logo.
 * 
 * This class is used to create and display the animated mBreak logo.
 * It can be positioned anywhere, played, stopped, paused and more.
 */
typedef struct Logo {
    // Position
    float x;
    float y;
    
    // Scale
    float scale;
    
    // Animation frames
    LogoFrame* frames;
    int frame_count;
    
    // Animation state
    int current_frame;
    float time_accumulator;
    bool playing;
    bool paused;
    
    // Maximum dimensions (cached)
    float max_width;
    float max_height;
} Logo;

/**
 * @brief Initialize a Logo.
 * 
 * @return An initialized Logo.
 */
Logo InitLogo(void);

/**
 * @brief Clean up resources used by a Logo.
 * 
 * @param logo Pointer to the Logo to clean up.
 */
void UnloadLogo(Logo* logo);

/**
 * @brief Start playing the logo animation.
 * 
 * @param logo Pointer to the Logo.
 */
void PlayLogo(Logo* logo);

/**
 * @brief Pause the logo animation.
 * 
 * @param logo Pointer to the Logo.
 */
void PauseLogo(Logo* logo);

/**
 * @brief Stop the logo animation.
 * 
 * @param logo Pointer to the Logo.
 */
void StopLogo(Logo* logo);

/**
 * @brief Get the width of the logo.
 * 
 * @param logo Pointer to the Logo.
 * @return The width of the logo.
 */
float GetLogoWidth(const Logo* logo);

/**
 * @brief Get the height of the logo.
 * 
 * @param logo Pointer to the Logo.
 * @return The height of the logo.
 */
float GetLogoHeight(const Logo* logo);

/**
 * @brief Update the logo animation.
 * 
 * @param logo Pointer to the Logo to update.
 * @param delta_time The time passed since the last frame in seconds.
 */
void UpdateLogo(Logo* logo, float delta_time);

/**
 * @brief Draw the logo to the screen.
 * 
 * @param logo Pointer to the Logo to draw.
 */
void DrawLogo(const Logo* logo);

#endif // LOGO_H 