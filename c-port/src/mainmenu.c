#include "screens.h"
#include "font.h"
#include <stdlib.h>
#include <stdio.h>
#include <math.h>

// Include UI components
#include "ui/logo.h"
#include "ui/listmenu.h"
#include "ui/textitem.h"
#include "ui/transition.h"

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
    GameScreen nextScreen;
    bool done;
    
    // Logo
    Logo logo;
    Vector2 logoDesiredPosition;
    Transition logoTransition;
    
    // Menu
    ListMenu mainMenu;
    Transition menuTransition;
    
    // Menu items
    TextItem playItem;
    TextItem optionsItem;
    TextItem helpItem;
    TextItem quitItem;
} MainMenuState;

// Static menu state
static MainMenuState menuState;

// Function declarations
static void InitMainMenu(void);
static void UpdateMainMenu(float deltaTime);
static void DrawMainMenu(void);
static void UnloadMainMenu(void);
static GameScreen GetNextMainMenuScreen(void);

// Menu callback functions
static void StartGame(void* data);
static void OpenOptions(void* data);
static void OpenHelp(void* data);
static void QuitGame(void* data);

// Initialize main menu
static void InitMainMenu(void) {
    // Initialize state
    menuState.nextScreen = MAIN_MENU;
    menuState.done = false;
    
    // Initialize logo
    menuState.logo = InitLogo();
    
    // Set desired logo position (top quarter of screen)
    float logoWidth = GetLogoWidth(&menuState.logo);
    float logoHeight = GetLogoHeight(&menuState.logo);
    menuState.logoDesiredPosition = (Vector2){
        (GAME_WIDTH - logoWidth) / 2.0f,
        (GAME_HEIGHT - logoHeight) / 4.0f
    };
    
    // Initialize logo transition
    menuState.logoTransition = InitTransition();
    menuState.logoTransition.speed = 120.0f;
    
    // Start logo animation
    PlayLogo(&menuState.logo);
    
    // Initialize main menu at center of screen
    menuState.mainMenu = InitListMenu(GAME_WIDTH / 2.0f, GAME_HEIGHT / 2.0f, 0);
    
    // Initialize menu items
    menuState.playItem = InitTextItem("Start", WHITE, 255, 20);
    menuState.optionsItem = InitTextItem("Options", WHITE, 255, 20);
    menuState.helpItem = InitTextItem("Help", WHITE, 255, 20);
    menuState.quitItem = InitTextItem("Quit", WHITE, 255, 20);
    
    // Set up text item surfaces (needed for rendering)
    SetupTextItemSurfaces(&menuState.playItem);
    SetupTextItemSurfaces(&menuState.optionsItem);
    SetupTextItemSurfaces(&menuState.helpItem);
    SetupTextItemSurfaces(&menuState.quitItem);
    
    // Add items to the menu with their callback functions
    AddListMenuItem(&menuState.mainMenu, (Item*)&menuState.playItem, StartGame, NULL);
    AddListMenuItem(&menuState.mainMenu, (Item*)&menuState.optionsItem, OpenOptions, NULL);
    AddListMenuItem(&menuState.mainMenu, (Item*)&menuState.helpItem, OpenHelp, NULL);
    AddListMenuItem(&menuState.mainMenu, (Item*)&menuState.quitItem, QuitGame, NULL);
    
    // Select the first item by default
    menuState.mainMenu.base.items[0]->selected = true;
    
    // Initialize menu transition
    menuState.menuTransition = InitTransition();
    
    // Set up odd-even transition for the main menu (items come in from alternating sides)
    SetupOddEvenTransition(&menuState.menuTransition, &menuState.mainMenu.base, true, true, false, false);
    
    printf("Main menu initialized\n");
}

// Menu callbacks
static void StartGame(void* data) {
    menuState.done = true;
    menuState.nextScreen = PREPARE_MENU;
    ScreenMainMenu.finishScreen = true;
}

static void OpenOptions(void* data) {
    menuState.nextScreen = OPTIONS;
    ScreenMainMenu.finishScreen = true;
}

