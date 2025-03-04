#include "../include/screens.h"
#include <stdlib.h>
#include <stdio.h>

// Menu states
typedef enum MenuOption {
    MENU_PLAY = 0,
    MENU_OPTIONS,
    MENU_HELP,
    MENU_EXIT,
    MENU_COUNT
} MenuOption;

// Menu state
typedef struct MainMenuState {
    int selectedOption;
    bool optionSelected;
    GameScreen nextScreen;
    float frameCounter;
    float textBlink;
} MainMenuState;

// Static menu state
static MainMenuState menuState;

// Function declarations
static void InitMainMenu(void);
static void UpdateMainMenu(float deltaTime);
static void DrawMainMenu(void);
static void UnloadMainMenu(void);
static GameScreen GetNextMainMenuScreen(void);
static Rectangle GetMenuOptionBounds(const char* text, float y, float fontSize);

// Initialize main menu
static void InitMainMenu(void) {
    menuState.selectedOption = MENU_PLAY;
    menuState.optionSelected = false;
    menuState.nextScreen = MAIN_MENU;
    menuState.frameCounter = 0;
    menuState.textBlink = 0;
    
    printf("Main menu initialized\n");
}

// Update main menu logic
static void UpdateMainMenu(float deltaTime) {
    // Update timers
    menuState.frameCounter += deltaTime;
    menuState.textBlink = sinf(menuState.frameCounter * 4) * 0.5f + 0.5f;
    
    // Navigate menu options using up/down keys
    if (IsKeyPressed(KEY_UP)) {
        menuState.selectedOption--;
        if (menuState.selectedOption < 0) {
            menuState.selectedOption = MENU_COUNT - 1;
        }
    } else if (IsKeyPressed(KEY_DOWN)) {
        menuState.selectedOption++;
        if (menuState.selectedOption >= MENU_COUNT) {
            menuState.selectedOption = 0;
        }
    }
    
    // Select current option with enter/space
    if (IsKeyPressed(KEY_ENTER) || IsKeyPressed(KEY_SPACE)) {
        menuState.optionSelected = true;
        
        // Determine next screen based on selection
        switch (menuState.selectedOption) {
            case MENU_PLAY:
                menuState.nextScreen = GAMEPLAY;
                break;
            case MENU_OPTIONS:
                menuState.nextScreen = OPTIONS;
                break;
            case MENU_HELP:
                menuState.nextScreen = MAIN_MENU; // We'll stay in main menu for now
                break;
            case MENU_EXIT:
                // Signal that the window should close
                CloseWindow();
                break;
            default:
                menuState.nextScreen = MAIN_MENU;
                break;
        }
        
        // If we're not exiting, finish the screen to transition
        if (menuState.selectedOption != MENU_EXIT) {
            ScreenMainMenu.finishScreen = true;
        }
    }
    
    // Alternative navigation with mouse
    Vector2 mousePoint = GetMousePosition();
    
    // Check if mouse is over menu options
    for (int i = 0; i < MENU_COUNT; i++) {
        float y = GetScreenHeight() / 2 - 40 + i * 60;
        
        const char* optionText;
        switch (i) {
            case MENU_PLAY: optionText = "PLAY"; break;
            case MENU_OPTIONS: optionText = "OPTIONS"; break;
            case MENU_HELP: optionText = "HELP"; break;
            case MENU_EXIT: optionText = "EXIT"; break;
            default: optionText = ""; break;
        }
        
        Rectangle bounds = GetMenuOptionBounds(optionText, y, 30);
        
        // If mouse is over option, select it
        if (CheckCollisionPointRec(mousePoint, bounds)) {
            menuState.selectedOption = i;
            
            // If mouse is clicked, select the option
            if (IsMouseButtonPressed(MOUSE_LEFT_BUTTON)) {
                menuState.optionSelected = true;
                
                // Same logic as above for determining next screen
                switch (menuState.selectedOption) {
                    case MENU_PLAY:
                        menuState.nextScreen = GAMEPLAY;
                        ScreenMainMenu.finishScreen = true;
                        break;
                    case MENU_OPTIONS:
                        menuState.nextScreen = OPTIONS;
                        ScreenMainMenu.finishScreen = true;
                        break;
                    case MENU_HELP:
                        menuState.nextScreen = MAIN_MENU;
                        break;
                    case MENU_EXIT:
                        CloseWindow();
                        break;
                    default:
                        menuState.nextScreen = MAIN_MENU;
                        break;
                }
            }
        }
    }
}

