/**
 * @file textitem.h
 * @brief Text item component for UI.
 */

#ifndef TEXTITEM_H
#define TEXTITEM_H

#include "raylib.h"
#include "ui/item.h"

/**
 * @brief TextItem structure for displaying text in UI.
 * 
 * This is a wrapper around Raylib's text rendering. It can be used in menus
 * or simply to display text. It has additional properties to function as a button.
 */
typedef struct TextItem {
    // Base item properties
    Item base;
    
    // Text properties
    char* string;
    char* off_string;
    Font font;
    int font_size;
    Color font_color;
    Color selected_font_color;
    Color on_font_color;
    Color off_font_color;
    Color selected_on_font_color;
    Color selected_off_font_color;
    int alpha_value;
    
    // State
    bool is_on_off;
    bool on;
    
    // Blinking properties
    bool blink;
    float blink_rate;
    float blink_time_passed;
} TextItem;

/**
 * @brief Initialize a TextItem with the given string and properties.
 * 
 * @param string The text to display.
 * @param color The color of the text.
 * @param alpha_value The alpha transparency (0-255).
 * @param size Optional font size, NULL for default.
 * @return An initialized TextItem.
 */
TextItem InitTextItem(const char* string, Color color, int alpha_value, int size);

/**
 * @brief Clean up resources used by a TextItem.
 * 
 * @param item Pointer to the TextItem to clean up.
 */
void UnloadTextItem(TextItem* item);

/**
 * @brief Set up the textures used for rendering the TextItem.
 * 
 * @param item Pointer to the TextItem.
 */
void SetupTextItemSurfaces(TextItem* item);

/**
 * @brief Set up the TextItem as an on/off toggle with separate states.
 * 
 * @param item Pointer to the TextItem.
 * @param off_string The text to display when in "off" state.
 * @param state The initial state (true = on, false = off).
 */
void SetupTextItemIsOnOff(TextItem* item, const char* off_string, bool state);

/**
 * @brief Change the displayed text.
 * 
 * @param item Pointer to the TextItem.
 * @param string The new text to display.
 */
void SetTextItemString(TextItem* item, const char* string);

/**
 * @brief Set the text to be bold.
 * 
 * @param item Pointer to the TextItem.
 * @param choice Whether text should be bold.
 */
void SetTextItemBold(TextItem* item, bool choice);

/**
 * @brief Set the text to be italic.
 * 
 * @param item Pointer to the TextItem.
 * @param choice Whether text should be italic.
 */
void SetTextItemItalic(TextItem* item, bool choice);

/**
 * @brief Change the color of the text.
 * 
 * @param item Pointer to the TextItem.
 * @param color The new color.
 */
void SetTextItemColor(TextItem* item, Color color);

/**
 * @brief Get the width of the text.
 * 
 * @param item Pointer to the TextItem.
 * @return The width of the text.
 */
float GetTextItemWidth(const TextItem* item);

/**
 * @brief Get the height of the text.
 * 
 * @param item Pointer to the TextItem.
 * @return The height of the text.
 */
float GetTextItemHeight(const TextItem* item);

/**
 * @brief Update the TextItem's state.
 * 
 * @param item Pointer to the TextItem to update.
 * @param delta_time The time passed since the last frame in seconds.
 */
void UpdateTextItem(TextItem* item, float delta_time);

/**
 * @brief Toggle the on/off state of the TextItem.
 * 
 * @param item Pointer to the TextItem.
 * @return The new state after toggle.
 */
bool ToggleTextItemOnOff(TextItem* item);

/**
 * @brief Draw the TextItem to the screen.
 * 
 * @param item Pointer to the TextItem to draw.
 */
void DrawTextItem(const TextItem* item);

/**
 * @brief Generate a list of TextItems from a string, one character per item.
 * 
 * @param string The string to convert.
 * @param count Pointer to store the number of items created.
 * @return Array of TextItem pointers, must be freed by caller.
 */
TextItem** GenerateListFromString(const char* string, int* count);

#endif // TEXTITEM_H 