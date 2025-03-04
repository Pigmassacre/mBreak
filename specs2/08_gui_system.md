# GUI System Specification

## Overview

The GUI System provides a comprehensive framework for creating interactive menus, buttons, text elements, and other UI components. The system supports various types of layouts, transitions, and user interaction methods including keyboard, mouse, and gamepad input.

## Core Architecture

### GUI Item Base

```c
typedef struct GUIItem {
    // Position and dimensions
    Vector2 position;            // x, y position on screen
    float width;                 // Width of item
    float height;                // Height of item
    Rectangle bounds;            // Bounds for collision detection
    
    // Visual state
    Color color;                 // Base color
    Color shadowColor;           // Shadow color
    Color selectedColor;         // Color when selected
    Color chosenColor;           // Color when chosen
    Color disabledColor;         // Color when disabled
    
    // Shadow properties
    Vector2 shadowOffset;        // Offset for shadow
    
    // Border properties for selection feedback
    float selectedBorderSize;    // Border size when selected
    float chosenBorderSize;      // Border size when chosen
    
    // State flags
    bool selected;               // Whether item is currently selected
    bool chosen;                 // Whether item is currently chosen
    bool disabled;               // Whether item is currently disabled
    
    // Callbacks
    void (*onSelect)(struct GUIItem* self);
    void (*onClick)(struct GUIItem* self);
    void (*onHover)(struct GUIItem* self);
    
    // Virtual methods (function pointers)
    void (*update)(struct GUIItem* self, float deltaTime);
    void (*draw)(struct GUIItem* self);
    float (*getWidth)(struct GUIItem* self);
    float (*getHeight)(struct GUIItem* self);
    void (*setPosition)(struct GUIItem* self, Vector2 position);
    
    // Type-specific data (union for different item types)
    union {
        struct TextItemData* textItem;
        struct ImageItemData* imageItem;
        struct ChoiceItemData* choiceItem;
        struct ColorItemData* colorItem;
    } data;
} GUIItem;
```

### Core GUI Functions

```c
// Initialize a basic GUI item with default properties
GUIItem* GUIItemInit(Vector2 position, Color color);

// Update GUI item state
void GUIItemUpdate(GUIItem* item, float deltaTime);

// Draw the GUI item
void GUIItemDraw(GUIItem* item);

// Check if a point is inside the GUI item
bool GUIItemContainsPoint(GUIItem* item, Vector2 point);

// Set the state of a GUI item (selected, chosen, disabled)
void GUIItemSetState(GUIItem* item, bool selected, bool chosen, bool disabled);

// Destroy GUI item and free resources
void GUIItemDestroy(GUIItem* item);
```

## Menu System

The Menu system manages collections of GUI items, handling layout, selection state, and callbacks.

```c
typedef struct Menu {
    // GUI items
    List* items;                 // List of GUI items in menu
    Dictionary* functions;       // Map of items to function callbacks
    
    // Position and layout
    Vector2 position;            // Position of menu
    int currentPosition;         // Current selection position
    float spacing;               // Spacing between items (for auto-layout)
    
    // Menu linking
    List* otherMenus;            // List of other menus (for shared selection state)
    
    // State tracking
    GUIItem* previousSelectedItem; // Previously selected item (for sound effects)
    
    // Sound effect
    Sound selectSound;           // Sound played on selection change
    
    // Virtual methods
    void (*update)(struct Menu* self, float deltaTime);
    void (*draw)(struct Menu* self);
    void (*positionItem)(struct Menu* self, GUIItem* item);
    float (*getWidth)(struct Menu* self);
    float (*getHeight)(struct Menu* self);
} Menu;
```

### Menu Functions

```c
// Initialize a new menu at position
Menu* MenuInit(Vector2 position);

// Add an item to the menu with associated callback function
void MenuAddItem(Menu* menu, GUIItem* item, void (*function)(GUIItem*));

// Remove an item from the menu
void MenuRemoveItem(Menu* menu, GUIItem* item);

// Update menu state, handle selection and input
void MenuUpdate(Menu* menu, float deltaTime);

// Draw all menu items
void MenuDraw(Menu* menu);

// Position all items according to menu layout
void MenuCleanup(Menu* menu);

// Register other menus for coordinated selection
void MenuRegisterOtherMenus(Menu* menu, List* otherMenus);

// Check if mouse position is over a menu item
bool MenuIsMouseOverItem(Menu* menu, GUIItem* item, Vector2 mousePos);

// Get the dimensions of the menu
float MenuGetWidth(Menu* menu);
float MenuGetHeight(Menu* menu);

// Destroy menu and free resources
void MenuDestroy(Menu* menu);
```

## Menu Variations

### Grid Menu

The Grid Menu arranges items in a grid layout with rows and columns.

