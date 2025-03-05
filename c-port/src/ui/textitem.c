/**
 * @file textitem.c
 * @brief Implementation of the TextItem UI component.
 */

#include "ui/textitem.h"
#include "ui/utils.h"
#include <stdlib.h>
#include <string.h>
#include <stdio.h>

// Default font values
#define TEXT_ITEM_FONT_PATH "resources/fonts/ADDLG___.TTF"
#define TEXT_ITEM_FONT_SIZE 9
#define TEXT_ITEM_BLINK_RATE 750.0f

// Default colors
static const Color TEXT_ITEM_ON_COLOR = { 0, 90, 0, 255 };
static const Color TEXT_ITEM_OFF_COLOR = { 90, 0, 0, 255 };
static const Color TEXT_ITEM_SELECTED_ON_COLOR = { 0, 255, 0, 255 };
static const Color TEXT_ITEM_SELECTED_OFF_COLOR = { 255, 0, 0, 255 };

// Forward declaration of helper functions
static char* CopyString(const char* source);
static void RenderTextToTexture(TextItem* item, Texture2D* texture, const char* text, Color color);

TextItem InitTextItem(const char* string, Color color, int alpha_value, int size) {
    TextItem item;
    
    // Initialize base item
    item.base = InitItem(color);
    
    // Initialize text properties
    item.string = CopyString(string);
    item.off_string = CopyString(string);
    item.font_path = CopyString(TEXT_ITEM_FONT_PATH);
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
    
    // Initialize font
    item.font = LoadFont(item.font_path);
    
    // Mark textures as not initialized yet
    item.textures_initialized = false;
    
    // Setup the surfaces/textures for rendering
    SetupTextItemSurfaces(&item);
    
    return item;
}

void UnloadTextItem(TextItem* item) {
    // Free allocated strings
    if (item->string) {
        free(item->string);
        item->string = NULL;
    }
    
    if (item->off_string) {
        free(item->off_string);
        item->off_string = NULL;
    }
    
    if (item->font_path) {
        free(item->font_path);
        item->font_path = NULL;
    }
    
    // Unload font
    UnloadFont(item->font);
    
    // Unload textures if they were initialized
    if (item->textures_initialized) {
        UnloadTexture(item->surface);
        UnloadTexture(item->selected_surface);
        UnloadTexture(item->shadow_surface);
        
        if (item->is_on_off) {
            UnloadTexture(item->on_surface);
            UnloadTexture(item->off_surface);
            UnloadTexture(item->selected_on_surface);
            UnloadTexture(item->selected_off_surface);
            UnloadTexture(item->shadow_off_surface);
        }
    }
}

void SetupTextItemSurfaces(TextItem* item) {
    // If textures were already initialized, unload them first
    if (item->textures_initialized) {
        UnloadTexture(item->surface);
        UnloadTexture(item->selected_surface);
        UnloadTexture(item->shadow_surface);
    }
    
    // Render the regular text texture
    RenderTextToTexture(item, &item->surface, item->string, item->font_color);
    
    // Render the selected text texture
    RenderTextToTexture(item, &item->selected_surface, item->string, item->selected_font_color);
    
    // Render the shadow text texture
    RenderTextToTexture(item, &item->shadow_surface, item->string, item->base.shadow_color);
    
    // Set the alpha for all textures
    // Note: In Raylib, we would handle alpha at draw time since textures don't have alpha property
    
    // Mark textures as initialized
    item->textures_initialized = true;
    
    // Update the item's width and height based on the text size
    Vector2 text_size = MeasureTextEx(item->font, item->string, item->font_size, 1.0f);
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
    // If textures were already initialized for on/off state, unload them first
    if (item->textures_initialized && item->is_on_off) {
        UnloadTexture(item->on_surface);
        UnloadTexture(item->off_surface);
        UnloadTexture(item->selected_on_surface);
        UnloadTexture(item->selected_off_surface);
        UnloadTexture(item->shadow_off_surface);
    }
    
    // Set the textitem to be on/off toggle
    item->is_on_off = true;
    item->on = state;
    
    // Update off string
    if (item->off_string) {
        free(item->off_string);
    }
    item->off_string = CopyString(off_string);
    
    // Render the on text texture
    RenderTextToTexture(item, &item->on_surface, item->string, item->on_font_color);
    
    // Render the off text texture
    RenderTextToTexture(item, &item->off_surface, item->off_string, item->off_font_color);
    
    // Render the selected and on texture
    RenderTextToTexture(item, &item->selected_on_surface, item->string, item->selected_on_font_color);
    
    // Render the selected and off texture
    RenderTextToTexture(item, &item->selected_off_surface, item->off_string, item->selected_off_font_color);
    
    // Render the shadow off texture
    RenderTextToTexture(item, &item->shadow_off_surface, item->off_string, item->base.shadow_color);
}

