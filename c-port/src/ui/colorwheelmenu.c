/**
 * @file colorwheelmenu.c
 * @brief Implementation of the ColorWheelMenu UI component.
 */

#include "ui/colorwheelmenu.h"
#include "ui/item.h"
#include <stdlib.h>
#include <math.h>

// Default color for the color display when no color is selected
#define DEFAULT_COLOR GRAY

// Size of the color display item
#define COLOR_DISPLAY_SIZE 20.0f

// Size of the selection indicator
#define SELECTION_INDICATOR_SIZE 8

// Size of the hover indicator
#define HOVER_INDICATOR_SIZE 5

// Function to handle dummy menu item selection
static void DummyFunction(Item* item) {
    // This function does nothing, it's just to satisfy the menu system
    (void)item; // Avoid unused parameter warning
}

ColorWheelMenu InitColorWheelMenu(float radius, float center_x, float center_y) {
    ColorWheelMenu colorwheel;
    
    // Initialize the base menu
    colorwheel.base = InitMenu();
    
    // Store the radius and center position
    colorwheel.radius = radius;
    colorwheel.center_x = center_x;
    colorwheel.center_y = center_y;
    
    // Initialize selection state
    colorwheel.selected_color = DEFAULT_COLOR;
    colorwheel.selected_pos = (Vector2){ 0, 0 };
    colorwheel.hover_pos = (Vector2){ 0, 0 };
    colorwheel.has_selection = false;
    colorwheel.has_hover = false;
    
    // Initialize the color display item
    colorwheel.color_display = InitItem();
    colorwheel.color_display.width = COLOR_DISPLAY_SIZE;
    colorwheel.color_display.height = COLOR_DISPLAY_SIZE;
    colorwheel.color_display.color = DEFAULT_COLOR;
    
    // Set auto-positioning for the color display
    colorwheel.auto_position_color_display = true;
    
    // Generate the color wheel texture
    GenerateColorWheel(&colorwheel);
    
    // Add a dummy item to make this menu compatible with the game's menu navigation system
    Item dummy_item = InitItem();
    dummy_item.width = 0;
    dummy_item.height = 0;
    AddMenuItem(&colorwheel.base, &dummy_item, DummyFunction);
    
    return colorwheel;
}

void UnloadColorWheelMenu(ColorWheelMenu* colorwheel) {
    // Unload the color wheel texture
    UnloadTexture(colorwheel->wheel_texture);
    
    // Unload the base menu
    UnloadMenu(&colorwheel->base);
}

void GenerateColorWheel(ColorWheelMenu* colorwheel) {
    // Calculate the dimensions of the texture
    int size = (int)(colorwheel->radius * 2);
    
    // Create an image to draw the color wheel
    Image wheel_image = GenImageColor(size, size, BLANK);
    
    // Generate the color wheel
    for (int x = 0; x < size; x++) {
        for (int y = 0; y < size; y++) {
            // Calculate the position relative to the center
            float dx = (float)x - colorwheel->radius;
            float dy = (float)y - colorwheel->radius;
            
            // Calculate the distance from the center
            float distance = sqrtf(dx * dx + dy * dy);
            
            if (distance <= colorwheel->radius) {
                // Calculate the hue based on the angle
                float angle = atan2f(dy, dx);
                float hue = (angle / (2.0f * PI)) + 0.5f; // Normalize to 0-1 range
                
                // Calculate the saturation based on the distance from center
                float saturation = fminf(1.0f, distance / colorwheel->radius);
                
                // Convert HSV to RGB
                Color color = HsvToRgb(hue, saturation, 1.0f);
                
                // Set the pixel color
                ImageDrawPixel(&wheel_image, x, y, color);
            }
        }
    }
    
    // Convert the image to a texture
    colorwheel->wheel_texture = LoadTextureFromImage(wheel_image);
    
    // Unload the image as it's no longer needed
    UnloadImage(wheel_image);
}

Color HsvToRgb(float h, float s, float v) {
    Color rgb;
    
    // Handle grayscale case
    if (s == 0.0f) {
        rgb.r = (unsigned char)(v * 255.0f);
        rgb.g = (unsigned char)(v * 255.0f);
        rgb.b = (unsigned char)(v * 255.0f);
        rgb.a = 255;
        return rgb;
    }
    
    h = fmodf(h, 1.0f) * 6.0f;
    int i = (int)h;
    float f = h - (float)i;
    float p = v * (1.0f - s);
    float q = v * (1.0f - s * f);
    float t = v * (1.0f - s * (1.0f - f));
    
    switch (i) {
        case 0:
            rgb.r = (unsigned char)(v * 255.0f);
            rgb.g = (unsigned char)(t * 255.0f);
            rgb.b = (unsigned char)(p * 255.0f);
            break;
        case 1:
            rgb.r = (unsigned char)(q * 255.0f);
            rgb.g = (unsigned char)(v * 255.0f);
            rgb.b = (unsigned char)(p * 255.0f);
            break;
        case 2:
            rgb.r = (unsigned char)(p * 255.0f);
            rgb.g = (unsigned char)(v * 255.0f);
            rgb.b = (unsigned char)(t * 255.0f);
            break;
        case 3:
            rgb.r = (unsigned char)(p * 255.0f);
            rgb.g = (unsigned char)(q * 255.0f);
            rgb.b = (unsigned char)(v * 255.0f);
            break;
        case 4:
            rgb.r = (unsigned char)(t * 255.0f);
            rgb.g = (unsigned char)(p * 255.0f);
            rgb.b = (unsigned char)(v * 255.0f);
            break;
        default: // case 5
            rgb.r = (unsigned char)(v * 255.0f);
            rgb.g = (unsigned char)(p * 255.0f);
            rgb.b = (unsigned char)(q * 255.0f);
            break;
    }
    
    rgb.a = 255;
    return rgb;
}