```c
typedef struct GridMenu {
    // Menu base (inherits from Menu)
    Menu base;
    
    // Grid-specific properties
    int maxColumns;              // Maximum columns before wrapping
    float columnSpacing;         // Spacing between columns
    float rowSpacing;            // Spacing between rows
    int currentRowSize;          // Current number of items in row
    float currentRowPosition;    // Current Y position for row
} GridMenu;
```

### Grid Menu Functions

```c
// Initialize a new grid menu
GridMenu* GridMenuInit(Vector2 position, int maxColumns);

// Position an item in the grid
void GridMenuPositionItem(GridMenu* menu, GUIItem* item);

// Populate the grid with an item
void GridMenuPopulateGrid(GridMenu* menu, GUIItem* item, int rowSize, float rowPosition);

// Clean up and reposition all items
void GridMenuCleanup(GridMenu* menu);

// Get the dimensions of the grid menu
float GridMenuGetWidth(GridMenu* menu);
float GridMenuGetHeight(GridMenu* menu);
```

### List Menu

The List Menu arranges items in a scrollable vertical list.

```c
typedef struct ListMenu {
    // Menu base (inherits from Menu)
    Menu base;
    
    // List-specific properties
    int visibleItems;            // Number of visible items
    int totalItems;              // Total number of items
    int startIndex;              // First visible item index
    float scrollPosition;        // Current scroll position
    float scrollSpeed;           // Scroll speed
    bool showScrollbar;          // Whether to show scrollbar
} ListMenu;
```

### List Menu Functions

```c
// Initialize a new list menu
ListMenu* ListMenuInit(Vector2 position, int visibleItems);

// Add scroll functionality
void ListMenuHandleScroll(ListMenu* menu, float amount);

// Update list menu including scrolling
void ListMenuUpdate(ListMenu* menu, float deltaTime);

// Draw list menu with visible items
void ListMenuDraw(ListMenu* menu);
```

## GUI Items

### Text Item

```c
typedef struct TextItemData {
    // Text properties
    char* text;                  // Text string
    Font font;                   // Font to use
    int fontSize;                // Font size
    
    // Text rendering
    Color textColor;             // Color of text
    Color selectedTextColor;     // Color when selected
    bool isBold;                 // Bold text
    bool isItalic;               // Italic text
    
    // On/Off state for toggles
    bool isOnOff;                // Whether this is an on/off toggle
    bool isOn;                   // Current state if on/off
    char* offText;               // Text when off
    Color onColor;               // Color when on
    Color offColor;              // Color when off
    
    // Blinking effect
    bool isBlinking;             // Whether text blinks
    float blinkRate;             // Rate of blinking
    float blinkTimer;            // Timer for blinking
    bool blinkState;             // Current blink state
} TextItemData;

// Text item methods
GUIItem* TextItemInit(const char* text, Vector2 position, Color color);
void TextItemSetText(GUIItem* item, const char* text);
void TextItemSetFont(GUIItem* item, Font font, int fontSize);
void TextItemSetOnOff(GUIItem* item, const char* offText, bool initialState);
void TextItemToggleOnOff(GUIItem* item);
void TextItemSetBlinking(GUIItem* item, bool blinking, float blinkRate);
```

### Image Item

```c
typedef struct ImageItemData {
    // Image properties
    Texture2D texture;           // Image texture
    Rectangle sourceRect;        // Source rectangle
    float scale;                 // Scale factor
    bool centerOrigin;           // Whether to center origin
    
    // Animation
    bool isAnimated;             // Whether image is animated
    int frameCount;              // Number of animation frames
    int currentFrame;            // Current animation frame
    float frameTime;             // Time per frame
    float frameTimer;            // Timer for animation
} ImageItemData;

// Image item methods
GUIItem* ImageItemInit(Texture2D texture, Vector2 position, Color tint);
void ImageItemSetScale(GUIItem* item, float scale);
void ImageItemSetSourceRect(GUIItem* item, Rectangle sourceRect);
void ImageItemSetAnimation(GUIItem* item, int frameCount, float frameTime);
```

### Choice Item

```c
typedef struct ChoiceItemData {
    // Choices
    char** choices;              // Array of choice strings
    int choiceCount;             // Number of choices
    int currentChoice;           // Current selected choice
    
    // Text rendering (reuses TextItemData)
    TextItemData textData;       // Text rendering properties
} ChoiceItemData;

// Choice item methods
GUIItem* ChoiceItemInit(char** choices, int choiceCount, Vector2 position, Color color);
void ChoiceItemSetChoice(GUIItem* item, int choiceIndex);
void ChoiceItemNextChoice(GUIItem* item);
void ChoiceItemPrevChoice(GUIItem* item);
int ChoiceItemGetCurrentChoice(GUIItem* item);
```

### Color Wheel Item

