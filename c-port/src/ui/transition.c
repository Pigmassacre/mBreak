/**
 * @file transition.c
 * @brief Implementation of the Transition UI component.
 */

#include "ui/transition.h"
#include "ui/item.h"
#include <stdlib.h>
#include <string.h>

// Default transition speed
#define TRANSITION_DEFAULT_SPEED (14.0f * 60.0f) // Assuming 60 FPS

// Initial capacity for arrays
#define INITIAL_CAPACITY 16

// Screen dimensions (should be defined elsewhere in a real project)
#define SCREEN_WIDTH 800
#define SCREEN_HEIGHT 600

// Direction enum for internal use
typedef enum {
    DIRECTION_LEFT,
    DIRECTION_RIGHT,
    DIRECTION_UP,
    DIRECTION_DOWN
} Direction;

// Helper function to grow an array
static void* GrowArray(void* array, size_t* capacity, size_t element_size) {
    size_t new_capacity = *capacity * 2;
    void* new_array = realloc(array, new_capacity * element_size);
    
    if (new_array) {
        *capacity = new_capacity;
    }
    
    return new_array;
}

// Helper function to find a position entry for an item
static int FindPositionIndex(const Transition* transition, const Item* item) {
    for (int i = 0; i < transition->position_count; i++) {
        if (transition->start_positions[i].item == item) {
            return i;
        }
    }
    return -1;
}

// Helper function to add a position entry
static void AddPositionEntry(Transition* transition, Item* item, Vector2 position) {
    // Check if we need to grow the array
    if (transition->position_count >= transition->position_capacity) {
        TransitionPosition* new_positions = (TransitionPosition*)GrowArray(
            transition->start_positions, 
            &transition->position_capacity, 
            sizeof(TransitionPosition)
        );
        
        if (!new_positions) {
            // Handle allocation failure
            return;
        }
        
        transition->start_positions = new_positions;
    }
    
    // Add the new position entry
    transition->start_positions[transition->position_count].item = item;
    transition->start_positions[transition->position_count].position = position;
    transition->position_count++;
}

// Helper function to build a list of available directions
static void BuildDirectionList(Direction* directions, int* count, bool left, bool right, bool up, bool down) {
    *count = 0;
    
    if (left) {
        directions[(*count)++] = DIRECTION_LEFT;
    }
    if (right) {
        directions[(*count)++] = DIRECTION_RIGHT;
    }
    if (up) {
        directions[(*count)++] = DIRECTION_UP;
    }
    if (down) {
        directions[(*count)++] = DIRECTION_DOWN;
    }
}

// Helper function to position an item based on a direction
static void PositionItemByDirection(Item* item, Direction direction) {
    switch (direction) {
        case DIRECTION_LEFT:
            item->x = -GetItemWidth(item);
            break;
        case DIRECTION_RIGHT:
            item->x = SCREEN_WIDTH;
            break;
        case DIRECTION_UP:
            item->y = -GetItemHeight(item);
            break;
        case DIRECTION_DOWN:
            item->y = SCREEN_HEIGHT;
            break;
    }
}

// Helper function to get the opposite direction
static Direction GetOppositeDirection(Direction direction) {
    switch (direction) {
        case DIRECTION_LEFT:
            return DIRECTION_RIGHT;
        case DIRECTION_RIGHT:
            return DIRECTION_LEFT;
        case DIRECTION_UP:
            return DIRECTION_DOWN;
        case DIRECTION_DOWN:
            return DIRECTION_UP;
        default:
            return direction; // Should never happen
    }
}

Transition InitTransition(void) {
    Transition transition;
    
    // Initialize speed
    transition.speed = TRANSITION_DEFAULT_SPEED;
    
    // Initialize items array
    transition.item_capacity = INITIAL_CAPACITY;
    transition.item_count = 0;
    transition.items = (Item**)malloc(transition.item_capacity * sizeof(Item*));
    
    // Initialize positions array
    transition.position_capacity = INITIAL_CAPACITY;
    transition.position_count = 0;
    transition.start_positions = (TransitionPosition*)malloc(transition.position_capacity * sizeof(TransitionPosition));
    
    return transition;
}

void UnloadTransition(Transition* transition) {
    // Free arrays
    if (transition->items) {
        free(transition->items);
        transition->items = NULL;
    }
    
    if (transition->start_positions) {
        free(transition->start_positions);
        transition->start_positions = NULL;
    }
    
    transition->item_count = 0;
    transition->position_count = 0;
}

void AddTransitionItems(Transition* transition, const Menu* menu) {
    for (int i = 0; i < menu->item_count; i++) {
        Item* item = menu->items[i];
        
        // Check if the item is already in our list
        bool already_added = false;
        for (int j = 0; j < transition->item_count; j++) {
            if (transition->items[j] == item) {
                already_added = true;
                break;
            }
        }
        
        if (!already_added) {
            // Check if we need to grow the array
            if (transition->item_count >= transition->item_capacity) {
                Item** new_items = (Item**)GrowArray(
                    transition->items, 
                    &transition->item_capacity, 
                    sizeof(Item*)
                );
                
                if (!new_items) {
                    // Handle allocation failure
                    return;
                }
                
                transition->items = new_items;
            }
            
            // Add the item
            transition->items[transition->item_count++] = item;
        }
    }
}

