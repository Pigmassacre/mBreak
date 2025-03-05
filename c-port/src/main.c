#include <stdio.h>
#include "screens.h"
#include "raylib.h"
#include <stdlib.h>

// Default window dimensions (can be changed by user)
#define DEFAULT_SCREEN_WIDTH 855
#define DEFAULT_SCREEN_HEIGHT 480
#define GAME_TITLE "mBreak"

// Global font variable
Font gameFont;

// Global virtual screen (render texture)
RenderTexture2D virtualScreen;

// Main entry point
int main(void) {
    // Initialize window with resizing support
    SetConfigFlags(FLAG_WINDOW_RESIZABLE);
    InitWindow(DEFAULT_SCREEN_WIDTH, DEFAULT_SCREEN_HEIGHT, GAME_TITLE);
    InitAudioDevice();
    
    // Set minimum window size
    SetWindowMinSize(GAME_WIDTH, GAME_HEIGHT);
    
    // Set target FPS (60 by default)
    SetTargetFPS(60);
    
    // Load the game font (bitmap font)
    // Make sure the path is relative to the executable location
    // Both the .fnt and .png files must be in the same directory
    gameFont = LoadFont("resources/fonts/PaintBasic.fnt");
    SetTextureFilter(gameFont.texture, TEXTURE_FILTER_POINT);  // For crisp pixel scaling
    
    // Create virtual screen (render texture) for fixed resolution gameplay
    virtualScreen = LoadRenderTexture(GAME_WIDTH, GAME_HEIGHT);
    SetTextureFilter(virtualScreen.texture, TEXTURE_FILTER_POINT);  // For crisp pixel scaling
    
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
        
        // Draw to virtual screen (fixed game resolution)
        BeginTextureMode(virtualScreen);
            ClearBackground(BLACK);
            DrawScreen(currentScreen);
        EndTextureMode();
        
        // Draw actual window (scaled)
        BeginDrawing();
            ClearBackground(BLACK);
            
            // Calculate scaling to maintain aspect ratio
            float scale = min(
                (float)GetScreenWidth() / GAME_WIDTH,
                (float)GetScreenHeight() / GAME_HEIGHT
            );
            
            // Calculate centered position
            int scaledWidth = (int)(GAME_WIDTH * scale);
            int scaledHeight = (int)(GAME_HEIGHT * scale);
            int posX = (GetScreenWidth() - scaledWidth) / 2;
            int posY = (GetScreenHeight() - scaledHeight) / 2;
            
            // Draw the scaled texture
            DrawTexturePro(
                virtualScreen.texture,
                (Rectangle){ 0, 0, (float)GAME_WIDTH, (float)-GAME_HEIGHT },
                (Rectangle){ (float)posX, (float)posY, (float)scaledWidth, (float)scaledHeight },
                (Vector2){ 0, 0 },
                0.0f,
                WHITE
            );
            
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
    
    // Unload the virtual screen and font
    UnloadRenderTexture(virtualScreen);
    UnloadFont(gameFont);
    
    // Cleanup and close resources
    CloseAudioDevice();
    CloseWindow();
    
    return 0;
} 