```c
typedef struct ColorWheelData {
    // Color properties
    Color currentColor;          // Currently selected color
    float hue;                   // Current hue (0-360)
    float saturation;            // Current saturation (0-1)
    float value;                 // Current value/brightness (0-1)
    
    // Wheel properties
    float radius;                // Wheel radius
    float sliderWidth;           // Width of sliders
    float sliderHeight;          // Height of sliders
    
    // Interaction state
    bool isDraggingWheel;        // Whether user is dragging wheel
    bool isDraggingSlider;       // Whether user is dragging slider
    int activeSlider;            // Which slider is active (0=hue, 1=sat, 2=val)
} ColorWheelData;

// Color wheel methods
GUIItem* ColorWheelInit(Vector2 position, float radius, Color initialColor);
void ColorWheelSetColor(GUIItem* item, Color color);
Color ColorWheelGetColor(GUIItem* item);
void ColorWheelHandleInput(GUIItem* item, Vector2 mousePosition, bool isMouseDown);
```

## Arrow Indicator

The Arrow Indicator provides a directional visual cue for the initial angle of ball movement during the countdown phase.

```c
typedef struct ArrowIndicator {
    // Visual properties
    Vector2 position;           // Center position of the arrow
    float angle;                // Current angle in radians
    Color color;                // Arrow color (with alpha)
    Shadow* shadow;             // Associated shadow
    
    // Dimensions
    float width;                // Width of the arrow
    float height;               // Height of the arrow
    
    // Rendering
    Texture2D texture;          // Arrow texture
    Rectangle sourceRect;       // Source rectangle for texture
    Rectangle destRect;         // Destination rectangle for drawing
    float rotation;             // Rotation in degrees (derived from angle)
} ArrowIndicator;
```

### Arrow Indicator Functions

```c
// Create a new arrow indicator at the specified position and angle
ArrowIndicator* CreateArrowIndicator(Vector2 position, float angle) {
    ArrowIndicator* arrow = MemAlloc(sizeof(ArrowIndicator));
    
    // Set initial properties
    arrow->position = position;
    arrow->angle = angle;
    arrow->color = (Color){ 255, 255, 255, 180 }; // White with transparency
    arrow->width = 15;
    arrow->height = 6;
    
    // Set up rendering rectangles
    arrow->sourceRect = (Rectangle){ 0, 0, arrow->width, arrow->height };
    arrow->destRect = (Rectangle){ position.x, position.y - arrow->height/2, arrow->width, arrow->height };
    arrow->rotation = -angle * RAD2DEG; // Convert to degrees and adjust for drawing
    
    // Create shadow
    arrow->shadow = CreateShadow((Rectangle){ position.x, position.y, arrow->width, arrow->height });
    
    // Load or create texture
    arrow->texture = CreateArrowTexture(arrow->width, arrow->height);
    
    return arrow;
}

// Create the arrow texture with an arrow shape
Texture2D CreateArrowTexture(float width, float height) {
    // Create an image for the arrow
    Image arrowImage = GenImageColor(width, height, BLANK);
    
    // Draw arrow body (line)
    ImageDrawLine(&arrowImage, 0, height/2, width-6, height/2, WHITE);
    
    // Draw arrow head (triangle)
    Vector2 points[3] = {
        { width-6, height/2-3 },  // Top point
        { width, height/2 },      // Tip
        { width-6, height/2+3 }   // Bottom point
    };
    ImageDrawTriangle(&arrowImage, points[0], points[1], points[2], WHITE);
    
    // Create texture from image
    Texture2D texture = LoadTextureFromImage(arrowImage);
    UnloadImage(arrowImage);
    
    return texture;
}

// Update arrow position and angle
void UpdateArrowIndicator(ArrowIndicator* arrow, Vector2 position, float angle) {
    arrow->position = position;
    
    // Only update rotation if angle has changed
    if (arrow->angle != angle) {
        arrow->angle = angle;
        arrow->rotation = -angle * RAD2DEG;
    }
    
    // Update rectangle positions based on rotation
    float cosAngle = cosf(angle);
    float sinAngle = sinf(angle);
    
    // Adjust position based on direction to maintain correct starting point
    if (cosAngle < 0) {
        // Pointing left - adjust to keep starting point
        arrow->destRect.x = position.x - arrow->destRect.width;
    } else {
        // Pointing right
        arrow->destRect.x = position.x;
    }
    
    arrow->destRect.y = position.y - arrow->destRect.height/2;
    
    // Update shadow position
    UpdateShadow(arrow->shadow, (Rectangle){ arrow->destRect.x, arrow->destRect.y, arrow->width, arrow->height });
}

// Draw the arrow indicator
void DrawArrowIndicator(ArrowIndicator* arrow) {
    // Draw shadow first
    DrawShadow(arrow->shadow);
    
    // Draw the arrow with rotation around its center
    DrawTexturePro(
        arrow->texture, 
        arrow->sourceRect,
        arrow->destRect,
        (Vector2){ 0, arrow->destRect.height/2 },
        arrow->rotation,
        arrow->color
    );
}

// Free arrow indicator resources
void FreeArrowIndicator(ArrowIndicator* arrow) {
    if (arrow) {
        FreeShadow(arrow->shadow);
        UnloadTexture(arrow->texture);
        MemFree(arrow);
    }
}
```

