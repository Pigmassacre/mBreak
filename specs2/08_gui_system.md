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