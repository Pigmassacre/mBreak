/**
 * @file textitem.c
 * @brief Implementation of the TextItem UI component.
 */

#include "ui/textitem.h"
#include "ui/utils.h"
#include "font.h"  // Include the font.h header for access to gameFont
#include <stdlib.h>
#include <string.h>
#include <stdio.h>
#include <math.h>

// Default font values
#define TEXT_ITEM_FONT_SIZE 16
#define TEXT_ITEM_BLINK_RATE 750.0f

// Default colors
static const Color TEXT_ITEM_ON_COLOR = { 0, 90, 0, 255 };
static const Color TEXT_ITEM_OFF_COLOR = { 90, 0, 0, 255 };
static const Color TEXT_ITEM_SELECTED_ON_COLOR = { 0, 255, 0, 255 };
static const Color TEXT_ITEM_SELECTED_OFF_COLOR = { 255, 0, 0, 255 };

// Forward declaration of helper functions
static char* CopyString(const char* source);

TextItem InitTextItem(const char* string, Color color, int alpha_value, int size) {
    TextItem item;
    
    // Initialize base item
    item.base = InitItem(color);
    
    // Override the draw function to use DrawTextItem
    item.base.draw = (DrawItemFunc)DrawTextItem;
    
    // Initialize text properties
    item.string = CopyString(string);
    item.off_string = CopyString(string);
    item.font_size = (size > 0) ? size : TEXT_ITEM_FONT_SIZE;
    item.font_color = color;
    item.selected_font_color = item.base.selected_color;
    item.on_font_color = TEXT_ITEM_ON_COLOR;
    item.off_font_color = TEXT_ITEM_OFF_COLOR;
    item.selected_on_font_color = TEXT_ITEM_SELECTED_ON_COLOR;
    item.selected_off_font_color = TEXT_ITEM_SELECTED_OFF_COLOR;
    item.alpha_value = alpha_value;
    
    // Initialize state
    item.is_on_off = false;
    item.on = false;
    
    // Initialize blinking properties
    item.blink = false;
    item.blink_rate = TEXT_ITEM_BLINK_RATE;
    item.blink_time_passed = 0.0f;
    
    // Use the global gameFont
    item.font = gameFont;
    
    // Setup item dimensions based on text size
    SetupTextItemSurfaces(&item);
    
    return item;
}

void UnloadTextItem(TextItem* item) {
    // Free strings
    if (item->string) {
        free(item->string);
    }
    
    if (item->off_string) {
        free(item->off_string);
    }
    
    // Note: We don't unload the font as it's managed globally
}

void SetupTextItemSurfaces(TextItem* item) {
    // We're not using textures anymore with our direct rendering approach
    // Just calculate the dimensions based on the text
    
    // Update the item's width and height based on the text size
    Vector2 text_size = MeasureTextEx(item->font, item->string, item->font_size, 0.0f);  // 0 spacing for bitmap font
    item->base.width = text_size.x;
    item->base.height = text_size.y;
    
    // Update the rectangles
    item->base.rect.width = text_size.x;
    item->base.rect.height = text_size.y;
    item->base.selected_rect.width = text_size.x + item->base.selected_border_size;
    item->base.selected_rect.height = text_size.y + item->base.selected_border_size;
    item->base.chosen_rect.width = text_size.x + item->base.chosen_border_size;
    item->base.chosen_rect.height = text_size.y + item->base.chosen_border_size;
    item->base.shadow_rect.width = text_size.x;
    item->base.shadow_rect.height = text_size.y;
}

void SetupTextItemIsOnOff(TextItem* item, const char* off_string, bool state) {
    // Set the textitem to be on/off toggle
    item->is_on_off = true;
    item->on = state;
    
    // Update off string
    if (item->off_string) {
        free(item->off_string);
    }
    item->off_string = CopyString(off_string);
    
    // No need to create any textures, we're using direct rendering
}

void SetTextItemSize(TextItem* item, int font_size) {
    if (item->font_size != font_size) {
        // Update font size
        item->font_size = font_size;
        
        // No need to reload the font, we're using the global gameFont
        // Just update dimensions
        SetupTextItemSurfaces(item);
        if (item->is_on_off) {
            SetupTextItemIsOnOff(item, item->off_string, item->on);
        }
    }
}