### Integration with Countdown System

The Arrow Indicator is primarily used in the game's countdown phase to show the initial direction of ball movement:

```c
// Example integration with countdown system
void InitializeCountdown(Game* game, float initialAngle) {
    // Create countdown
    game->countdown = CreateCountdown();
    
    // Create arrow indicator at ball starting position
    Vector2 ballPosition = { 
        LEVEL_X + (LEVEL_WIDTH + BALL_WIDTH)/2,
        LEVEL_Y + (LEVEL_HEIGHT + BALL_HEIGHT)/2
    };
    game->arrowIndicator = CreateArrowIndicator(ballPosition, initialAngle);
    
    // Setup countdown timers and state
    // ...
}

// Update countdown and arrow
void UpdateCountdown(Game* game) {
    // Update countdown logic
    // ...
    
    // Draw arrow during countdown
    if (!game->countdown->done) {
        DrawArrowIndicator(game->arrowIndicator);
    } else {
        // Cleanup when countdown is done
        FreeArrowIndicator(game->arrowIndicator);
        game->arrowIndicator = NULL;
    }
}
```

## Toast Notification System

The Toast Notification System provides temporary modal message dialogs that overlay the current screen to provide important information or feedback to the player. Toasts are typically used for warnings, errors, or critical information that requires acknowledgment before proceeding.

```c
typedef struct Toast {
    // Content
    char* message;              // Message to display
    TextItem** textLines;       // Array of text lines (for wrapped text)
    int lineCount;              // Number of text lines
    
    // Visual properties
    Color textColor;            // Primary text color
    Color alternateTextColor;   // Secondary text color for alternating lines
    Color backgroundColor;      // Background color with alpha for dimming
    float backgroundAlpha;      // Alpha value for background dimming
    
    // Menu
    Menu* menu;                 // Menu containing "OK" button
    
    // Positioning
    int screenPadding;          // Padding from screen edges
    
    // Animation
    Transition* transition;     // Transition for animating in/out
    
    // State
    bool active;                // Whether toast is currently showing
} Toast;
```

### Toast Notification Functions

