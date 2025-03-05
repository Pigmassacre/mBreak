#ifndef SCREENS_H
#define SCREENS_H

#include "raylib.h"

// Game dimensions (fixed internal resolution)
#define GAME_WIDTH 570
#define GAME_HEIGHT 320

// Level dimensions (from Python version)
#define LEVEL_WIDTH 176
#define LEVEL_HEIGHT 120
#define LEVEL_X ((GAME_WIDTH - LEVEL_WIDTH) / 2)
#define LEVEL_Y ((GAME_HEIGHT - LEVEL_HEIGHT) / 2)
#define LEVEL_MAX_X (LEVEL_X + LEVEL_WIDTH)
#define LEVEL_MAX_Y (LEVEL_Y + LEVEL_HEIGHT)

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

// Render texture for virtual screen (game canvas)
extern RenderTexture2D virtualScreen;

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