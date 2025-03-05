/**
 * @file item.h
 * @brief Base class for UI items.
 */

#ifndef ITEM_H
#define ITEM_H

#include "raylib.h"

// Forward declaration to resolve circular dependency
struct Item;

/**
 * @brief Function pointer type for drawing items
 */
typedef void (*DrawItemFunc)(const struct Item* item);

/**
 * @brief Item structure representing a basic UI element.
 * 
 * This is the base structure for all UI items. Items can be selected,
 * chosen or disabled. Each item is drawn differently depending on these states.
 */
typedef struct Item {
    // Position and size
    float x;
    float y;
    float width;
    float height;
    
    // States
    bool selected;
    bool chosen;
    bool disabled;
    
    // Colors
    Color color;
    Color shadow_color;
    Color selected_color;
    Color chosen_color;
    Color disabled_color;
    
    // Shadow properties
    float shadow_offset_x;
    float shadow_offset_y;
    
    // Border sizes
    float selected_border_size;
    float chosen_border_size;
    
    // Animation properties
    float x_nudge;
    float y_nudge;
    float max_x_nudge;
    float max_y_nudge;
    float x_nudge_retreat_speed;
    float y_nudge_retreat_speed;
    float time_passed;
    
    // Rects for drawing - represented as Rectangles in Raylib
    Rectangle rect;
    Rectangle selected_rect;
    Rectangle chosen_rect;
    Rectangle shadow_rect;
    
    // Function pointer for drawing - enables polymorphism
    DrawItemFunc draw;
} Item;

/**
 * @brief Initialize an Item with default values.
 * 
 * @param color The color of the item.
 * @return An initialized Item.
 */
Item InitItem(Color color);

/**
 * @brief Get the width of the item.
 * 
 * @param item Pointer to the item.
 * @return The width of the item.
 */
float GetItemWidth(const Item* item);

/**
 * @brief Get the height of the item.
 * 
 * @param item Pointer to the item.
 * @return The height of the item.
 */
float GetItemHeight(const Item* item);

/**
 * @brief Update the item's state and animations.
 * 
 * @param item Pointer to the item to update.
 * @param delta_time The time passed since the last frame in seconds.
 */
void UpdateItem(Item* item, float delta_time);

/**
 * @brief Draw the item to the screen.
 * 
 * @param item Pointer to the item to draw.
 */
void DrawItem(const Item* item);

/**
 * @brief Default drawing implementation for base items.
 * 
 * @param item Pointer to the item to draw.
 */
void DrawDefaultItem(const Item* item);

/**
 * @brief Called before drawing the disabled state.
 * 
 * This function can be overridden by derived item types.
 * 
 * @param item Pointer to the item.
 */
void DrawBeforeDisabledItem(const Item* item);

#endif // ITEM_H 