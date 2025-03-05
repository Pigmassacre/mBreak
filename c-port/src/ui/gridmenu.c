/**
 * @file gridmenu.c
 * @brief Implementation of the GridMenu UI component.
 */

#include "ui/gridmenu.h"
#include "ui/item.h"

// Default offset between items
#define GRID_MENU_DEFAULT_OFFSET 2.0f

GridMenu InitGridMenu(float x, float y, int position, int max_number_of_columns) {
    GridMenu menu;
    
    // Initialize base menu
    menu.base = InitMenu(x, y, position);
    
    // Initialize grid properties
    menu.max_number_of_columns = max_number_of_columns;
    menu.offset = GRID_MENU_DEFAULT_OFFSET;
    
    // Initialize current state
    menu.current_row_size = 0;
    menu.current_row_position = y;
    
    return menu;
}

void UnloadGridMenu(GridMenu* menu) {
    // Unload base menu
    UnloadMenu(&menu->base);
}

void PopulateGridMenu(GridMenu* menu, Item* item, int row_size, float row_position, int* new_row_size, float* new_row_position) {
    // Populates the grid according to the max_number_of_columns
    if (row_size > menu->max_number_of_columns) {
        // If the row size is larger than the max number of columns,
        // we position the item below the last row and at the beginning of the new row
        row_size = 1;
        row_position = row_position + GetItemHeight(item) + menu->offset;
    }
    
    if (row_size > 1) {
        // If the row size is larger than one, we position the item to the right of the last item in the last row
        item->x = menu->base.x + (row_size - 1) * GetItemWidth(item) + (row_size - 1) * menu->offset;
        item->y = row_position;
    } else {
        // Otherwise, we position the item to the beginning of the row
        item->x = menu->base.x;
        item->y = row_position;
    }
    
    // Return the changed row_size and row_position
    *new_row_size = row_size;
    *new_row_position = row_position;
}

void PositionGridMenuItem(GridMenu* menu, Item* item) {
    // Increment the current row size
    menu->current_row_size++;
    
    // Populate the grid with the item, and update the current row size and position
    PopulateGridMenu(menu, item, menu->current_row_size, menu->current_row_position, 
                    &menu->current_row_size, &menu->current_row_position);
}

void AddGridMenuItem(GridMenu* menu, Item* item, MenuItemFunction function, void* data) {
    // Add the item to the base menu
    AddMenuItem(&menu->base, item, function, data);
    
    // Position the item according to grid menu layout
    PositionGridMenuItem(menu, item);
}

void CleanupGridMenu(GridMenu* menu) {
    // Reset the current row size and position
    menu->current_row_size = 0;
    menu->current_row_position = menu->base.y;
    
    // Call the base menu cleanup to reposition all items
    CleanupMenu(&menu->base);
}

void UpdateGridMenu(GridMenu* menu, float delta_time) {
    // Update the base menu
    UpdateMenu(&menu->base, delta_time);
}

void DrawGridMenu(const GridMenu* menu) {
    // Draw the base menu
    DrawMenu(&menu->base);
} 