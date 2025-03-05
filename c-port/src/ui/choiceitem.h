/**
 * @file choiceitem.h
 * @brief Choice item component for UI.
 */

#ifndef CHOICEITEM_H
#define CHOICEITEM_H

#include "raylib.h"
#include "ui/item.h"

/**
 * @brief ChoiceItem structure for displaying a single text value in UI.
 * 
 * This displays a single text value in the middle of the item.
 * It inherits from Item and provides simple text rendering.
 */
typedef struct ChoiceItem {
    // Base item properties
    Item base;
    
    // Font properties
    Font font;
    
    // Text properties
    char* value;
    Color font_color;
    int alpha_value;
    
    // Font rendering surface
    Texture2D font_surface;
} ChoiceItem;

/**
 * @brief Initialize a ChoiceItem with the given value.
 * 
 * @param value The text value to display.
 * @param color The background color for the item.
 * @param font_color The color for the text.
 * @param alpha_value The alpha value for transparency.
 * @return An initialized ChoiceItem.
 */
ChoiceItem InitChoiceItem(const char* value, Color color, Color font_color, int alpha_value);

/**
 * @brief Clean up resources used by a ChoiceItem.
 * 
 * @param item Pointer to the ChoiceItem to clean up.
 */
void UnloadChoiceItem(ChoiceItem* item);

/**
 * @brief Update the ChoiceItem's state.
 * 
 * @param item Pointer to the ChoiceItem to update.
 * @param delta_time The time passed since the last frame in seconds.
 */
void UpdateChoiceItem(ChoiceItem* item, float delta_time);

/**
 * @brief Draw the ChoiceItem to the screen.
 * 
 * @param item Pointer to the ChoiceItem to draw.
 */
void DrawChoiceItem(const ChoiceItem* item);

#endif // CHOICEITEM_H 