```c
// Create a new toast notification with the specified message
Toast* CreateToast(const char* message, Color textColor, Color alternateTextColor) {
    Toast* toast = MemAlloc(sizeof(Toast));
    
    // Set default colors if not specified
    if (textColor.r == 0 && textColor.g == 0 && textColor.b == 0 && textColor.a == 0) {
        textColor = RED;  // Default to red for warnings
    }
    
    if (alternateTextColor.r == 0 && alternateTextColor.g == 0 && 
        alternateTextColor.b == 0 && alternateTextColor.a == 0) {
        alternateTextColor = (Color){ 255, 20, 20, 255 };  // Slightly lighter red
    }
    
    // Copy message
    toast->message = TextCopy(message);
    toast->textColor = textColor;
    toast->alternateTextColor = alternateTextColor;
    toast->backgroundAlpha = 0.88f;  // Slight transparency
    toast->active = false;
    toast->screenPadding = 6;
    
    // Wrap text to fit screen width
    WrapTextIntoLines(toast);
    
    // Create OK button menu
    CreateToastMenu(toast);
    
    // Create transition for animation
    toast->transition = CreateTransition(0.5f);  // Fast transition
    SetupToastTransition(toast);
    
    return toast;
}

// Split message into multiple lines that fit within screen width
void WrapTextIntoLines(Toast* toast) {
    // Calculate maximum width for text
    int maxWidth = GetScreenWidth() - (toast->screenPadding * 2);
    
    // Count how many lines we need
    int numLines = MeasureTextWrapped(toast->message, maxWidth);
    toast->lineCount = numLines;
    
    // Allocate text lines
    toast->textLines = MemAlloc(sizeof(TextItem*) * numLines);
    
    // Split text into lines
    char** wrappedLines = WrapText(toast->message, maxWidth);
    
    // Create text items for each line with alternating colors
    bool useAlternateColor = false;
    for (int i = 0; i < numLines; i++) {
        Color lineColor = useAlternateColor ? toast->alternateTextColor : toast->textColor;
        toast->textLines[i] = TextItemInit(wrappedLines[i], (Vector2){0, 0}, lineColor);
        useAlternateColor = !useAlternateColor;
        
        // Free the wrapped line
        MemFree(wrappedLines[i]);
    }
    
    // Free the wrapped lines array
    MemFree(wrappedLines);
    
    // Position text lines vertically centered
    PositionToastLines(toast);
}

// Position text lines in the center of the screen
void PositionToastLines(Toast* toast) {
    float totalHeight = 0;
    
    // Calculate total height of all lines
    for (int i = 0; i < toast->lineCount; i++) {
        totalHeight += toast->textLines[i]->getHeight(toast->textLines[i]);
    }
    
    // Calculate starting Y position (centered)
    float startY = (GetScreenHeight() - totalHeight) / 2.0f;
    
    // Position each line
    for (int i = 0; i < toast->lineCount; i++) {
        // Center horizontally
        float lineWidth = toast->textLines[i]->getWidth(toast->textLines[i]);
        toast->textLines[i]->setPosition(toast->textLines[i], 
            (Vector2){
                (GetScreenWidth() - lineWidth) / 2.0f,
                startY
            });
        
        // Move startY for next line
        startY += toast->textLines[i]->getHeight(toast->textLines[i]);
    }
}

// Create the OK button menu for the toast
void CreateToastMenu(Toast* toast) {
    toast->menu = MenuInit((Vector2){GetScreenWidth() / 2, 0});
    
    // Create OK button
    GUIItem* okButton = TextItemInit("OK", (Vector2){0, 0}, WHITE);
    MenuAddItem(toast->menu, okButton, DismissToast);
    
    // Position menu below text
    if (toast->lineCount > 0) {
        TextItem* lastLine = toast->textLines[toast->lineCount - 1];
        float menuY = lastLine->position.y + lastLine->getHeight(lastLine) + 20;
        toast->menu->position.y = menuY;
    } else {
        toast->menu->position.y = GetScreenHeight() / 2 + 20;
    }
    
    // Cleanup and select the OK button
    MenuCleanup(toast->menu);
    toast->menu->items[0]->selected = true;
}

// Setup transition for toast animation
void SetupToastTransition(Toast* toast) {
    // Set transition speed
    toast->transition->speed *= 1.5f;
    
    // Setup transition for text lines
    for (int i = 0; i < toast->lineCount; i++) {
        // First line slides in from all sides except bottom
        if (i == 0) {
            TransitionSetupSingle(toast->transition, toast->textLines[i], true, true, true, false);
        } else {
            // Other lines slide in from left and right only
            TransitionSetupSingle(toast->transition, toast->textLines[i], true, true, false, false);
        }
    }
    
    // OK button slides in from bottom
    TransitionSetupSingle(toast->transition, toast->menu->items[0], true, true, false, true);
}

// Show the toast notification
void ShowToast(Toast* toast) {
    toast->active = true;
}

// Dismiss the toast notification (callback for OK button)
void DismissToast(GUIItem* item) {
    // Get toast from item's parent menu
    Toast* toast = GetToastFromMenuItem(item);
    if (toast != NULL) {
        toast->active = false;
    }
}

// Update toast state
void UpdateToast(Toast* toast, float deltaTime) {
    if (!toast->active) {
        return;
    }
    
    // Update transition
    TransitionUpdate(toast->transition, deltaTime);
    
    // Update menu
    MenuUpdate(toast->menu, deltaTime);
    
    // Handle input for OK button
    // In real implementation, this would use the input system
}

// Draw the toast notification
void DrawToast(Toast* toast) {
    if (!toast->active) {
        return;
    }
    
    // Draw dimmed background
    DrawRectangle(
        0, 0,
        GetScreenWidth(), GetScreenHeight(),
        ColorAlpha(BLACK, toast->backgroundAlpha)
    );
    
    // Draw text lines
    for (int i = 0; i < toast->lineCount; i++) {
        toast->textLines[i]->draw(toast->textLines[i]);
    }
    
    // Draw menu with OK button
    MenuDraw(toast->menu);
}

// Free toast resources
void FreeToast(Toast* toast) {
    if (toast == NULL) {
        return;
    }
    
    // Free message
    if (toast->message != NULL) {
        MemFree(toast->message);
    }
    
    // Free text lines
    for (int i = 0; i < toast->lineCount; i++) {
        if (toast->textLines[i] != NULL) {
            GUIItemDestroy(toast->textLines[i]);
        }
    }
    if (toast->textLines != NULL) {
        MemFree(toast->textLines);
    }
    
    // Free menu
    if (toast->menu != NULL) {
        MenuDestroy(toast->menu);
    }
    
    // Free transition
    if (toast->transition != NULL) {
        FreeTransition(toast->transition);
    }
    
    // Free toast
    MemFree(toast);
}

## Menu Traversal System

The Traversal system provides keyboard, gamepad, and mouse navigation for menus.

```c
// Traverse menus based on input events
void TraverseMenus(List* menus, InputState input);

// Select item in given direction
void SelectDirectional(List* menus, Direction direction);

// Handle activation of selected item
void ActivateSelected(List* menus);

// Get currently selected item across all menus
GUIItem* GetSelectedItem(List* menus);

