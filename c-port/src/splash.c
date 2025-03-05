#include "screens.h"
#include "font.h"
#include <stdlib.h>
#include <stdio.h>

// Splash screen state
typedef struct SplashState {
    float timer;
    float alpha;
    bool fadeOut;
} SplashState;

// Static splash state
static SplashState splashState;

// Function declarations
static void InitSplash(void);
static void UpdateSplash(float deltaTime);
static void DrawSplash(void);
static void UnloadSplash(void);
static GameScreen GetNextSplashScreen(void);

// Initialize splash screen
static void InitSplash(void) {
    splashState.timer = 0.0f;
    splashState.alpha = 0.0f;
    splashState.fadeOut = false;
    
    printf("Splash screen initialized\n");
}

// Update splash screen logic
static void UpdateSplash(float deltaTime) {
    // Update timer
    splashState.timer += deltaTime;
    
    // Fade in effect
    if (!splashState.fadeOut) {
        splashState.alpha += deltaTime;
        
        // Start fade out after 2 seconds
        if (splashState.alpha >= 1.0f && splashState.timer >= 2.0f) {
            splashState.fadeOut = true;
        }
    }
    // Fade out effect
    else {
        splashState.alpha -= deltaTime;
        
        // Move to next screen when fade out is complete
        if (splashState.alpha <= 0.0f) {
            extern Screen ScreenSplash;
            ScreenSplash.finishScreen = true;
        }
    }
    
    // Clamp alpha value between 0 and 1
    if (splashState.alpha < 0.0f) splashState.alpha = 0.0f;
    if (splashState.alpha > 1.0f) splashState.alpha = 1.0f;
    
    // Skip splash screen if any key or mouse button is pressed
    if (IsKeyPressed(KEY_SPACE) || IsKeyPressed(KEY_ENTER) || IsMouseButtonPressed(MOUSE_LEFT_BUTTON)) {
        extern Screen ScreenSplash;
        ScreenSplash.finishScreen = true;
    }
}

// Draw splash screen elements
static void DrawSplash(void) {
    // Draw background
    DrawRectangle(0, 0, GAME_WIDTH, GAME_HEIGHT, BLACK);
    
    // Draw logo with fade effect
    int fontSize = 40; // Smaller font for the smaller render target
    const char* text = "mBREAK";
    
    Vector2 textSize = MeasureTextEx(gameFont, text, fontSize, 0);  // 0 spacing for bitmap font
    DrawTextEx(gameFont, text, 
             (Vector2){GAME_WIDTH/2 - textSize.x/2, 
             GAME_HEIGHT/2 - fontSize/2}, 
             fontSize, 
             0,  // 0 spacing for bitmap font
             ColorAlpha(BLUE, splashState.alpha));
    
    // Draw raylib logo
    const char* raylibText = "Powered by raylib";
    fontSize = 14; // Smaller font for the smaller render target
    textSize = MeasureTextEx(gameFont, raylibText, fontSize, 0);  // 0 spacing for bitmap font
    DrawTextEx(gameFont, raylibText, 
             (Vector2){GAME_WIDTH/2 - textSize.x/2, 
             GAME_HEIGHT/2 + 40}, 
             fontSize, 
             0,  // 0 spacing for bitmap font
             ColorAlpha(GRAY, splashState.alpha));
}

// Unload splash screen resources
static void UnloadSplash(void) {
    printf("Splash screen unloaded\n");
}

// Get next screen after splash
static GameScreen GetNextSplashScreen(void) {
    return MAIN_MENU;
}

// Screen initializer called by the screen management system
Screen InitSplashScreen(void) {
    // Create a local Screen structure and return it
    Screen screen = {
        .init = InitSplash,
        .update = UpdateSplash,
        .draw = DrawSplash,
        .unload = UnloadSplash,
        .getNextScreen = GetNextSplashScreen,
        .finishScreen = false,
        .nextScreen = MAIN_MENU
    };
    
    return screen;
} 