// Draw main menu elements
static void DrawMainMenu(void) {
    // Draw background
    DrawRectangle(0, 0, GetScreenWidth(), GetScreenHeight(), BLACK);
    
    // Draw title
    int titleFontSize = 60;
    const char* titleText = "mBREAK";
    Vector2 titleSize = MeasureTextEx(GetFontDefault(), titleText, titleFontSize, 2);
    DrawText(titleText, GetScreenWidth()/2 - titleSize.x/2, 80, titleFontSize, BLUE);
    
    // Draw menu options
    for (int i = 0; i < MENU_COUNT; i++) {
        float y = GetScreenHeight() / 2 - 40 + i * 60;
        
        const char* optionText;
        switch (i) {
            case MENU_PLAY: optionText = "PLAY"; break;
            case MENU_OPTIONS: optionText = "OPTIONS"; break;
            case MENU_HELP: optionText = "HELP"; break;
            case MENU_EXIT: optionText = "EXIT"; break;
            default: optionText = ""; break;
        }
        
        // Draw selected option with highlight
        if (i == menuState.selectedOption) {
            Color highlightColor = ColorAlpha(WHITE, menuState.textBlink);
            Rectangle bounds = GetMenuOptionBounds(optionText, y, 30);
            DrawRectangleRec(bounds, ColorAlpha(BLUE, 0.3f));
            DrawRectangleLinesEx(bounds, 2, highlightColor);
            DrawText(optionText, GetScreenWidth()/2 - MeasureText(optionText, 30)/2, y, 30, WHITE);
        } else {
            DrawText(optionText, GetScreenWidth()/2 - MeasureText(optionText, 30)/2, y, 30, GRAY);
        }
    }
    
    // Draw version and copyright
    DrawText("Version 1.0", 20, GetScreenHeight() - 30, 20, DARKGRAY);
    DrawText("(C) 2025 mBreak Team", GetScreenWidth() - 240, GetScreenHeight() - 30, 20, DARKGRAY);
    
    // Draw controls hint
    DrawText("UP/DOWN + ENTER to select", GetScreenWidth()/2 - 160, GetScreenHeight() - 60, 20, LIGHTGRAY);
}

// Unload main menu resources
static void UnloadMainMenu(void) {
    printf("Main menu unloaded\n");
}

// Get next screen after main menu
static GameScreen GetNextMainMenuScreen(void) {
    return menuState.nextScreen;
}

// Calculate bounds for menu options (for mouse interaction)
static Rectangle GetMenuOptionBounds(const char* text, float y, float fontSize) {
    float width = MeasureText(text, fontSize) + 40;
    float height = fontSize + 20;
    float x = GetScreenWidth()/2 - width/2;
    
    return (Rectangle){ x, y - 10, width, height };
}

// Screen initializer called by the screen management system
Screen InitMainMenuScreen(void) {
    static Screen ScreenMainMenu;
    
    ScreenMainMenu = (Screen){
        .init = InitMainMenu,
        .update = UpdateMainMenu,
        .draw = DrawMainMenu,
        .unload = UnloadMainMenu,
        .getNextScreen = GetNextMainMenuScreen,
        .finishScreen = false,
        .nextScreen = GAMEPLAY
    };
    
    return ScreenMainMenu;
} 