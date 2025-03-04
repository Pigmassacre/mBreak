#include "../include/screens.h"
#include <stdlib.h>
#include <stdio.h>
#include <math.h>

// Logo animation frames structure
typedef struct {
    Texture2D texture;
    float duration;
} LogoFrame;

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
    
    // Logo animation
    LogoFrame logoFrames[7];
    int currentLogoFrame;
    float logoFrameTime;
    bool logoAnimPlaying;
    
    // Logo position and transition
    Vector2 logoPosition;
    Vector2 logoDesiredPosition;
    float logoTransitionSpeed;
    
    // Menu transition
    bool menuVisible;
    Vector2 menuItemPositions[MENU_COUNT];
    Vector2 menuItemDesiredPositions[MENU_COUNT];
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
static void MoveItemToPosition(Vector2* itemPos, Vector2 desiredPos, float speed, float deltaTime);
static void SetupMenuTransition(void);

// Initialize main menu
static void InitMainMenu(void) {
    menuState.selectedOption = MENU_PLAY;
    menuState.optionSelected = false;
    menuState.nextScreen = MAIN_MENU;
    menuState.frameCounter = 0;
    menuState.textBlink = 0;
    
    // Load logo frames
    char frameFileName[64];
    for (int i = 0; i < 7; i++) {
        sprintf(frameFileName, "resources/logo/mBreakTitle_0%d.png", i+1);
        menuState.logoFrames[i].texture = LoadTexture(frameFileName);
        
        // Set durations matching the Python implementation
        if (i == 0 || i == 7) {
            menuState.logoFrames[i].duration = 1.55f; // 1550ms
        } else {
            menuState.logoFrames[i].duration = 0.075f; // 75ms
        }
    }
    
    // Initialize logo animation
    menuState.currentLogoFrame = 0;
    menuState.logoFrameTime = 0;
    menuState.logoAnimPlaying = true;
    
    // Set initial logo position (off-screen top)
    int logoWidth = menuState.logoFrames[0].texture.width;
    int logoHeight = menuState.logoFrames[0].texture.height;
    menuState.logoPosition = (Vector2){ (GetScreenWidth() - logoWidth * 2) / 2, -logoHeight * 2 };
    
    // Set desired logo position (top quarter of screen)
    menuState.logoDesiredPosition = (Vector2){ 
        (GetScreenWidth() - logoWidth * 2) / 2,
        (GetScreenHeight() - logoHeight * 2) / 4
    };
    
    // Set logo transition speed
    menuState.logoTransitionSpeed = 120 * 60 / 1000.0f; // Convert from pixels/second to pixels/frame at 60fps
    
    // Initialize menu visibility (hidden until logo is in position)
    menuState.menuVisible = false;
    
    // Set up menu positions
    SetupMenuTransition();
    
    printf("Main menu initialized\n");
}

// Set up menu item positions and transitions
static void SetupMenuTransition(void) {
    float menuCenterX = GetScreenWidth() / 2.0f;
    float menuCenterY = GetScreenHeight() / 2.0f;
    
    // Set desired positions (centered)
    for (int i = 0; i < MENU_COUNT; i++) {
        const char* optionText;
        switch (i) {
            case MENU_PLAY: optionText = "Start"; break;
            case MENU_OPTIONS: optionText = "Options"; break;
            case MENU_HELP: optionText = "Help"; break;
            case MENU_EXIT: optionText = "Quit"; break;
            default: optionText = ""; break;
        }
        
        float fontSize = 30;
        float itemHeight = fontSize + 20;
        float textWidth = MeasureText(optionText, fontSize);
        
        // Position items in a vertical list centered on screen
        menuState.menuItemDesiredPositions[i] = (Vector2){
            menuCenterX - textWidth / 2,
            menuCenterY + (itemHeight * 2.0f) * i - ((MENU_COUNT-1) * itemHeight)
        };
        
        // Set initial positions (off screen to the right)
        menuState.menuItemPositions[i] = (Vector2){
            GetScreenWidth(),
            menuState.menuItemDesiredPositions[i].y
        };
    }
}