void SetTextItemString(TextItem* item, const char* string) {
    if (strcmp(item->string, string) != 0) {
        // Update string
        if (item->string) {
            free(item->string);
        }
        item->string = CopyString(string);
        
        // Regenerate surfaces
        SetupTextItemSurfaces(item);
    }
}

void SetTextItemBold(TextItem* item, bool choice) {
    // Raylib doesn't have a direct way to set bold, 
    // we would need to load a bold version of the font
    // This is a placeholder for compatibility
}

void SetTextItemItalic(TextItem* item, bool choice) {
    // Raylib doesn't have a direct way to set italic,
    // we would need to load an italic version of the font
    // This is a placeholder for compatibility
}

void SetTextItemColor(TextItem* item, Color color) {
    if (!ColorEquals(item->font_color, color)) {
        item->font_color = color;
        SetupTextItemSurfaces(item);
    }
}

float GetTextItemWidth(const TextItem* item) {
    Vector2 text_size = MeasureTextEx(item->font, item->string, item->font_size, 0.0f);  // 0 spacing for bitmap font
    return text_size.x;
}

float GetTextItemHeight(const TextItem* item) {
    Vector2 text_size = MeasureTextEx(item->font, item->string, item->font_size, 0.0f);  // 0 spacing for bitmap font
    return text_size.y;
}

void UpdateTextItem(TextItem* item, float delta_time) {
    // Update base item properties (animation, etc.)
    UpdateItem(&item->base, delta_time);
    
    // Handle blinking if enabled
    if (item->blink) {
        item->blink_time_passed += delta_time * 1000.0f; // Convert to milliseconds
        
        if (item->blink_time_passed > item->blink_rate) {
            // Toggle alpha (visibility)
            if (item->alpha_value == 255) {
                item->alpha_value = 0;
                item->blink_time_passed = item->blink_rate / 3.0f;
            } else {
                item->alpha_value = 255;
                item->blink_time_passed = 0;
            }
            
            // Note: In Raylib, we handle alpha at draw time
        }
    }
}

