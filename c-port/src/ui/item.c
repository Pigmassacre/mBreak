/**
 * @file item.c
 * @brief Implementation of the base UI item.
 */

#include "ui/item.h"
#include <math.h>

// Define default values for the Item class
#define ITEM_DEFAULT_WIDTH 16
#define ITEM_DEFAULT_HEIGHT 16
#define ITEM_SHADOW_OFFSET_X 0
#define ITEM_SHADOW_OFFSET_Y 1
#define ITEM_SELECTED_BORDER_SIZE 2
#define ITEM_CHOSEN_BORDER_SIZE 2
#define ITEM_MAX_X_NUDGE 2
#define ITEM_MAX_Y_NUDGE 2

Item InitItem(Color color) {
    Item item;
    
    // Initialize position and size
    item.x = 0;
    item.y = 0;
    item.width = ITEM_DEFAULT_WIDTH;
    item.height = ITEM_DEFAULT_HEIGHT;
    
    // Initialize states
    item.selected = false;
    item.chosen = false;
    item.disabled = false;
    
    // Initialize colors
    item.color = color;
    item.shadow_color = (Color){ 50, 50, 50, 255 };
    item.selected_color = (Color){ 255, 255, 255, 255 };
    item.chosen_color = (Color){ 200, 200, 200, 255 };
    item.disabled_color = (Color){ 75, 75, 75, 240 };
    
    // Initialize shadow properties
    item.shadow_offset_x = ITEM_SHADOW_OFFSET_X;
    item.shadow_offset_y = ITEM_SHADOW_OFFSET_Y;
    
    // Initialize border sizes
    item.selected_border_size = ITEM_SELECTED_BORDER_SIZE;
    item.chosen_border_size = ITEM_CHOSEN_BORDER_SIZE;
    
    // Initialize animation properties
    item.x_nudge = 0;
    item.y_nudge = 0;
    item.max_x_nudge = ITEM_MAX_X_NUDGE;
    item.max_y_nudge = ITEM_MAX_Y_NUDGE;
    item.x_nudge_retreat_speed = 0.1f * 60.0f; // Assuming 60 FPS
    item.y_nudge_retreat_speed = 0.1f * 60.0f; // Assuming 60 FPS
    item.time_passed = 0;
    
    // Initialize rectangles
    item.rect = (Rectangle){ item.x, item.y, item.width, item.height };
    item.selected_rect = (Rectangle){ 
        item.x - (ITEM_SELECTED_BORDER_SIZE / 2.0f), 
        item.y - (ITEM_SELECTED_BORDER_SIZE / 2.0f), 
        item.width + ITEM_SELECTED_BORDER_SIZE, 
        item.height + ITEM_SELECTED_BORDER_SIZE 
    };
    item.chosen_rect = (Rectangle){ 
        item.x - (ITEM_CHOSEN_BORDER_SIZE / 2.0f), 
        item.y - (ITEM_CHOSEN_BORDER_SIZE / 2.0f), 
        item.width + ITEM_CHOSEN_BORDER_SIZE, 
        item.height + ITEM_CHOSEN_BORDER_SIZE 
    };
    item.shadow_rect = (Rectangle){ 
        item.x + item.shadow_offset_x, 
        item.y + item.shadow_offset_y, 
        item.width, 
        item.height 
    };
    
    return item;
}

float GetItemWidth(const Item* item) {
    return item->rect.width;
}

float GetItemHeight(const Item* item) {
    return item->rect.height;
}

void UpdateItem(Item* item, float delta_time) {
    if (item->selected) {
        // Animate the y_nudge based on sine wave for a hovering effect
        item->y_nudge = -((sinf(item->time_passed * 0.0075f) + 1.0f) / 2.0f) * item->max_y_nudge;
        item->time_passed += delta_time * 1000.0f; // Convert to milliseconds
    } else {
        // Reset the animation when not selected
        item->time_passed = 0;
        
        // Gradually return to neutral position
        if (item->y_nudge < 0) {
            item->y_nudge += item->y_nudge_retreat_speed * delta_time;
            if (item->y_nudge > 0) {
                item->y_nudge = 0;
            }
        } else if (item->y_nudge > 0) {
            item->y_nudge -= item->y_nudge_retreat_speed * delta_time;
            if (item->y_nudge < 0) {
                item->y_nudge = 0;
            }
        }
    }
    
    // Clamp nudge values
    if (item->x_nudge < -item->max_x_nudge) {
        item->x_nudge = -item->max_x_nudge;
    } else if (item->x_nudge > item->max_x_nudge) {
        item->x_nudge = item->max_x_nudge;
    }
    
    if (item->y_nudge < -item->max_y_nudge) {
        item->y_nudge = -item->max_y_nudge;
    } else if (item->y_nudge > item->max_y_nudge) {
        item->y_nudge = item->max_y_nudge;
    }
    
    // Update rectangle positions
    item->rect.x = item->x + item->x_nudge;
    item->rect.y = item->y + item->y_nudge;
    
    item->selected_rect.x = item->x - (item->selected_border_size / 2.0f) + item->x_nudge;
    item->selected_rect.y = item->y - (item->selected_border_size / 2.0f) + item->y_nudge;
    
    item->chosen_rect.x = item->x - (item->chosen_border_size / 2.0f) + item->x_nudge;
    item->chosen_rect.y = item->y - (item->chosen_border_size / 2.0f) + item->y_nudge;
    
    item->shadow_rect.x = item->x + item->shadow_offset_x + item->x_nudge;
    item->shadow_rect.y = item->y + item->shadow_offset_y + item->y_nudge;
}

void DrawItem(const Item* item) {
    // Draw the shadow
    DrawRectangleRec(item->shadow_rect, item->shadow_color);
    
    // If chosen, draw the chosen border
    if (item->chosen) {
        DrawRectangleRec(item->chosen_rect, item->chosen_color);
        
        // If also selected, draw a smaller selected border
        if (item->selected) {
            DrawRectangleRec(item->rect, item->selected_color);
        }
    }
    else if (item->selected) {
        // If selected, draw the selected border
        DrawRectangleRec(item->selected_rect, item->selected_color);
    }
    
    // Draw the main color of the item
    DrawRectangleRec(item->rect, item->color);
    
    // Call pre-disabled hook
    DrawBeforeDisabledItem(item);
    
    // If disabled, draw the disabled overlay
    if (item->disabled) {
        DrawRectangleRec(item->rect, item->disabled_color);
    }
}

void DrawBeforeDisabledItem(const Item* item) {
    // This is an empty implementation, intended to be overridden by derived types
    // It's called before drawing the disabled state
    (void)item; // Avoid unused parameter warning
} 