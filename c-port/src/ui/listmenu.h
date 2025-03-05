/**
 * @file listmenu.h
 * @brief List menu component for UI.
 */

#ifndef LISTMENU_H
#define LISTMENU_H

#include "raylib.h"
#include "ui/menu.h"

/**
 * @brief ListMenu structure for creating vertical list menus.
 * 
 * A variant of the menu that displays items in a top-to-bottom fashion.
 */
typedef struct ListMenu {
    // Base menu properties
    Menu base;
} ListMenu;

/**
 * @brief Initialize a ListMenu.
 * 
 * @param x The x coordinate of the menu.
 * @param y The y coordinate of the menu.
 * @param position The starting position in the menu.
 * @return An initialized ListMenu.
 */
ListMenu InitListMenu(float x, float y, int position);

/**
 * @brief Clean up resources used by a ListMenu.
 * 
 * @param menu Pointer to the ListMenu to clean up.
 */
void UnloadListMenu(ListMenu* menu);

/**
 * @brief Position an item within the list menu.
 * 
 * @param menu Pointer to the ListMenu.
 * @param item Pointer to the Item to position.
 */
void PositionListMenuItem(ListMenu* menu, Item* item);

/**
 * @brief Add an item to the list menu with an associated function.
 * 
 * @param menu Pointer to the ListMenu.
 * @param item Pointer to the Item to add.
 * @param function Function to call when the item is activated.
 * @param data Data to pass to the function when called.
 */
void AddListMenuItem(ListMenu* menu, Item* item, MenuItemFunction function, void* data);

/**
 * @brief Update the list menu state.
 * 
 * @param menu Pointer to the ListMenu to update.
 * @param delta_time The time passed since the last frame in seconds.
 */
void UpdateListMenu(ListMenu* menu, float delta_time);

/**
 * @brief Draw the list menu to the screen.
 * 
 * @param menu Pointer to the ListMenu to draw.
 */
void DrawListMenu(const ListMenu* menu);

#endif // LISTMENU_H 