// Function to determine possible items for directional selection
List* GetPossibleSelections(List* menus, Direction direction, GUIItem* currentItem);
```

## Transition System

The Transition system handles animated transitions between menus and screens.

```c
typedef struct Transition {
    // Items to transition
    List* items;                 // Items being transitioned
    Dictionary* startPositions;  // Starting positions of items
    
    // Transition properties
    float speed;                 // Transition speed
    bool isActive;               // Whether transition is active
    float progress;              // Transition progress (0-1)
    
    // Easing function
    float (*easingFunction)(float);  // Easing function for transition
} Transition;

// Transition methods
Transition* TransitionInit(float speed);
void TransitionAddItems(Transition* transition, Menu* menu);
void TransitionAddItem(Transition* transition, GUIItem* item);
void TransitionRemoveAllItems(Transition* transition);
void TransitionSetup(Transition* transition, Menu* menu, bool left, bool right, bool up, bool down);
void TransitionSetupSingle(Transition* transition, GUIItem* item, bool left, bool right, bool up, bool down);
void TransitionUpdate(Transition* transition, float deltaTime);
bool TransitionIsComplete(Transition* transition);
```

## Layout System

The Layout system provides tools for organizing GUI elements.

```c
// Layout types
typedef enum LayoutType {
    LAYOUT_VERTICAL,
    LAYOUT_HORIZONTAL,
    LAYOUT_GRID,
    LAYOUT_FREE
} LayoutType;

typedef struct Layout {
    // Layout properties
    LayoutType type;             // Type of layout
    Vector2 position;            // Base position of layout
    float spacing;               // Spacing between elements
    List* items;                 // Items in the layout
    
    // Grid-specific properties
    int columns;                 // Number of columns (for grid)
    float columnWidth;           // Width of columns (for grid)
    float rowHeight;             // Height of rows (for grid)
    
    // Padding and margins
    float paddingLeft;           // Left padding
    float paddingRight;          // Right padding
    float paddingTop;            // Top padding
    float paddingBottom;         // Bottom padding
} Layout;

// Layout methods
Layout* LayoutInit(Vector2 position, LayoutType type, float spacing);
void LayoutAddItem(Layout* layout, GUIItem* item);
void LayoutRemoveItem(Layout* layout, GUIItem* item);
void LayoutArrange(Layout* layout);
void LayoutSetPadding(Layout* layout, float left, float right, float top, float bottom);
void LayoutSetGrid(Layout* layout, int columns, float columnWidth, float rowHeight);
```

## Event System

The Event system handles GUI input events and callbacks.

```c
typedef enum GUIEventType {
    GUI_EVENT_CLICK,
    GUI_EVENT_HOVER,
    GUI_EVENT_HOVER_EXIT,
    GUI_EVENT_SELECT,
    GUI_EVENT_DESELECT,
    GUI_EVENT_KEY,
    GUI_EVENT_VALUE_CHANGE
} GUIEventType;

typedef struct GUIEvent {
    GUIEventType type;           // Type of event
    GUIItem* item;               // Item that triggered event
    void* data;                  // Additional event data
} GUIEvent;

typedef struct GUIEventSystem {
    List* listeners;             // Event listeners
} GUIEventSystem;

// Event system methods
GUIEventSystem* GUIEventSystemInit(void);
void GUIEventSystemAddListener(GUIEventSystem* system, GUIEventType type, GUIItem* item, void (*callback)(GUIEvent*));
void GUIEventSystemRemoveListener(GUIEventSystem* system, GUIEventType type, GUIItem* item, void (*callback)(GUIEvent*));
void GUIEventSystemTriggerEvent(GUIEventSystem* system, GUIEvent event);
```

## Theme System

The Theme system handles consistent visual styling across the UI.

```c
typedef struct GUITheme {
    // Colors
    Color primaryColor;          // Main UI color
    Color secondaryColor;        // Secondary UI color
    Color accentColor;           // Accent UI color
    Color backgroundColor;       // Background color
    Color textColor;             // Text color
    Color disabledColor;         // Disabled item color
    Color shadowColor;           // Shadow color
    
    // Fonts
    Font defaultFont;            // Default font
    int defaultFontSize;         // Default font size
    
    // Dimensions
    float itemSpacing;           // Default spacing between items
    float itemPadding;           // Default padding within items
    float borderSize;            // Default border size
    
    // Effects
    bool useShadows;             // Whether to use shadows
    Vector2 shadowOffset;        // Shadow offset
} GUITheme;

