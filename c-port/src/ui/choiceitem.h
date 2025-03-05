/**
 * @file choiceitem.h
 * @brief Choice item component for UI.
 */

#ifndef CHOICEITEM_H
#define CHOICEITEM_H

#include "raylib.h"
#include "ui/item.h"
#include "ui/textitem.h"

/**
 * @brief ChoiceItem structure for creating multi-option UI elements.
 * 
 * This represents an item with multiple selectable choices. It cycles through
 * options when activated, and can be used for settings or options menus.
 */
typedef struct ChoiceItem {
    // Base item properties
    Item base;
    
    // The choices available
    char** choices;
    int choice_count;
    
    // Current position in choices
    int position;
    
    // The TextItem used to display the current choice
    TextItem text_item;
    
    // Whether the TextItem was initialized by us (for cleanup)
    bool owns_text_item;
} ChoiceItem;

/**
 * @brief Initialize a ChoiceItem with the given choices.
 * 
 * @param choices Array of strings representing the available choices.
 * @param choice_count Number of choices in the array.
 * @param position Initial position/selected choice index.
 * @param color The color for the item.
 * @return An initialized ChoiceItem.
 */
ChoiceItem InitChoiceItem(const char** choices, int choice_count, int position, Color color);

/**
 * @brief Initialize a ChoiceItem that uses an existing TextItem.
 * 
 * @param choices Array of strings representing the available choices.
 * @param choice_count Number of choices in the array.
 * @param position Initial position/selected choice index.
 * @param text_item Pointer to an existing TextItem to use.
 * @return An initialized ChoiceItem.
 */
ChoiceItem InitChoiceItemWithTextItem(const char** choices, int choice_count, int position, TextItem* text_item);

/**
 * @brief Clean up resources used by a ChoiceItem.
 * 
 * @param item Pointer to the ChoiceItem to clean up.
 */
void UnloadChoiceItem(ChoiceItem* item);

/**
 * @brief Get the currently selected choice text.
 * 
 * @param item Pointer to the ChoiceItem.
 * @return The text of the current choice.
 */
const char* GetChoiceItemText(const ChoiceItem* item);

/**
 * @brief Get the currently selected choice index.
 * 
 * @param item Pointer to the ChoiceItem.
 * @return The index of the current choice.
 */
int GetChoiceItemPosition(const ChoiceItem* item);

/**
 * @brief Set the currently selected choice by index.
 * 
 * @param item Pointer to the ChoiceItem.
 * @param position The index to set as current choice.
 */
void SetChoiceItemPosition(ChoiceItem* item, int position);

/**
 * @brief Move to the next choice.
 * 
 * @param item Pointer to the ChoiceItem.
 * @return The new position after moving to the next choice.
 */
int NextChoiceItemPosition(ChoiceItem* item);

/**
 * @brief Move to the previous choice.
 * 
 * @param item Pointer to the ChoiceItem.
 * @return The new position after moving to the previous choice.
 */
int PreviousChoiceItemPosition(ChoiceItem* item);

/**
 * @brief Get the width of the ChoiceItem.
 * 
 * @param item Pointer to the ChoiceItem.
 * @return The width of the ChoiceItem.
 */
float GetChoiceItemWidth(const ChoiceItem* item);

/**
 * @brief Get the height of the ChoiceItem.
 * 
 * @param item Pointer to the ChoiceItem.
 * @return The height of the ChoiceItem.
 */
float GetChoiceItemHeight(const ChoiceItem* item);

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