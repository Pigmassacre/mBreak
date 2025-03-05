#include "screens.h"
#include "font.h"
#include <stdlib.h>

// Global screen variable definitions
Screen ScreenLogo;
Screen ScreenSplash;
Screen ScreenMainMenu;
Screen ScreenPrepareMenu;
Screen ScreenGameplay;
Screen ScreenGameOver;
Screen ScreenOptions;

// External reference to virtualScreen created in main.c
extern RenderTexture2D virtualScreen;

// External declarations for initialization functions implemented in other files
// These functions are defined in their respective module files
extern Screen InitSplashScreen(void);
extern Screen InitMainMenuScreen(void);
extern Screen InitGameplayScreen(void);

// Generic screen function implementations

void InitScreen(Screen *screen) {
    if (screen->init) {
        screen->init();
    }
    screen->finishScreen = false;
}

void UpdateScreen(Screen *screen, float deltaTime) {
    if (screen->update) {
        screen->update(deltaTime);
    }
}

void DrawScreen(Screen *screen) {
    if (screen->draw) {
        screen->draw();
    }
}

void UnloadScreen(Screen *screen) {
    if (screen->unload) {
        screen->unload();
    }
}

GameScreen GetNextScreen(Screen *screen) {
    if (screen->getNextScreen) {
        return screen->getNextScreen();
    }
    return screen->nextScreen;
}

void SetNextScreen(Screen *screen, GameScreen nextScreen) {
    screen->nextScreen = nextScreen;
}

void FinishScreen(Screen *screen) {
    screen->finishScreen = true;
}

// Logo screen function implementations (placeholder)
static void LogoInit(void) {
    // TODO: Initialize logo screen resources
}

static void LogoUpdate(float deltaTime) {
    // TODO: Update logo screen logic
    // Automatically transition to splash screen after a few seconds
    static float logoTimer = 0.0f;
    logoTimer += deltaTime;
    
    // Transition after 2 seconds
    if (logoTimer > 2.0f) {
        // Use the global ScreenLogo variable
        ScreenLogo.finishScreen = true;
    }
}

static void LogoDraw(void) {
    DrawTextEx(gameFont, "LOGO SCREEN", (Vector2){20, 20}, 30, 1, WHITE);
    
    const char* poweredText = "POWERED BY RAYLIB";
    Vector2 textSize = MeasureTextEx(gameFont, poweredText, 20, 1);
    DrawTextEx(gameFont, poweredText, 
              (Vector2){GAME_WIDTH/2 - textSize.x/2, GAME_HEIGHT/2}, 
              20, 1, GRAY);
}

static void LogoUnload(void) {
    // TODO: Unload logo screen resources
}

static GameScreen LogoGetNextScreen(void) {
    return SPLASH;
}

// Only define the Logo screen initialization here (others are in their own files)
Screen InitLogoScreen(void) {
    Screen screen = {0};
    screen.init = LogoInit;
    screen.update = LogoUpdate;
    screen.draw = LogoDraw;
    screen.unload = LogoUnload;
    screen.getNextScreen = LogoGetNextScreen;
    screen.finishScreen = false;
    screen.nextScreen = LOGO;
    return screen;
}

// Shim implementations for screens not yet implemented
// These are temporary implementations to satisfy the linker

// Prepare Menu Screen shim
Screen InitPrepareMenuScreen(void) {
    Screen screen = {0};
    screen.init = NULL;
    screen.update = NULL;
    screen.draw = NULL;
    screen.unload = NULL;
    screen.getNextScreen = NULL;
    screen.finishScreen = false;
    screen.nextScreen = GAMEPLAY;
    return screen;
}

// Game Over Screen shim
Screen InitGameOverScreen(void) {
    Screen screen = {0};
    screen.init = NULL;
    screen.update = NULL;
    screen.draw = NULL;
    screen.unload = NULL;
    screen.getNextScreen = NULL;
    screen.finishScreen = false;
    screen.nextScreen = MAIN_MENU;
    return screen;
}

// Options Screen shim
Screen InitOptionsScreen(void) {
    Screen screen = {0};
    screen.init = NULL;
    screen.update = NULL;
    screen.draw = NULL;
    screen.unload = NULL;
    screen.getNextScreen = NULL;
    screen.finishScreen = false;
    screen.nextScreen = MAIN_MENU;
    return screen;
}

// The rest of the initialization functions are defined in their respective files
// and should NOT be defined here to avoid duplicate definition errors 