// Theme methods
GUITheme* GUIThemeInit(void);
void GUIThemeApplyToItem(GUITheme* theme, GUIItem* item);
void GUIThemeApplyToMenu(GUITheme* theme, Menu* menu);
GUITheme* GUIThemeCreateFromFile(const char* fileName);
void GUIThemeSaveToFile(GUITheme* theme, const char* fileName);
```

## Animation System

The Animation system provides tools for animating GUI elements.

```c
typedef enum AnimationType {
    ANIMATION_FADE,
    ANIMATION_MOVE,
    ANIMATION_SCALE,
    ANIMATION_ROTATE,
    ANIMATION_COLOR,
    ANIMATION_CUSTOM
} AnimationType;

typedef struct GUIAnimation {
    // Animation properties
    AnimationType type;          // Type of animation
    GUIItem* target;             // Target item
    float duration;              // Duration in seconds
    float elapsed;               // Elapsed time
    
    // Easing
    float (*easingFunction)(float);  // Easing function
    
    // Animation values
    union {
        struct {
            float startValue;
            float endValue;
        } fade;
        
        struct {
            Vector2 startPosition;
            Vector2 endPosition;
        } move;
        
        struct {
            Vector2 startScale;
            Vector2 endScale;
        } scale;
        
        struct {
            float startAngle;
            float endAngle;
        } rotate;
        
        struct {
            Color startColor;
            Color endColor;
        } color;
        
        struct {
            void* data;
            void (*updateFunc)(GUIItem*, void*, float);
        } custom;
    } values;
    
    // Callbacks
    void (*onComplete)(GUIItem*);
    bool repeat;                 // Whether to repeat
    bool alternateDirection;     // Whether to alternate direction when repeating
} GUIAnimation;

// Animation methods
GUIAnimation* GUIAnimationInit(GUIItem* target, AnimationType type, float duration);
void GUIAnimationSetEasing(GUIAnimation* animation, float (*easingFunction)(float));
void GUIAnimationSetFade(GUIAnimation* animation, float startValue, float endValue);
void GUIAnimationSetMove(GUIAnimation* animation, Vector2 startPosition, Vector2 endPosition);
void GUIAnimationSetScale(GUIAnimation* animation, Vector2 startScale, Vector2 endScale);
void GUIAnimationSetRotate(GUIAnimation* animation, float startAngle, float endAngle);
void GUIAnimationSetColor(GUIAnimation* animation, Color startColor, Color endColor);
void GUIAnimationSetCustom(GUIAnimation* animation, void* data, void (*updateFunc)(GUIItem*, void*, float));
void GUIAnimationSetOnComplete(GUIAnimation* animation, void (*onComplete)(GUIItem*));
void GUIAnimationPlay(GUIAnimation* animation);
void GUIAnimationStop(GUIAnimation* animation);
void GUIAnimationUpdate(GUIAnimation* animation, float deltaTime);
bool GUIAnimationIsPlaying(GUIAnimation* animation);
```

## Sound System Integration

```c
// GUI sound effects
typedef struct GUISounds {
    Sound hover;                 // Hover sound
    Sound select;                // Selection sound
    Sound click;                 // Click sound
    Sound back;                  // Back/cancel sound
    Sound error;                 // Error sound
    Sound transition;            // Menu transition sound
    Sound toggle;                // Toggle on/off sound
} GUISounds;

// Sound methods
GUISounds* GUISoundsInit(void);
void GUISoundsLoad(GUISounds* sounds, const char* hoverFile, const char* selectFile, 
                  const char* clickFile, const char* backFile, const char* errorFile,
                  const char* transitionFile, const char* toggleFile);
void GUISoundsPlay(GUISounds* sounds, int soundIndex);
void GUISoundsSetVolume(GUISounds* sounds, float volume);
void GUISoundsDestroy(GUISounds* sounds);
```

## Focus System

The Focus system handles keyboard/gamepad focus management across UI components.

```c
typedef struct FocusManager {
    GUIItem* currentFocus;       // Currently focused item
    List* focusableItems;        // All focusable items
    bool keyboardMode;           // Whether keyboard/gamepad mode is active
} FocusManager;

// Focus methods
FocusManager* FocusManagerInit(void);
void FocusManagerAddItem(FocusManager* manager, GUIItem* item);
void FocusManagerRemoveItem(FocusManager* manager, GUIItem* item);
void FocusManagerSetFocus(FocusManager* manager, GUIItem* item);
void FocusManagerNavigate(FocusManager* manager, Direction direction);
void FocusManagerActivateFocused(FocusManager* manager);
void FocusManagerUpdate(FocusManager* manager, InputState input);
```

## Accessibility Features

```c
typedef struct GUIAccessibility {
    // Text-to-speech
    bool textToSpeechEnabled;    // Whether TTS is enabled
    
    // High contrast mode
    bool highContrastMode;       // Whether high contrast mode is enabled
    Color highContrastTextColor; // Text color in high contrast mode
    Color highContrastBgColor;   // Background color in high contrast mode
    
    // Font scaling
    float fontScale;             // Font scaling factor for accessibility
    
    // Input timing
    float inputRepeatDelay;      // Delay before input repeats
    float inputRepeatRate;       // Rate of input repetition
    
    // Gamepad sensitivity
    float gamepadDeadzone;       // Gamepad stick deadzone
} GUIAccessibility;

