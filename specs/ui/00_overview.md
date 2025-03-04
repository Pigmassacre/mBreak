# UI System Overview

## System Components

### UI Manager
```c
typedef struct UIManager {
    // Screen management
    Screen* currentScreen;
    Screen* previousScreen;
    TransitionEffect* transition;
    
    // UI elements
    UIElement** elements;
    int elementCount;
    int capacity;
    
    // Input handling
    Vector2 mousePosition;
    bool mousePressed;
    bool mouseReleased;
    
    // Layout system
    LayoutManager* layoutManager;
    
    // Theme system
    UITheme* currentTheme;
} UIManager;
```

### UI Element Base
```c
typedef struct UIElement {
    // Core properties
    Rectangle bounds;
    bool visible;
    bool enabled;
    Color color;
    
    // State
    UIState state;
    bool focused;
    bool hovered;
    
    // Events
    UIEventHandler onHover;
    UIEventHandler onClick;
    UIEventHandler onFocus;
    
    // Style
    UIStyle* style;
    
    // Layout
    Vector2 position;
    Vector2 size;
    float scale;
    float rotation;
} UIElement;
```

### Theme System
```c
typedef struct UITheme {
    // Colors
    struct {
        Color primary;
        Color secondary;
        Color accent;
        Color text;
        Color background;
        Color disabled;
    } colors;
    
    // Fonts
    struct {
        Font titleFont;
        Font bodyFont;
        Font buttonFont;
        int titleSize;
        int bodySize;
        int buttonSize;
    } fonts;
    
    // Spacing
    struct {
        float padding;
        float margin;
        float gap;
        float borderWidth;
    } spacing;
} UITheme;
```

## Core Components

### Button
```c
typedef struct UIButton {
    UIElement base;
    
    // Button specific
    const char* text;
    Texture2D icon;
    bool isToggle;
    bool isPressed;
    
    // Animation
    float pressScale;
    float hoverScale;
    Color pressColor;
    Color hoverColor;
} UIButton;

void DrawButton(UIButton* button) {
    // Draw background
    DrawRectangleRec(button->base.bounds, button->base.color);
    
    // Draw icon if exists
    if (button->icon.id != 0) {
        DrawTexture(button->icon, 
            button->base.bounds.x + (button->base.bounds.width - button->icon.width) / 2,
            button->base.bounds.y + (button->base.bounds.height - button->icon.height) / 2,
            WHITE);
    }
    
    // Draw text
    DrawText(button->text,
        button->base.bounds.x + button->base.bounds.width / 2,
        button->base.bounds.y + button->base.bounds.height / 2,
        button->base.style->fontSize,
        button->base.style->textColor);
}
```

### Panel
```c
typedef struct UIPanel {
    UIElement base;
    
    // Panel specific
    UIElement** children;
    int childCount;
    bool isDraggable;
    bool isResizable;
    
    // Scroll
    Vector2 scrollOffset;
    bool hasScrollbar;
    float scrollSpeed;
} UIPanel;

void UpdatePanel(UIPanel* panel) {
    // Update children
    for (int i = 0; i < panel->childCount; i++) {
        UpdateUIElement(panel->children[i]);
    }
    
    // Handle scrolling
    if (panel->hasScrollbar) {
        UpdateScroll(panel);
    }
    
    // Handle dragging
    if (panel->isDraggable) {
        UpdateDrag(panel);
    }
}
```

### Text
```c
typedef struct UIText {
    UIElement base;
    
    // Text specific
    char* content;
    TextAlignment alignment;
    bool isWrapped;
    bool isRich;
    
    // Rich text
    struct {
        Color* colors;
        int* sizes;
        bool* isBold;
        bool* isItalic;
    } formatting;
} UIText;

void DrawText(UIText* text) {
    if (text->isRich) {
        DrawRichText(text);
    } else {
        DrawSimpleText(text);
    }
}
```

## Layout System

### Layout Manager
```c
typedef struct LayoutManager {
    // Layout settings
    LayoutType type;
    float spacing;
    Vector2 padding;
    
    // Grid specific
    struct {
        int columns;
        int rows;
        float cellWidth;
        float cellHeight;
    } grid;
    
    // Flex specific
    struct {
        FlexDirection direction;
        FlexWrap wrap;
        FlexJustify justify;
        FlexAlign align;
    } flex;
} LayoutManager;

void LayoutElements(UIElement** elements, int count, LayoutManager* layout) {
    switch (layout->type) {
        case LAYOUT_GRID:
            LayoutGrid(elements, count, layout);
            break;
        case LAYOUT_FLEX:
            LayoutFlex(elements, count, layout);
            break;
        case LAYOUT_ABSOLUTE:
            // No layout needed
            break;
    }
}
```

## Animation System

### UI Animation
```c
typedef struct UIAnimation {
    // Animation properties
    float duration;
    float elapsed;
    EaseType easeType;
    bool isPlaying;
    
    // Values
    struct {
        Vector2 position;
        Vector2 scale;
        float rotation;
        Color color;
    } start, end, current;
    
    // Callbacks
    void (*onComplete)(UIElement*);
    void (*onUpdate)(UIElement*, float);
} UIAnimation;

void UpdateAnimation(UIAnimation* anim, float deltaTime) {
    if (!anim->isPlaying) return;
    
    anim->elapsed += deltaTime;
    float t = anim->elapsed / anim->duration;
    
    // Apply easing
    t = ApplyEasing(t, anim->easeType);
    
    // Interpolate values
    anim->current.position = Vector2Lerp(anim->start.position, anim->end.position, t);
    anim->current.scale = Vector2Lerp(anim->start.scale, anim->end.scale, t);
    anim->current.rotation = Lerp(anim->start.rotation, anim->end.rotation, t);
    anim->current.color = ColorLerp(anim->start.color, anim->end.color, t);
    
    if (anim->elapsed >= anim->duration) {
        anim->isPlaying = false;
        if (anim->onComplete) anim->onComplete(anim->target);
    }
}
```

## Event System

### UI Events
```c
typedef struct UIEvent {
    UIEventType type;
    UIElement* target;
    Vector2 position;
    bool handled;
    
    // Event specific data
    union {
        struct {
            int button;
            bool isDouble;
        } mouse;
        
        struct {
            int key;
            bool isRepeat;
        } keyboard;
        
        struct {
            float delta;
            Vector2 offset;
        } scroll;
    } data;
} UIEvent;

void HandleUIEvent(UIManager* manager, UIEvent event) {
    // Find target element
    UIElement* target = FindEventTarget(manager, event.position);
    
    // Bubble event up
    while (target && !event.handled) {
        if (target->eventHandler) {
            target->eventHandler(target, &event);
        }
        target = target->parent;
    }
}
```

## Debug Features

### UI Debug Visualization
```c
void DrawUIDebug(UIManager* manager) {
    if (!IsDebugMode()) return;
    
    for (int i = 0; i < manager->elementCount; i++) {
        UIElement* element = manager->elements[i];
        
        // Draw bounds
        DrawRectangleLinesEx(element->bounds, 1, RED);
        
        // Draw anchor points
        DrawAnchorPoints(element);
        
        // Draw layout grid
        if (element->layout) {
            DrawLayoutGrid(element);
        }
        
        // Draw element info
        DrawElementInfo(element);
    }
}
``` 