bool ToggleTextItemOnOff(TextItem* item) {
    item->on = !item->on;
    return item->on;
}
void DrawTextItem(const TextItem* item) {
    // Skip drawing if alpha is 0
    if (item->alpha_value == 0) {
        return;
    }
    
    // Calculate the position for the text to be centered on the item's position
    Vector2 text_size = MeasureTextEx(item->font, item->string, item->font_size, 0.0f);  // 0 spacing for bitmap font
    
    // Alpha to use for drawing
    float alpha_ratio = (float)item->alpha_value / 255.0f;
    
    // First draw the shadow
    if (item->is_on_off) {
        if (item->on) {
            // Draw shadow for "on" state
            Color shadow_color = ColorAlpha(item->base.shadow_color, alpha_ratio);
            DrawTextEx(item->font, item->string, 
                      (Vector2){ floorf(item->base.x + item->base.shadow_offset_x), 
                                floorf(item->base.y + item->base.shadow_offset_y + item->base.y_nudge) },
                      item->font_size, 0.0f, shadow_color);  // 0 spacing for bitmap font
        } else {
            // Draw shadow for "off" state
            Color shadow_color = ColorAlpha(item->base.shadow_color, alpha_ratio);
            Vector2 off_text_size = MeasureTextEx(item->font, item->off_string, item->font_size, 0.0f);  // 0 spacing for bitmap font
            DrawTextEx(item->font, item->off_string, 
                      (Vector2){ floorf(item->base.x + item->base.shadow_offset_x), 
                                floorf(item->base.y + item->base.shadow_offset_y + item->base.y_nudge) },
                      item->font_size, 0.0f, shadow_color);  // 0 spacing for bitmap font
        }
    } else {
        // Draw shadow for normal state
        Color shadow_color = ColorAlpha(item->base.shadow_color, alpha_ratio);
        DrawTextEx(item->font, item->string, 
                  (Vector2){ floorf(item->base.x + item->base.shadow_offset_x), 
                            floorf(item->base.y + item->base.shadow_offset_y + item->base.y_nudge) },
                  item->font_size, 0.0f, shadow_color);  // 0 spacing for bitmap font
    }
    
    // Then draw the text
    if (item->base.selected) {
        if (item->is_on_off) {
            if (item->on) {
                // Draw selected "on" text
                Color text_color = ColorAlpha(item->selected_on_font_color, alpha_ratio);
                DrawTextEx(item->font, item->string, 
                          (Vector2){ floorf(item->base.x), floorf(item->base.y + item->base.y_nudge) },
                          item->font_size, 0.0f, text_color);
            } else {
                // Draw selected "off" text
                Color text_color = ColorAlpha(item->selected_off_font_color, alpha_ratio);
                Vector2 off_text_size = MeasureTextEx(item->font, item->off_string, item->font_size, 0.0f);
                DrawTextEx(item->font, item->off_string, 
                          (Vector2){ floorf(item->base.x), floorf(item->base.y + item->base.y_nudge) },
                          item->font_size, 0.0f, text_color);
            }
        } else {
            // Draw selected text
            Color text_color = ColorAlpha(item->selected_font_color, alpha_ratio);
            DrawTextEx(item->font, item->string, 
                      (Vector2){ floorf(item->base.x), floorf(item->base.y + item->base.y_nudge) },
                      item->font_size, 0.0f, text_color);
        }
    } else if (item->is_on_off) {
        if (item->on) {
            // Draw "on" text
            Color text_color = ColorAlpha(item->on_font_color, alpha_ratio);
            DrawTextEx(item->font, item->string, 
                      (Vector2){ floorf(item->base.x), floorf(item->base.y + item->base.y_nudge) },
                      item->font_size, 0.0f, text_color);
        } else {
            // Draw "off" text
            Color text_color = ColorAlpha(item->off_font_color, alpha_ratio);
            Vector2 off_text_size = MeasureTextEx(item->font, item->off_string, item->font_size, 0.0f);
            DrawTextEx(item->font, item->off_string, 
                      (Vector2){ floorf(item->base.x), floorf(item->base.y + item->base.y_nudge) },
                      item->font_size, 0.0f, text_color);
        }
    } else {
        // Draw normal text
        Color text_color = ColorAlpha(item->font_color, alpha_ratio);
        DrawTextEx(item->font, item->string, 
                  (Vector2){ floorf(item->base.x), floorf(item->base.y + item->base.y_nudge) },
                  item->font_size, 0.0f, text_color);
    }

    DrawTextEx(item->font, item->string, (Vector2){ floorf(item->base.x + item->base.shadow_offset_x), floorf(item->base.y + item->base.shadow_offset_y + item->base.y_nudge) }, 32, 0.0f, WHITE);
}

TextItem** GenerateListFromString(const char* string, int* count) {
    if (!string || !count) {
        return NULL;
    }
    
    // Get string length
    int length = strlen(string);
    *count = length;
    
    if (length == 0) {
        return NULL;
    }
    
    // Allocate array for TextItem pointers
    TextItem** list = (TextItem**)malloc(length * sizeof(TextItem*));
    if (!list) {
        *count = 0;
        return NULL;
    }
    
    // Create a TextItem for each character
    for (int i = 0; i < length; i++) {
        char letter[2] = { string[i], '\0' };
        
        // Allocate memory for the TextItem
        list[i] = (TextItem*)malloc(sizeof(TextItem));
        if (!list[i]) {
            // Clean up previously allocated items
            for (int j = 0; j < i; j++) {
                UnloadTextItem(list[j]);
                free(list[j]);
            }
            free(list);
            *count = 0;
            return NULL;
        }
        
        // Initialize the TextItem
        *list[i] = InitTextItem(letter, (Color){ 128, 128, 128, 255 }, 255, 0);
    }
    
    return list;
}

// Helper function to create a deep copy of a string
static char* CopyString(const char* source) {
    if (!source) {
        return NULL;
    }
    
    size_t len = strlen(source) + 1;
    char* dest = (char*)malloc(len);
    
    if (dest) {
        memcpy(dest, source, len);
    }
    
    return dest;
} 