void RemoveAllTransitionItems(Transition* transition) {
    transition->item_count = 0;
}

void SetupTransition(Transition* transition, Menu* menu, bool left, bool right, bool up, bool down) {
    // Build the list of available directions
    Direction directions[4];
    int direction_count;
    BuildDirectionList(directions, &direction_count, left, right, up, down);
    
    if (direction_count == 0) {
        return; // No directions specified
    }
    
    // Add all items from the menu
    AddTransitionItems(transition, menu);
    
    // Make sure all items are in the right position
    CleanupMenu(menu);
    
    // For each item, store its current position and move it off-screen
    for (int i = 0; i < menu->item_count; i++) {
        Item* item = menu->items[i];
        
        // Store the current position if not already stored
        if (FindPositionIndex(transition, item) == -1) {
            Vector2 position = { item->x, item->y };
            AddPositionEntry(transition, item, position);
        }
        
        // Choose a random direction and position the item
        Direction direction = directions[rand() % direction_count];
        PositionItemByDirection(item, direction);
    }
}

void SetupOddEvenTransition(Transition* transition, Menu* menu, bool left, bool right, bool up, bool down) {
    // Build the list of available directions
    Direction directions[4];
    int direction_count;
    BuildDirectionList(directions, &direction_count, left, right, up, down);
    
    if (direction_count == 0) {
        return; // No directions specified
    }
    
    // Add all items from the menu
    AddTransitionItems(transition, menu);
    
    // Make sure all items are in the right position
    CleanupMenu(menu);
    
    // Choose a random starting direction
    Direction direction = directions[rand() % direction_count];
    bool odd = (rand() % 2) == 0;
    
    // For each item, store its current position and move it off-screen
    for (int i = 0; i < menu->item_count; i++) {
        Item* item = menu->items[i];
        
        // Store the current position if not already stored
        if (FindPositionIndex(transition, item) == -1) {
            Vector2 position = { item->x, item->y };
            AddPositionEntry(transition, item, position);
        }
        
        // Position the item based on whether it's odd or even
        if (odd) {
            PositionItemByDirection(item, direction);
        } else {
            PositionItemByDirection(item, GetOppositeDirection(direction));
        }
        
        // Toggle odd/even for the next item
        odd = !odd;
    }
}

void SetupSingleItemTransition(Transition* transition, Item* item, bool left, bool right, bool up, bool down) {
    // Build the list of available directions
    Direction directions[4];
    int direction_count;
    BuildDirectionList(directions, &direction_count, left, right, up, down);
    
    if (direction_count == 0) {
        return; // No directions specified
    }
    
    // Check if the item is already in our list
    bool already_added = false;
    for (int i = 0; i < transition->item_count; i++) {
        if (transition->items[i] == item) {
            already_added = true;
            break;
        }
    }
    
    if (!already_added) {
        // Check if we need to grow the array
        if (transition->item_count >= transition->item_capacity) {
            Item** new_items = (Item**)GrowArray(
                transition->items, 
                &transition->item_capacity, 
                sizeof(Item*)
            );
            
            if (!new_items) {
                // Handle allocation failure
                return;
            }
            
            transition->items = new_items;
        }
        
        // Add the item
        transition->items[transition->item_count++] = item;
    }
    
    // Store the current position if not already stored
    if (FindPositionIndex(transition, item) == -1) {
        Vector2 position = { item->x, item->y };
        AddPositionEntry(transition, item, position);
    }
    
    // Choose a random direction and position the item
    Direction direction = directions[rand() % direction_count];
    PositionItemByDirection(item, direction);
}

void UpdateTransition(Transition* transition, float delta_time) {
    // Move each item towards its target position
    for (int i = 0; i < transition->item_count; i++) {
        Item* item = transition->items[i];
        
        // Find the target position for this item
        int position_index = FindPositionIndex(transition, item);
        if (position_index == -1) {
            continue; // No target position found
        }
        
        Vector2 target = transition->start_positions[position_index].position;
        
        // Move the item towards its target position
        if (target.x < item->x) {
            if ((item->x - transition->speed * delta_time) < target.x) {
                item->x = target.x;
            } else {
                item->x -= transition->speed * delta_time;
            }
        } else if (target.x > item->x) {
            if ((item->x + transition->speed * delta_time) > target.x) {
                item->x = target.x;
            } else {
                item->x += transition->speed * delta_time;
            }
        }
        
        if (target.y < item->y) {
            if ((item->y - transition->speed * delta_time) < target.y) {
                item->y = target.y;
            } else {
                item->y -= transition->speed * delta_time;
            }
        } else if (target.y > item->y) {
            if ((item->y + transition->speed * delta_time) > target.y) {
                item->y = target.y;
            } else {
                item->y += transition->speed * delta_time;
            }
        }
    }
} 