// Update main menu logic
static void UpdateMainMenu(float deltaTime) {
    // Update timers
    menuState.frameCounter += deltaTime;
    menuState.textBlink = sinf(menuState.frameCounter * 4) * 0.5f + 0.5f;
    
    // Update logo animation
    if (menuState.logoAnimPlaying) {
        menuState.logoFrameTime += deltaTime;
        
        // Check if it's time to advance to the next frame
        if (menuState.logoFrameTime >= menuState.logoFrames[menuState.currentLogoFrame].duration) {
            menuState.logoFrameTime = 0;
            menuState.currentLogoFrame = (menuState.currentLogoFrame + 1) % 7;
        }
    }
    
    // Move logo to its desired position
    MoveItemToPosition(&menuState.logoPosition, menuState.logoDesiredPosition, 
                       menuState.logoTransitionSpeed, deltaTime);
    
    // Check if logo is in position to show menu
    if (!menuState.menuVisible) {
        if (menuState.logoPosition.x == menuState.logoDesiredPosition.x && 
            menuState.logoPosition.y == menuState.logoDesiredPosition.y) {
            menuState.menuVisible = true;
        }
    }
    
    // If menu is visible, handle menu navigation and update menu item positions
    if (menuState.menuVisible) {
        // Update menu item positions
        for (int i = 0; i < MENU_COUNT; i++) {
            MoveItemToPosition(&menuState.menuItemPositions[i], 
                              menuState.menuItemDesiredPositions[i],
                              menuState.logoTransitionSpeed, deltaTime);
        }
        
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
                    menuState.nextScreen = PREPARE_MENU;
                    ScreenMainMenu.finishScreen = true;
                    break;
                case MENU_OPTIONS:
                    menuState.nextScreen = OPTIONS;
                    ScreenMainMenu.finishScreen = true;
                    break;
                case MENU_HELP:
                    // Just stay in main menu for now, will implement later
                    menuState.nextScreen = MAIN_MENU;
                    break;
                case MENU_EXIT:
                    // Signal that the window should close
                    CloseWindow();
                    break;
                default:
                    menuState.nextScreen = MAIN_MENU;
                    break;
            }
        }
        
        // Handle gamepad back button or escape key to exit
        if (IsKeyPressed(KEY_ESCAPE)) {
            menuState.selectedOption = MENU_EXIT;
        }
        
        // Alternative navigation with mouse
        Vector2 mousePoint = GetMousePosition();
        
        // Check if mouse is over menu options
        for (int i = 0; i < MENU_COUNT; i++) {
            const char* optionText;
            switch (i) {
                case MENU_PLAY: optionText = "Start"; break;
                case MENU_OPTIONS: optionText = "Options"; break;
                case MENU_HELP: optionText = "Help"; break;
                case MENU_EXIT: optionText = "Quit"; break;
                default: optionText = ""; break;
            }
            
            float fontSize = 30;
            Vector2 position = menuState.menuItemPositions[i];
            Rectangle bounds = (Rectangle){
                position.x - 10,
                position.y - 10,
                MeasureText(optionText, fontSize) + 20,
                fontSize + 20
            };
            
            // If mouse is over option, select it
            if (CheckCollisionPointRec(mousePoint, bounds)) {
                menuState.selectedOption = i;
                
                // If mouse is clicked, select the option
                if (IsMouseButtonPressed(MOUSE_LEFT_BUTTON)) {
                    menuState.optionSelected = true;
                    
                    // Same logic as above for determining next screen
                    switch (menuState.selectedOption) {
                        case MENU_PLAY:
                            menuState.nextScreen = PREPARE_MENU;
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
}

// Move an item toward its desired position
static void MoveItemToPosition(Vector2* itemPos, Vector2 desiredPos, float speed, float deltaTime) {
    // X-axis movement
    if (desiredPos.x < itemPos->x) {
        itemPos->x -= speed * deltaTime * 60.0f; // Scale by 60fps
        if (itemPos->x < desiredPos.x) {
            itemPos->x = desiredPos.x;
        }
    } else if (desiredPos.x > itemPos->x) {
        itemPos->x += speed * deltaTime * 60.0f; // Scale by 60fps
        if (itemPos->x > desiredPos.x) {
            itemPos->x = desiredPos.x;
        }
    }
    
    // Y-axis movement
    if (desiredPos.y < itemPos->y) {
        itemPos->y -= speed * deltaTime * 60.0f; // Scale by 60fps
        if (itemPos->y < desiredPos.y) {
            itemPos->y = desiredPos.y;
        }
    } else if (desiredPos.y > itemPos->y) {
        itemPos->y += speed * deltaTime * 60.0f; // Scale by 60fps
        if (itemPos->y > desiredPos.y) {
            itemPos->y = desiredPos.y;
        }
    }
}

// Draw main menu elements
static void DrawMainMenu(void) {
    // Draw background
    DrawRectangle(0, 0, GetScreenWidth(), GetScreenHeight(), BLACK);
    
    // Draw the animated logo (scaled 2x like in Python)
    int logoWidth = menuState.logoFrames[menuState.currentLogoFrame].texture.width;
    int logoHeight = menuState.logoFrames[menuState.currentLogoFrame].texture.height;
    DrawTextureEx(menuState.logoFrames[menuState.currentLogoFrame].texture, 
                 menuState.logoPosition, 0.0f, 2.0f, WHITE);
    
    // Only draw menu if it's visible (logo is in position)
    if (menuState.menuVisible) {
        // Draw menu options
        for (int i = 0; i < MENU_COUNT; i++) {
            const char* optionText;
            switch (i) {
                case MENU_PLAY: optionText = "Start"; break;
                case MENU_OPTIONS: optionText = "Options"; break;
                case MENU_HELP: optionText = "Help"; break;
                case MENU_EXIT: optionText = "Quit"; break;
                default: optionText = ""; break;
            }
            
            float fontSize = 30;
            Vector2 position = menuState.menuItemPositions[i];
            
            // Draw selected option with highlight effect
            if (i == menuState.selectedOption) {
                Color highlightColor = ColorAlpha(WHITE, menuState.textBlink);
                Rectangle bounds = (Rectangle){
                    position.x - 10,
                    position.y - 10,
                    MeasureText(optionText, fontSize) + 20,
                    fontSize + 20
                };
                
                // Draw shadow (offset slightly down)
                DrawText(optionText, position.x, position.y + 1, fontSize, DARKGRAY);
                
                // Draw item highlight
                DrawRectangleRec(bounds, ColorAlpha(GRAY, 0.3f));
                DrawRectangleLinesEx(bounds, 2, highlightColor);
                
                // Draw text
                DrawText(optionText, position.x, position.y, fontSize, WHITE);
            } else {
                // Draw shadow
                DrawText(optionText, position.x, position.y + 1, fontSize, DARKGRAY);
                
                // Draw text
                DrawText(optionText, position.x, position.y, fontSize, LIGHTGRAY);
            }
        }
    }
}

// Unload main menu resources
static void UnloadMainMenu(void) {
    // Unload logo textures
    for (int i = 0; i < 7; i++) {
        UnloadTexture(menuState.logoFrames[i].texture);
    }
    
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
    // Create a local Screen structure and return it
    Screen screen = {
        .init = InitMainMenu,
        .update = UpdateMainMenu,
        .draw = DrawMainMenu,
        .unload = UnloadMainMenu,
        .getNextScreen = GetNextMainMenuScreen,
        .finishScreen = false,
        .nextScreen = PREPARE_MENU // Changed from GAMEPLAY to PREPARE_MENU
    };
    
    return screen;
} 