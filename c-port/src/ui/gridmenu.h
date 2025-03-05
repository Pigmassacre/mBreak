/**
 * @file gridmenu.h
 * @brief Grid menu component for UI.
 */

#ifndef GRIDMENU_H
#define GRIDMENU_H

#include "raylib.h"
#include "ui/menu.h"

/**
 * @brief GridMenu structure for creating grid-based menus.
 * 
 * A variant of the menu that displays items in a grid (table) fashion.
 * The user can specify the max number of columns, and the GridMenu takes care
 * of positioning each of its items accordingly.
 */
typedef struct GridMenu {
    // Base menu properties
    Menu base;
    
    // Grid properties
    int max_number_of_columns;
    float offset;
    
    // Current state for positioning
    int current_row_size;
    float current_row_position;
} GridMenu;

/**
 * @brief Initialize a GridMenu.
 * 
 * @param x The x coordinate of the menu.
 * @param y The y coordinate of the menu.
 * @param position The starting position in the menu.
 * @param max_number_of_columns Maximum number of columns in the grid.
 * @return An initialized GridMenu.
 */
GridMenu InitGridMenu(float x, float y, int position, int max_number_of_columns);

/**
 * @brief Clean up resources used by a GridMenu.
 * 
 * @param menu Pointer to the GridMenu to clean up.
 */
void UnloadGridMenu(GridMenu* menu);

/**
 * @brief Position an item within the grid menu.
 * 
 * @param menu Pointer to the GridMenu.
 * @param item Pointer to the Item to position.
 */
void PositionGridMenuItem(GridMenu* menu, Item* item);

/**
 * @brief Helper function to populate the grid with an item.
 * 
 * @param menu Pointer to the GridMenu.
 * @param item Pointer to the Item to position.
 * @param row_size Current size of the row.
 * @param row_position Current position of the row.
 * @param new_row_size Pointer to store the new row size.
 * @param new_row_position Pointer to store the new row position.
 */
void PopulateGridMenu(GridMenu* menu, Item* item, int row_size, float row_position, int* new_row_size, float* new_row_position);

/**
 * @brief Add an item to the grid menu with an associated function.
 * 
 * @param menu Pointer to the GridMenu.
 * @param item Pointer to the Item to add.
 * @param function Function to call when the item is activated.
 * @param data Data to pass to the function when called.
 */
void AddGridMenuItem(GridMenu* menu, Item* item, MenuItemFunction function, void* data);

/**
 * @brief Cleanup and reposition all items in the grid menu.
 * 
 * @param menu Pointer to the GridMenu.
 */
void CleanupGridMenu(GridMenu* menu);

/**
 * @brief Update the grid menu state.
 * 
 * @param menu Pointer to the GridMenu to update.
 * @param delta_time The time passed since the last frame in seconds.
 */
void UpdateGridMenu(GridMenu* menu, float delta_time);

/**
 * @brief Draw the grid menu to the screen.
 * 
 * @param menu Pointer to the GridMenu to draw.
 */
void DrawGridMenu(const GridMenu* menu);

#endif // GRIDMENU_H 