static void OpenHelp(void* data) {
    // For now, just stay in main menu
    // Later we'll implement the help screen
    menuState.nextScreen = MAIN_MENU;
}

static void QuitGame(void* data) {
    // Signal that we want to quit the game
    menuState.done = true;
    menuState.nextScreen = -1; // Special value to indicate exit
    CloseWindow();
}

// Update main menu logic
static void UpdateMainMenu(float deltaTime) {
    // Update logo animation
    UpdateLogo(&menuState.logo, deltaTime);
    
    // Move logo to its desired position using the transition
    Vector2 currentPos = { menuState.logo.x, menuState.logo.y };
    float speed = menuState.logoTransition.speed * deltaTime;
    
    // X-axis movement
    if (menuState.logoDesiredPosition.x < currentPos.x) {
        menuState.logo.x -= speed;
        if (menuState.logo.x < menuState.logoDesiredPosition.x) {
            menuState.logo.x = menuState.logoDesiredPosition.x;
        }
    } else if (menuState.logoDesiredPosition.x > currentPos.x) {
        menuState.logo.x += speed;
        if (menuState.logo.x > menuState.logoDesiredPosition.x) {
            menuState.logo.x = menuState.logoDesiredPosition.x;
        }
    }
    
    // Y-axis movement
    if (menuState.logoDesiredPosition.y < currentPos.y) {
        menuState.logo.y -= speed;
        if (menuState.logo.y < menuState.logoDesiredPosition.y) {
            menuState.logo.y = menuState.logoDesiredPosition.y;
        }
    } else if (menuState.logoDesiredPosition.y > currentPos.y) {
        menuState.logo.y += speed;
        if (menuState.logo.y > menuState.logoDesiredPosition.y) {
            menuState.logo.y = menuState.logoDesiredPosition.y;
        }
    }
    
    // If the logo is in place, update the menu
    if (menuState.logo.x == menuState.logoDesiredPosition.x && 
        menuState.logo.y == menuState.logoDesiredPosition.y) {
        // Update the menu transitions
        UpdateTransition(&menuState.menuTransition, deltaTime);
        
        // Update the menu
        UpdateListMenu(&menuState.mainMenu, deltaTime);
        
        // Handle escape key to select quit option
        if (IsKeyPressed(KEY_ESCAPE)) {
            // Deselect all items
            for (int i = 0; i < menuState.mainMenu.base.item_count; i++) {
                menuState.mainMenu.base.items[i]->selected = false;
            }
            // Select the quit item
            menuState.mainMenu.base.items[MENU_EXIT]->selected = true;
        }
    }
}

// Draw main menu elements
static void DrawMainMenu(void) {
    // Draw background
    DrawRectangle(0, 0, GAME_WIDTH, GAME_HEIGHT, BLACK);
    
    // Draw the logo
    DrawLogo(&menuState.logo);
    
    // If the logo is in place, draw the menu
    if (menuState.logo.x == menuState.logoDesiredPosition.x && 
        menuState.logo.y == menuState.logoDesiredPosition.y) {
        // Draw the menu
        DrawListMenu(&menuState.mainMenu);
    }
}

// Unload main menu resources
static void UnloadMainMenu(void) {
    // Unload logo
    UnloadLogo(&menuState.logo);
    
    // Unload transitions
    UnloadTransition(&menuState.logoTransition);
    UnloadTransition(&menuState.menuTransition);
    
    // Unload menu items
    UnloadTextItem(&menuState.playItem);
    UnloadTextItem(&menuState.optionsItem);
    UnloadTextItem(&menuState.helpItem);
    UnloadTextItem(&menuState.quitItem);
    
    // Unload menu
    UnloadListMenu(&menuState.mainMenu);
    
    printf("Main menu unloaded\n");
}

// Get next screen after main menu
static GameScreen GetNextMainMenuScreen(void) {
    if (menuState.nextScreen == -1) {
        // Special value to indicate exit
        return -1;
    }
    return menuState.nextScreen;
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
        .nextScreen = PREPARE_MENU
    };
    
    return screen;
} 