void SetTextItemFont(TextItem* item, const char* font_path) {
    if (strcmp(item->font_path, font_path) != 0) {
        // Unload the old font
        UnloadFont(item->font);
        
        // Update font path
        if (item->font_path) {
            free(item->font_path);
        }
        item->font_path = CopyString(font_path);
        
        // Load the new font
        item->font = LoadFont(item->font_path);
        
        // Regenerate all surfaces
        SetupTextItemSurfaces(item);
        if (item->is_on_off) {
            SetupTextItemIsOnOff(item, item->off_string, item->on);
        }
    }
}

void SetTextItemSize(TextItem* item, int font_size) {
    if (item->font_size != font_size) {
        // Update font size
        item->font_size = font_size;
        
        // Unload the old font
        UnloadFont(item->font);
        
        // Load the new font with updated size
        item->font = LoadFont(item->font_path);
        
        // Regenerate all surfaces
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
    Vector2 text_size = MeasureTextEx(item->font, item->string, item->font_size, 1.0f);
    return text_size.x;
}

float GetTextItemHeight(const TextItem* item) {
    Vector2 text_size = MeasureTextEx(item->font, item->string, item->font_size, 1.0f);
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
    
    // Alpha to use for drawing
    float alpha_ratio = (float)item->alpha_value / 255.0f;
    
    // First draw the shadow
    if (item->is_on_off) {
        if (item->on) {
            // Draw shadow for "on" state
            Color shadow_color = ColorAlpha(item->base.shadow_color, alpha_ratio);
            DrawTextEx(item->font, item->string, 
                      (Vector2){ item->base.x + item->base.shadow_offset_x, 
                                 item->base.y + item->base.shadow_offset_y + item->base.y_nudge },
                      item->font_size, 1.0f, shadow_color);
        } else {
            // Draw shadow for "off" state
            Color shadow_color = ColorAlpha(item->base.shadow_color, alpha_ratio);
            DrawTextEx(item->font, item->off_string, 
                      (Vector2){ item->base.x + item->base.shadow_offset_x, 
                                 item->base.y + item->base.shadow_offset_y + item->base.y_nudge },
                      item->font_size, 1.0f, shadow_color);
        }
    } else {
        // Draw shadow for normal state
        Color shadow_color = ColorAlpha(item->base.shadow_color, alpha_ratio);
        DrawTextEx(item->font, item->string, 
                  (Vector2){ item->base.x + item->base.shadow_offset_x, 
                             item->base.y + item->base.shadow_offset_y + item->base.y_nudge },
                  item->font_size, 1.0f, shadow_color);
    }
    
    // Then draw the text
    if (item->base.selected) {
        if (item->is_on_off) {
            if (item->on) {
                // Draw selected "on" text
                Color text_color = ColorAlpha(item->selected_on_font_color, alpha_ratio);
                DrawTextEx(item->font, item->string, 
                          (Vector2){ item->base.x, item->base.y + item->base.y_nudge },
                          item->font_size, 1.0f, text_color);
            } else {
                // Draw selected "off" text
                Color text_color = ColorAlpha(item->selected_off_font_color, alpha_ratio);
                DrawTextEx(item->font, item->off_string, 
                          (Vector2){ item->base.x, item->base.y + item->base.y_nudge },
                          item->font_size, 1.0f, text_color);
            }
        } else {
            // Draw selected text
            Color text_color = ColorAlpha(item->selected_font_color, alpha_ratio);
            DrawTextEx(item->font, item->string, 
                      (Vector2){ item->base.x, item->base.y + item->base.y_nudge },
                      item->font_size, 1.0f, text_color);
        }
    } else if (item->is_on_off) {
        if (item->on) {
            // Draw "on" text
            Color text_color = ColorAlpha(item->on_font_color, alpha_ratio);
            DrawTextEx(item->font, item->string, 
                      (Vector2){ item->base.x, item->base.y + item->base.y_nudge },
                      item->font_size, 1.0f, text_color);
        } else {
            // Draw "off" text
            Color text_color = ColorAlpha(item->off_font_color, alpha_ratio);
            DrawTextEx(item->font, item->off_string, 
                      (Vector2){ item->base.x, item->base.y + item->base.y_nudge },
                      item->font_size, 1.0f, text_color);
        }
    } else {
        // Draw normal text
        Color text_color = ColorAlpha(item->font_color, alpha_ratio);
        DrawTextEx(item->font, item->string, 
                  (Vector2){ item->base.x, item->base.y + item->base.y_nudge },
                  item->font_size, 1.0f, text_color);
    }
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

// Helper function to render text to a texture
static void RenderTextToTexture(TextItem* item, Texture2D* texture, const char* text, Color color) {
    // In Raylib, we don't pre-render text to textures for simple cases
    // We'll just create a placeholder texture and render the text directly in the draw function
    // This is more efficient for text that changes frequently
    
    // For compatibility with the Python API, we'll create a small 1x1 texture
    // The actual rendering will happen in the DrawTextItem function
    Image img = GenImageColor(1, 1, color);
    *texture = LoadTextureFromImage(img);
    UnloadImage(img);
} 