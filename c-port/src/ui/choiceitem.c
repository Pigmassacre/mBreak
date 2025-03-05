/**
 * @file choiceitem.c
 * @brief Implementation of the ChoiceItem UI component.
 */

#include "ui/choiceitem.h"
#include <stdlib.h>
#include <string.h>

// Font path and size constants - match Python implementation
static const char* FONT_PATH = "fonts/ADDLG___.TTF";
static const int FONT_SIZE = 9;

// Global font instance (similar to class variable in Python)
static Font defaultFont = { 0 };
static bool fontInitialized = false;

// Helper function to ensure the font is loaded
static void EnsureFontInitialized() {
    if (!fontInitialized) {
        defaultFont = LoadFont(FONT_PATH);
        fontInitialized = true;
    }
}

ChoiceItem InitChoiceItem(const char* value, Color color, Color font_color, int alpha_value) {
    ChoiceItem item;
    
    // Initialize base item
    item.base = InitItem(color);
    
    // Ensure the font is initialized
    EnsureFontInitialized();
    
    // Setup font values
    item.font = defaultFont;
    item.font_color = font_color;
    item.alpha_value = alpha_value;
    
    // Copy the value
    if (value) {
        item.value = strdup(value);
    } else {
        item.value = strdup("");
    }
    
    // Create the font surface (texture in Raylib)
    Image textImage = ImageTextEx(item.font, item.value, (float)FONT_SIZE, 1.0f, font_color);
    item.font_surface = LoadTextureFromImage(textImage);
    UnloadImage(textImage);
    
    return item;
}

void UnloadChoiceItem(ChoiceItem* item) {
    // Free the value string
    if (item->value) {
        free(item->value);
        item->value = NULL;
    }
    
    // Unload the font surface
    UnloadTexture(item->font_surface);
}

void UpdateChoiceItem(ChoiceItem* item, float delta_time) {
    // Update base item for animations, etc.
    UpdateItem(&item->base, delta_time);
}

void DrawChoiceItem(const ChoiceItem* item) {
    // Draw the base item first
    DrawItem(&item->base);
    
    // Calculate position to draw the text in the middle of the item
    float x = item->base.x + (item->base.width - item->font_surface.width) / 2.0f + 0.5f;
    float y = item->base.y + (item->base.height - item->font_surface.height) / 2.0f;
    
    // Draw the font surface in the middle of this item
    DrawTexture(item->font_surface, (int)x, (int)y, WHITE);
} 