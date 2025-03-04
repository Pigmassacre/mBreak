#include "../include/screens.h"
#include <stdlib.h>

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
        ScreenLogo.finishScreen = true;
    }
}

static void LogoDraw(void) {
    DrawText("LOGO SCREEN", 20, 20, 30, WHITE);
    DrawText("POWERED BY RAYLIB", GetScreenWidth()/2 - MeasureText("POWERED BY RAYLIB", 20)/2, 
             GetScreenHeight()/2, 20, GRAY);
}

static void LogoUnload(void) {
    // TODO: Unload logo screen resources
}

static GameScreen LogoGetNextScreen(void) {
    return SPLASH;
}

// Global screen instances
static Screen ScreenLogo;
static Screen ScreenSplash;
static Screen ScreenMainMenu;
static Screen ScreenPrepareMenu;
static Screen ScreenGameplay;
static Screen ScreenGameOver;
static Screen ScreenOptions;

// Screen initialization functions

Screen InitLogoScreen(void) {
    ScreenLogo = (Screen){
        .init = LogoInit,
        .update = LogoUpdate,
        .draw = LogoDraw,
        .unload = LogoUnload,
        .getNextScreen = LogoGetNextScreen,
        .finishScreen = false,
        .nextScreen = SPLASH
    };
    
    return ScreenLogo;
}

Screen InitSplashScreen(void) {
    // TODO: Implement splash screen
    ScreenSplash = (Screen){
        .init = NULL,
        .update = NULL,
        .draw = NULL,
        .unload = NULL,
        .getNextScreen = NULL,
        .finishScreen = false,
        .nextScreen = MAIN_MENU
    };
    
    return ScreenSplash;
}

Screen InitMainMenuScreen(void) {
    // TODO: Implement main menu screen
    ScreenMainMenu = (Screen){
        .init = NULL,
        .update = NULL,
        .draw = NULL,
        .unload = NULL,
        .getNextScreen = NULL,
        .finishScreen = false,
        .nextScreen = GAMEPLAY
    };
    
    return ScreenMainMenu;
}

Screen InitPrepareMenuScreen(void) {
    // TODO: Implement prepare menu screen
    ScreenPrepareMenu = (Screen){
        .init = NULL,
        .update = NULL,
        .draw = NULL,
        .unload = NULL,
        .getNextScreen = NULL,
        .finishScreen = false,
        .nextScreen = GAMEPLAY
    };
    
    return ScreenPrepareMenu;
}

Screen InitGameplayScreen(void) {
    // TODO: Implement gameplay screen
    ScreenGameplay = (Screen){
        .init = NULL,
        .update = NULL,
        .draw = NULL,
        .unload = NULL,
        .getNextScreen = NULL,
        .finishScreen = false,
        .nextScreen = GAME_OVER
    };
    
    return ScreenGameplay;
}

Screen InitGameOverScreen(void) {
    // TODO: Implement game over screen
    ScreenGameOver = (Screen){
        .init = NULL,
        .update = NULL,
        .draw = NULL,
        .unload = NULL,
        .getNextScreen = NULL,
        .finishScreen = false,
        .nextScreen = MAIN_MENU
    };
    
    return ScreenGameOver;
}

Screen InitOptionsScreen(void) {
    // TODO: Implement options screen
    ScreenOptions = (Screen){
        .init = NULL,
        .update = NULL,
        .draw = NULL,
        .unload = NULL,
        .getNextScreen = NULL,
        .finishScreen = false,
        .nextScreen = MAIN_MENU
    };
    
    return ScreenOptions;
} 