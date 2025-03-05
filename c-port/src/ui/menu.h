/**
 * @file menu.h
 * @brief Base menu component for UI.
 */

#ifndef MENU_H
#define MENU_H

#include "raylib.h"
#include <stddef.h>
#include <stdbool.h>

// Forward declarations
typedef struct Item Item;
typedef struct TextItem TextItem;

/**
 * @brief Function pointer type for menu item functions.
 * 
 * This defines the signature for functions that can be attached to menu items.
 */
typedef void (*MenuItemFunction)(void* data);

/**
 * @brief Menu structure for creating interactive menus.
 * 
 * This is the base menu class. It can be placed anywhere in the game screen, and if items
 * (TextItems, ImageItems, ColorItems, ChoiceItems, etc.) are added to it, those items are
 * displayed in a top-to-bottom fashion. It can also register a function to each item so that
 * when that item is clicked, the corresponding function is called.
 */
typedef struct Menu {
    // Menu items
    Item** items;
    int item_count;
    int item_capacity;
    
    // Other menus to coordinate with
    struct Menu** other_menus;
    int other_menu_count;
    int other_menu_capacity;
    
    // Function mapping
    MenuItemFunction* functions;
    void** function_data;
    
    // Previously selected item for sound effect
    Item* previous_selected_item;
    
    // Menu position
    int position;
    float x;
    float y;
    
    // Sound effect for selection
    Sound sound_effect;
    bool sound_loaded;
} Menu;

/**
 * @brief Initialize a Menu.
 * 
 * @param x The x coordinate of the menu.
 * @param y The y coordinate of the menu.
 * @param position The starting position in the menu.
 * @return An initialized Menu.
 */
Menu InitMenu(float x, float y, int position);

/**
 * @brief Clean up resources used by a Menu.
 * 
 * @param menu Pointer to the Menu to clean up.
 */
void UnloadMenu(Menu* menu);

/**
 * @brief Get the width of the menu.
 * 
 * @param menu Pointer to the Menu.
 * @return The width of the menu.
 */
float GetMenuWidth(const Menu* menu);

/**
 * @brief Get the height of the menu.
 * 
 * @param menu Pointer to the Menu.
 * @return The height of the menu.
 */
float GetMenuHeight(const Menu* menu);

/**
 * @brief Add an item to the menu with an associated function.
 * 
 * @param menu Pointer to the Menu.
 * @param item Pointer to the Item to add.
 * @param function Function to call when the item is activated.
 * @param data Data to pass to the function when called.
 */
void AddMenuItem(Menu* menu, Item* item, MenuItemFunction function, void* data);

/**
 * @brief Position an item within the menu.
 * 
 * @param menu Pointer to the Menu.
 * @param item Pointer to the Item to position.
 */
void PositionMenuItem(Menu* menu, Item* item);

/**
 * @brief Remove an item from the menu.
 * 
 * @param menu Pointer to the Menu.
 * @param item Pointer to the Item to remove.
 */
void RemoveMenuItem(Menu* menu, Item* item);

/**
 * @brief Cleanup and reposition all items in the menu.
 * 
 * @param menu Pointer to the Menu.
 */
void CleanupMenu(Menu* menu);

/**
 * @brief Register other menus to coordinate with.
 * 
 * @param menu Pointer to the Menu.
 * @param other_menus Array of Menu pointers to register.
 * @param count Number of menus in the array.
 */
void RegisterOtherMenus(Menu* menu, Menu** other_menus, int count);

/**
 * @brief Check if the mouse is over an item in the menu.
 * 
 * @param menu Pointer to the Menu.
 * @param item Pointer to the Item to check.
 * @param mouse_pos The mouse position.
 * @return True if the mouse is over the item, false otherwise.
 */
bool IsMouseOverMenuItem(const Menu* menu, const Item* item, Vector2 mouse_pos);

/**
 * @brief Update the menu state.
 * 
 * @param menu Pointer to the Menu to update.
 * @param delta_time The time passed since the last frame in seconds.
 */
void UpdateMenu(Menu* menu, float delta_time);

/**
 * @brief Draw the menu to the screen.
 * 
 * @param menu Pointer to the Menu to draw.
 */
void DrawMenu(const Menu* menu);

/**
 * @brief Set the sound effect for menu item selection.
 *
 * @param menu Pointer to the Menu.
 * @param sound_path Path to the sound file.
 */
void SetMenuSoundEffect(Menu* menu, const char* sound_path);

#endif // MENU_H 