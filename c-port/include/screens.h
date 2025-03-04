#ifndef SCREENS_H
#define SCREENS_H

#include "raylib.h"

// Screen type enumeration
typedef enum GameScreen {
    LOGO = 0,
    SPLASH,
    MAIN_MENU,
    PREPARE_MENU,
    GAMEPLAY,
    GAME_OVER,
    OPTIONS
} GameScreen;

// Generic screen data structure
typedef struct Screen {
    void (*init)(void);                // Initialize screen resources
    void (*update)(float deltaTime);   // Update screen logic
    void (*draw)(void);                // Draw screen
    void (*unload)(void);              // Unload screen resources
    GameScreen (*getNextScreen)(void); // Get next screen to transition to
    bool finishScreen;                 // Screen finalization status
    GameScreen nextScreen;             // Next screen to transition to
} Screen;

// Global screen variables (extern declarations)
extern Screen ScreenLogo;
extern Screen ScreenSplash;
extern Screen ScreenMainMenu;
extern Screen ScreenPrepareMenu;
extern Screen ScreenGameplay;
extern Screen ScreenGameOver;
extern Screen ScreenOptions;

// Screen function prototypes
void InitScreen(Screen *screen);
void UpdateScreen(Screen *screen, float deltaTime);
void DrawScreen(Screen *screen);
void UnloadScreen(Screen *screen);
GameScreen GetNextScreen(Screen *screen);
void SetNextScreen(Screen *screen, GameScreen nextScreen);
void FinishScreen(Screen *screen);

// Screen-specific initialization functions
Screen InitLogoScreen(void);
Screen InitSplashScreen(void);
Screen InitMainMenuScreen(void);
Screen InitPrepareMenuScreen(void);
Screen InitGameplayScreen(void);
Screen InitGameOverScreen(void);
Screen InitOptionsScreen(void);

#endif // SCREENS_H 