bool GetColorAtPosition(const ColorWheelMenu* colorwheel, Vector2 pos, Color* color) {
    // Calculate position relative to the top-left corner of the wheel
    float x = pos.x - colorwheel->base.x;
    float y = pos.y - colorwheel->base.y;
    
    // Check if the position is within the wheel's bounding box
    if (x >= 0 && x < colorwheel->radius * 2 && y >= 0 && y < colorwheel->radius * 2) {
        // Calculate distance from center of the wheel
        float dx = x - colorwheel->radius;
        float dy = y - colorwheel->radius;
        float distance = sqrtf(dx * dx + dy * dy);
        
        if (distance <= colorwheel->radius) {
            // Calculate the hue based on the angle
            float angle = atan2f(dy, dx);
            float hue = (angle / (2.0f * PI)) + 0.5f; // Normalize to 0-1 range
            
            // Calculate the saturation based on the distance from center
            float saturation = fminf(1.0f, distance / colorwheel->radius);
            
            // Convert HSV to RGB
            *color = HsvToRgb(hue, saturation, 1.0f);
            
            return true;
        }
    }
    
    return false;
}

bool SelectColor(ColorWheelMenu* colorwheel, Vector2 pos) {
    Color color;
    if (GetColorAtPosition(colorwheel, pos, &color)) {
        colorwheel->selected_color = color;
        colorwheel->selected_pos = (Vector2){ pos.x - colorwheel->base.x, pos.y - colorwheel->base.y };
        colorwheel->has_selection = true;
        colorwheel->color_display.color = color;
        
        // Play a sound effect to indicate selection (would be implemented elsewhere)
        // PlaySound(colorwheel->sound_effect);
        
        return true;
    }
    
    return false;
}

float GetColorWheelWidth(const ColorWheelMenu* colorwheel) {
    return colorwheel->radius * 2;
}

float GetColorWheelHeight(const ColorWheelMenu* colorwheel) {
    return colorwheel->radius * 2;
}

void SetColorDisplayPosition(ColorWheelMenu* colorwheel, float x, float y) {
    colorwheel->color_display.x = x;
    colorwheel->color_display.y = y;
    colorwheel->auto_position_color_display = false;
}

void UpdateColorWheelMenu(ColorWheelMenu* colorwheel) {
    // Update the base menu
    UpdateMenu(&colorwheel->base);
    
    // Update the color display position if auto-positioning is enabled
    if (colorwheel->auto_position_color_display) {
        colorwheel->color_display.x = colorwheel->base.x + colorwheel->radius * 2 + 10;
        colorwheel->color_display.y = colorwheel->base.y + colorwheel->radius - colorwheel->color_display.height / 2;
    }
    
    // Update hover position if mouse is over the wheel
    Vector2 mouse_pos = GetMousePosition();
    Color hover_color;
    
    if (GetColorAtPosition(colorwheel, mouse_pos, &hover_color)) {
        colorwheel->hover_pos = (Vector2){ mouse_pos.x - colorwheel->base.x, mouse_pos.y - colorwheel->base.y };
        colorwheel->has_hover = true;
        
        // Update the color display to show the color under the cursor
        // If a color is selected, keep showing that color
        if (!colorwheel->has_selection) {
            colorwheel->color_display.color = hover_color;
        }
        
        // Check for mouse click to select a color
        if (IsMouseButtonPressed(MOUSE_LEFT_BUTTON)) {
            SelectColor(colorwheel, mouse_pos);
        }
    } else {
        colorwheel->has_hover = false;
        
        // If no color is selected and mouse is not over the wheel, show a default color
        if (!colorwheel->has_selection) {
            colorwheel->color_display.color = DEFAULT_COLOR;
        }
    }
    
    // Update the color display item
    UpdateItem(&colorwheel->color_display);
}

void DrawColorWheelMenu(const ColorWheelMenu* colorwheel) {
    // Draw the color wheel
    DrawTexture(colorwheel->wheel_texture, (int)colorwheel->base.x, (int)colorwheel->base.y, WHITE);
    
    // Draw the selected position indicator if a color is selected
    if (colorwheel->has_selection) {
        // Draw a yellow square to mark the selected color
        DrawRectangleLines(
            (int)(colorwheel->base.x + colorwheel->selected_pos.x - SELECTION_INDICATOR_SIZE/2),
            (int)(colorwheel->base.y + colorwheel->selected_pos.y - SELECTION_INDICATOR_SIZE/2),
            SELECTION_INDICATOR_SIZE,
            SELECTION_INDICATOR_SIZE,
            YELLOW
        );
    }
    
    // Draw the hover position indicator if mouse is over the wheel
    if (colorwheel->has_hover) {
        // Draw a white circle to show the current hover position
        DrawCircleLines(
            (int)(colorwheel->base.x + colorwheel->hover_pos.x),
            (int)(colorwheel->base.y + colorwheel->hover_pos.y),
            HOVER_INDICATOR_SIZE,
            WHITE
        );
    }
    
    // Draw the color display
    DrawItem(&colorwheel->color_display);
    
    // Draw the base menu (which contains the dummy item)
    DrawMenu(&colorwheel->base);
}

void ClearColorSelection(ColorWheelMenu* colorwheel) {
    colorwheel->has_selection = false;
    colorwheel->selected_color = DEFAULT_COLOR;
    colorwheel->color_display.color = DEFAULT_COLOR;
} 