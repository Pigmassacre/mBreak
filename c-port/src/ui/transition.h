/**
 * @file transition.h
 * @brief Transition component for UI.
 */

#ifndef TRANSITION_H
#define TRANSITION_H

#include "raylib.h"
#include "ui/menu.h"
#include <stdbool.h>

/**
 * @brief Position entry for storing item start positions.
 */
typedef struct TransitionPosition {
    Item* item;
    Vector2 position;
} TransitionPosition;

/**
 * @brief Transition structure for creating menu transitions.
 * 
 * This handles the menu transitions seen in all menus in the game.
 * It works with any item that has an x and y position.
 * You can either add single items or every item in a given menu.
 */
typedef struct Transition {
    // The speed at which each item moves
    float speed;
    
    // List of items registered to this transition
    Item** items;
    int item_count;
    int item_capacity;
    
    // Start positions for each item
    TransitionPosition* start_positions;
    int position_count;
    int position_capacity;
} Transition;

/**
 * @brief Initialize a Transition.
 * 
 * @return An initialized Transition.
 */
Transition InitTransition(void);

/**
 * @brief Clean up resources used by a Transition.
 * 
 * @param transition Pointer to the Transition to clean up.
 */
void UnloadTransition(Transition* transition);

/**
 * @brief Add all items from a menu to the transition.
 * 
 * @param transition Pointer to the Transition.
 * @param menu Pointer to the Menu containing items to add.
 */
void AddTransitionItems(Transition* transition, const Menu* menu);

/**
 * @brief Remove all items from the transition.
 * 
 * @param transition Pointer to the Transition.
 */
void RemoveAllTransitionItems(Transition* transition);

/**
 * @brief Set up a transition for a menu.
 * 
 * Adds all items from the menu and positions them outside the screen
 * according to the specified directions.
 * 
 * @param transition Pointer to the Transition.
 * @param menu Pointer to the Menu to set up.
 * @param left Allow items to come from the left.
 * @param right Allow items to come from the right.
 * @param up Allow items to come from the top.
 * @param down Allow items to come from the bottom.
 */
void SetupTransition(Transition* transition, Menu* menu, bool left, bool right, bool up, bool down);

/**
 * @brief Set up an odd-even transition for a menu.
 * 
 * Similar to SetupTransition, but alternates between opposite sides for consecutive items.
 * 
 * @param transition Pointer to the Transition.
 * @param menu Pointer to the Menu to set up.
 * @param left Allow items to come from the left.
 * @param right Allow items to come from the right.
 * @param up Allow items to come from the top.
 * @param down Allow items to come from the bottom.
 */
void SetupOddEvenTransition(Transition* transition, Menu* menu, bool left, bool right, bool up, bool down);

/**
 * @brief Set up a transition for a single item.
 * 
 * @param transition Pointer to the Transition.
 * @param item Pointer to the Item to set up.
 * @param left Allow the item to come from the left.
 * @param right Allow the item to come from the right.
 * @param up Allow the item to come from the top.
 * @param down Allow the item to come from the bottom.
 */
void SetupSingleItemTransition(Transition* transition, Item* item, bool left, bool right, bool up, bool down);

/**
 * @brief Update the transition animation.
 * 
 * @param transition Pointer to the Transition to update.
 * @param delta_time The time passed since the last frame in seconds.
 */
void UpdateTransition(Transition* transition, float delta_time);

#endif // TRANSITION_H 