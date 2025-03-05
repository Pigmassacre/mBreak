/**
 * @file traversal.h
 * @brief Header file for the Traversal UI component.
 * 
 * This module contains all the code that handles traversing through menus with
 * keyboard, gamepad, or mouse. To add key-traversal support to a menu (or a bunch
 * of menus at the same time), all the corresponding screen has to do is call the
 * traverse_menus function while checking all events.
 */

#ifndef TRAVERSAL_H
#define TRAVERSAL_H

#include "raylib.h"
#include "ui/menu.h"

/**
 * @brief Checks for any events that we care about, and then handles those events correctly
 *        in regards to the selected item in list_of_menus.
 * 
 * @param key The key that was pressed (KEY_NULL if no key was pressed)
 * @param mouse_position The current mouse position
 * @param mouse_clicked Whether the mouse was clicked
 * @param menus Array of menus that we should be able to traverse through
 * @param menu_count Number of menus in the array
 */
void TraverseMenus(int key, Vector2 mouse_position, bool mouse_clicked, Menu* menus[], int menu_count);

/**
 * @brief Tries to traverse to the left or right of the currently selected item.
 * 
 * The algorithm favors the item with the least x-distance to the selected item AND the least y-distance,
 * with focus on the y-distance being as low as possible.
 * 
 * @param menus Array of menus that we should be able to traverse through
 * @param menu_count Number of menus in the array
 * @param left If true, traverse left; if false, traverse right
 */
void SelectLeftOrRight(Menu* menus[], int menu_count, bool left);

/**
 * @brief Tries to traverse up or down from the currently selected item.
 * 
 * The algorithm favors the item with the least y-distance to the selected item AND the least x-distance,
 * with focus on the x-distance being as low as possible.
 * 
 * @param menus Array of menus that we should be able to traverse through
 * @param menu_count Number of menus in the array
 * @param up If true, traverse up; if false, traverse down
 */
void SelectUpOrDown(Menu* menus[], int menu_count, bool up);

/**
 * @brief Returns the first selected item in the given array of menus.
 * 
 * @param menus Array of menus to search through
 * @param menu_count Number of menus in the array
 * @return Item* Pointer to the selected item, or NULL if no item is selected
 */
Item* GetSelectedItem(Menu* menus[], int menu_count);

/**
 * @brief Fills an array with all items from all menus.
 * 
 * @param menus Array of menus to get items from
 * @param menu_count Number of menus in the array
 * @param items Array to fill with items (must be pre-allocated with enough space)
 * @return int The number of items added to the array
 */
int FillListOfPossible(Menu* menus[], int menu_count, Item* items[]);

#endif // TRAVERSAL_H 