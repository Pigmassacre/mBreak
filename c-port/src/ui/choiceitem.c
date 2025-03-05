/**
 * @file choiceitem.c
 * @brief Implementation of the ChoiceItem UI component.
 */

#include "ui/choiceitem.h"
#include <stdlib.h>
#include <string.h>

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

// Helper function to copy an array of strings
static char** CopyStringArray(const char** source, int count) {
    if (!source || count <= 0) {
        return NULL;
    }
    
    char** dest = (char**)malloc(count * sizeof(char*));
    if (!dest) {
        return NULL;
    }
    
    for (int i = 0; i < count; i++) {
        dest[i] = CopyString(source[i]);
        if (!dest[i]) {
            // Clean up on failure
            for (int j = 0; j < i; j++) {
                free(dest[j]);
            }
            free(dest);
            return NULL;
        }
    }
    
    return dest;
}

ChoiceItem InitChoiceItem(const char** choices, int choice_count, int position, Color color) {
    ChoiceItem item;
    
    // Initialize base item
    item.base = InitItem(color);
    
    // Copy the choices
    item.choices = CopyStringArray(choices, choice_count);
    item.choice_count = choice_count;
    
    // Set the initial position
    item.position = (position >= 0 && position < choice_count) ? position : 0;
    
    // Initialize the text item with the current choice
    item.text_item = InitTextItem(choices[item.position], color, 255, 0);
    item.owns_text_item = true;
    
    return item;
}

ChoiceItem InitChoiceItemWithTextItem(const char** choices, int choice_count, int position, TextItem* text_item) {
    ChoiceItem item;
    
    // Initialize base item
    item.base = InitItem(text_item->base.color);
    
    // Copy the choices
    item.choices = CopyStringArray(choices, choice_count);
    item.choice_count = choice_count;
    
    // Set the initial position
    item.position = (position >= 0 && position < choice_count) ? position : 0;
    
    // Use the provided text item
    item.text_item = *text_item;
    item.owns_text_item = false;
    
    // Update the text item's string to the current choice
    SetTextItemString(&item.text_item, choices[item.position]);
    
    return item;
}

void UnloadChoiceItem(ChoiceItem* item) {
    // Free the choices
    if (item->choices) {
        for (int i = 0; i < item->choice_count; i++) {
            if (item->choices[i]) {
                free(item->choices[i]);
                item->choices[i] = NULL;
            }
        }
        free(item->choices);
        item->choices = NULL;
    }
    
    // Unload the text item if we own it
    if (item->owns_text_item) {
        UnloadTextItem(&item->text_item);
    }
}

const char* GetChoiceItemText(const ChoiceItem* item) {
    if (item->position >= 0 && item->position < item->choice_count) {
        return item->choices[item->position];
    }
    return "";
}

int GetChoiceItemPosition(const ChoiceItem* item) {
    return item->position;
}

void SetChoiceItemPosition(ChoiceItem* item, int position) {
    // Ensure position is within bounds
    if (position < 0) {
        position = 0;
    } else if (position >= item->choice_count) {
        position = item->choice_count - 1;
    }
    
    // Update position and text
    item->position = position;
    SetTextItemString(&item->text_item, item->choices[position]);
}

int NextChoiceItemPosition(ChoiceItem* item) {
    // Move to the next position, wrapping around if necessary
    item->position = (item->position + 1) % item->choice_count;
    
    // Update the text
    SetTextItemString(&item->text_item, item->choices[item->position]);
    
    return item->position;
}

int PreviousChoiceItemPosition(ChoiceItem* item) {
    // Move to the previous position, wrapping around if necessary
    item->position = (item->position - 1 + item->choice_count) % item->choice_count;
    
    // Update the text
    SetTextItemString(&item->text_item, item->choices[item->position]);
    
    return item->position;
}

float GetChoiceItemWidth(const ChoiceItem* item) {
    return GetTextItemWidth(&item->text_item);
}

float GetChoiceItemHeight(const ChoiceItem* item) {
    return GetTextItemHeight(&item->text_item);
}

void UpdateChoiceItem(ChoiceItem* item, float delta_time) {
    // Update base item for animations, etc.
    UpdateItem(&item->base, delta_time);
    
    // Update the text item
    UpdateTextItem(&item->text_item, delta_time);
    
    // Sync positions
    item->text_item.base.x = item->base.x;
    item->text_item.base.y = item->base.y;
    
    // Sync states
    item->text_item.base.selected = item->base.selected;
    item->text_item.base.chosen = item->base.chosen;
    item->text_item.base.disabled = item->base.disabled;
}

void DrawChoiceItem(const ChoiceItem* item) {
    // Draw the text item
    DrawTextItem(&item->text_item);
} 