// Accessibility methods
GUIAccessibility* GUIAccessibilityInit(void);
void GUIAccessibilityApplyToTheme(GUIAccessibility* accessibility, GUITheme* theme);
void GUIAccessibilitySetTextToSpeech(GUIAccessibility* accessibility, bool enabled);
void GUIAccessibilitySetHighContrast(GUIAccessibility* accessibility, bool enabled);
void GUIAccessibilitySetFontScale(GUIAccessibility* accessibility, float scale);
void GUIAccessibilityReadText(GUIAccessibility* accessibility, const char* text);
```

## GUI System Manager

```c
typedef struct GUISystem {
    // Core components
    List* allMenus;              // All menus in the system
    List* allItems;              // All items in the system
    GUIEventSystem* eventSystem; // Event system
    FocusManager* focusManager;  // Focus manager
    GUITheme* activeTheme;       // Active theme
    GUISounds* sounds;           // Sound effects
    GUIAccessibility* accessibility; // Accessibility features
    
    // State
    bool enabled;                // Whether GUI system is enabled
    bool debugMode;              // Whether debug mode is enabled
} GUISystem;

// GUI system methods
GUISystem* GUISystemInit(void);
void GUISystemUpdate(GUISystem* system, float deltaTime);
void GUISystemDraw(GUISystem* system);
void GUISystemHandleInput(GUISystem* system, InputState input);
void GUISystemAddMenu(GUISystem* system, Menu* menu);
void GUISystemRemoveMenu(GUISystem* system, Menu* menu);
void GUISystemSetTheme(GUISystem* system, GUITheme* theme);
void GUISystemDestroy(GUISystem* system);
void GUISystemToggleDebugMode(GUISystem* system);
```

## Performance Optimization

```c
// Batch rendering for GUI
void GUISystemBatchDraw(GUISystem* system) {
    // Sort items by texture to minimize texture binding
    SortItemsByTexture(system->allItems);
    
    // Begin batch drawing
    BeginDrawing();
    
    Texture2D currentTexture = { 0 };
    for (int i = 0; i < system->allItems->count; i++) {
        GUIItem* item = system->allItems->items[i];
        
        // Skip if item has no texture component
        if (!item->data.imageItem) continue;
        
        // Only include visible items
        Menu* parentMenu = GetParentMenu(system, item);
        if (parentMenu && !MenuIsVisible(parentMenu)) continue;
        
        // If texture changed, end previous batch and start new one
        if (item->data.imageItem->texture.id != currentTexture.id) {
            if (currentTexture.id != 0) EndDrawing();
            currentTexture = item->data.imageItem->texture;
            BeginMode2D(camera);
        }
        
        // Draw item
        DrawTexturePro(
            currentTexture,
            item->data.imageItem->sourceRect,
            (Rectangle){ item->position.x, item->position.y, item->width, item->height },
            (Vector2){ 0, 0 },
            0.0f,
            item->color
        );
    }
    
    // End final batch
    EndDrawing();
}
```

## Debugging Support

```c
// Draw GUI debug information
void GUISystemDrawDebug(GUISystem* system) {
    if (!system->debugMode) return;
    
    // Draw item boundaries
    for (int i = 0; i < system->allItems->count; i++) {
        GUIItem* item = system->allItems->items[i];
        
        // Draw item rectangle
        DrawRectangleLinesEx(
            (Rectangle){ item->position.x, item->position.y, item->width, item->height },
            1.0f,
            item->selected ? RED : GREEN
        );
        
        // Draw item ID and type
        char debugText[64];
        sprintf(debugText, "ID:%d Type:%d", i, GetItemType(item));
        DrawText(debugText, item->position.x, item->position.y - 12, 10, RED);
    }
    
    // Draw active focus
    if (system->focusManager->currentFocus) {
        GUIItem* focus = system->focusManager->currentFocus;
        DrawRectangleLinesEx(
            (Rectangle){ focus->position.x - 2, focus->position.y - 2, 
                        focus->width + 4, focus->height + 4 },
            2.0f,
            BLUE
        );
    }
    
    // Draw frame statistics
    char statsText[128];
    sprintf(statsText, "Items: %d Menus: %d Animations: %d", 
           system->allItems->count, system->allMenus->count, GetActiveAnimationCount());
    DrawText(statsText, 10, 10, 20, YELLOW);
}
```

## Conclusion

The GUI System is a comprehensive framework for creating and managing user interfaces in the game. Its modular design provides flexibility for creating various menu layouts, transitions, and interactive components while maintaining consistent behavior and visual styling. The integration with other systems such as input, sound, and rendering creates a cohesive and responsive user experience that works across different input methods and platforms. 