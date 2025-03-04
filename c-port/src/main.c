#include "raylib.h"
#include "../include/screens.h"
#include <stdlib.h>
#include <stdio.h>

// Default window dimensions (will be configurable later)
#define DEFAULT_SCREEN_WIDTH 800
#define DEFAULT_SCREEN_HEIGHT 600
#define GAME_TITLE "mBreak"

// Main entry point
int main(void) {
    // Initialize window and core systems
    InitWindow(DEFAULT_SCREEN_WIDTH, DEFAULT_SCREEN_HEIGHT, GAME_TITLE);
    InitAudioDevice();
    
    // Set target FPS (60 by default)
    SetTargetFPS(60);
    
    // Initialize timing variables for delta time calculation
    double previousTime = GetTime();
    double currentTime = 0;
    float deltaTime = 0;
    
    // Initialize global screen variables
    ScreenLogo = InitLogoScreen();
    ScreenSplash = InitSplashScreen();
    ScreenMainMenu = InitMainMenuScreen();
    ScreenPrepareMenu = InitPrepareMenuScreen();
    ScreenGameplay = InitGameplayScreen();
    ScreenGameOver = InitGameOverScreen();
    ScreenOptions = InitOptionsScreen();
    
    // Initialize current screen
    GameScreen currentScreenType = LOGO;
    Screen *currentScreen = &ScreenLogo;
    InitScreen(currentScreen);
    
    // Main game loop
    while (!WindowShouldClose()) {
        // Update delta time
        currentTime = GetTime();
        deltaTime = (float)(currentTime - previousTime);
        previousTime = currentTime;
        
        // Update current screen
        UpdateScreen(currentScreen, deltaTime);
        
        // Check if screen should change
        if (currentScreen->finishScreen) {
            // Get next screen
            currentScreenType = GetNextScreen(currentScreen);
            
            // Reset finish flag
            currentScreen->finishScreen = false;
            
            // Switch to next screen
            switch (currentScreenType) {
                case LOGO:
                    currentScreen = &ScreenLogo;
                    break;
                case SPLASH:
                    currentScreen = &ScreenSplash;
                    break;
                case MAIN_MENU:
                    currentScreen = &ScreenMainMenu;
                    break;
                case PREPARE_MENU:
                    currentScreen = &ScreenPrepareMenu;
                    break;
                case GAMEPLAY:
                    currentScreen = &ScreenGameplay;
                    break;
                case GAME_OVER:
                    currentScreen = &ScreenGameOver;
                    break;
                case OPTIONS:
                    currentScreen = &ScreenOptions;
                    break;
                default:
                    break;
            }
            
            // Initialize new screen
            InitScreen(currentScreen);
        }
        
        // Draw current screen
        BeginDrawing();
            ClearBackground(BLACK);
            
            DrawScreen(currentScreen);
            
            // Display FPS for debugging (will be configurable later)
            DrawFPS(10, 10);
            
        EndDrawing();
    }
    
    // Unload all screens before closing
    UnloadScreen(&ScreenLogo);
    UnloadScreen(&ScreenSplash);
    UnloadScreen(&ScreenMainMenu);
    UnloadScreen(&ScreenPrepareMenu);
    UnloadScreen(&ScreenGameplay);
    UnloadScreen(&ScreenGameOver);
    UnloadScreen(&ScreenOptions);
    
    // Cleanup and close resources
    CloseAudioDevice();
    CloseWindow();
    
    return 0;
} 