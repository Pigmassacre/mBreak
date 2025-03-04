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
    
    // Initialize current screen
    GameScreen currentScreenType = LOGO;
    Screen currentScreen = InitLogoScreen();
    InitScreen(&currentScreen);
    
    // Main game loop
    while (!WindowShouldClose()) {
        // Update delta time
        currentTime = GetTime();
        deltaTime = (float)(currentTime - previousTime);
        previousTime = currentTime;
        
        // Update current screen
        UpdateScreen(&currentScreen, deltaTime);
        
        // Check if screen should change
        if (currentScreen.finishScreen) {
            // Unload current screen
            UnloadScreen(&currentScreen);
            
            // Load next screen
            currentScreenType = GetNextScreen(&currentScreen);
            
            switch (currentScreenType) {
                case LOGO:
                    currentScreen = InitLogoScreen();
                    break;
                case SPLASH:
                    currentScreen = InitSplashScreen();
                    break;
                case MAIN_MENU:
                    currentScreen = InitMainMenuScreen();
                    break;
                case PREPARE_MENU:
                    currentScreen = InitPrepareMenuScreen();
                    break;
                case GAMEPLAY:
                    currentScreen = InitGameplayScreen();
                    break;
                case GAME_OVER:
                    currentScreen = InitGameOverScreen();
                    break;
                case OPTIONS:
                    currentScreen = InitOptionsScreen();
                    break;
                default:
                    break;
            }
            
            // Initialize new screen
            InitScreen(&currentScreen);
        }
        
        // Draw current screen
        BeginDrawing();
            ClearBackground(BLACK);
            
            DrawScreen(&currentScreen);
            
            // Display FPS for debugging (will be configurable later)
            DrawFPS(10, 10);
            
        EndDrawing();
    }
    
    // Unload current screen before closing
    UnloadScreen(&currentScreen);
    
    // Cleanup and close resources
    CloseAudioDevice();
    CloseWindow();
    
    return 0;
} 