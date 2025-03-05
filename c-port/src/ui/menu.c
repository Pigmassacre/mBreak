/**
 * @file menu.c
 * @brief Implementation of the menu component.
 */

#include "ui/menu.h"
#include "ui/item.h"
#include <stdlib.h>
#include <string.h>
#include <float.h>
#include <stdio.h>

// Initial capacity for item and other menu arrays
#define INITIAL_CAPACITY 8

// Default sound effect path
#define DEFAULT_SOUND_EFFECT_PATH "resources/sounds/select.wav"

// Helper function to grow an array
static void* GrowArray(void* array, size_t* capacity, size_t element_size) {
    size_t new_capacity = *capacity * 2;
    void* new_array = realloc(array, new_capacity * element_size);
    
    if (new_array) {
        *capacity = new_capacity;
    }
    
    return new_array;
}

Menu InitMenu(float x, float y, int position) {
    Menu menu;
    
    // Initialize menu items array
    menu.item_capacity = INITIAL_CAPACITY;
    menu.item_count = 0;
    menu.items = (Item**)malloc(menu.item_capacity * sizeof(Item*));
    
    // Initialize other menus array
    menu.other_menu_capacity = INITIAL_CAPACITY;
    menu.other_menu_count = 0;
    menu.other_menus = (struct Menu**)malloc(menu.other_menu_capacity * sizeof(struct Menu*));
    
    // Initialize functions array
    menu.functions = (MenuItemFunction*)malloc(menu.item_capacity * sizeof(MenuItemFunction));
    menu.function_data = (void**)malloc(menu.item_capacity * sizeof(void*));
    
    // Initialize position and tracking
    menu.previous_selected_item = NULL;
    menu.position = position;
    menu.x = x;
    menu.y = y;
    
    // Initialize sound
    menu.sound_loaded = false;
    
    return menu;
}

void UnloadMenu(Menu* menu) {
    if (!menu) {
        return;
    }
    
    // Free arrays
    if (menu->items) {
        free(menu->items);
        menu->items = NULL;
    }
    
    if (menu->other_menus) {
        free(menu->other_menus);
        menu->other_menus = NULL;
    }
    
    if (menu->functions) {
        free(menu->functions);
        menu->functions = NULL;
    }
    
    if (menu->function_data) {
        free(menu->function_data);
        menu->function_data = NULL;
    }
    
    // Unload sound if loaded
    if (menu->sound_loaded) {
        UnloadSound(menu->sound_effect);
        menu->sound_loaded = false;
    }
}

float GetMenuWidth(const Menu* menu) {
    // Returns the distance between the lowest x-value and the highest x-value out of all items
    float min_x = FLT_MAX;
    float max_x = 0;
    
    for (int i = 0; i < menu->item_count; i++) {
        Item* item = menu->items[i];
        if (item->x < min_x) {
            min_x = item->x;
        }
        if (item->x + GetItemWidth(item) > max_x) {
            max_x = item->x + GetItemWidth(item);
        }
    }
    
    // If no items, return 0
    if (min_x == FLT_MAX) {
        return 0;
    }
    
    return max_x - min_x;
}

float GetMenuHeight(const Menu* menu) {
    // Returns the distance between the lowest y-value and the highest y-value out of all items
    float min_y = FLT_MAX;
    float max_y = 0;
    
    for (int i = 0; i < menu->item_count; i++) {
        Item* item = menu->items[i];
        if (item->y < min_y) {
            min_y = item->y;
        }
        if (item->y + GetItemHeight(item) > max_y) {
            max_y = item->y + GetItemHeight(item);
        }
    }
    
    // If no items, return 0
    if (min_y == FLT_MAX) {
        return 0;
    }
    
    return max_y - min_y;
}

void AddMenuItem(Menu* menu, Item* item, MenuItemFunction function, void* data) {
    // Grow arrays if needed
    if (menu->item_count >= menu->item_capacity) {
        Item** new_items = (Item**)GrowArray(menu->items, &menu->item_capacity, sizeof(Item*));
        MenuItemFunction* new_functions = (MenuItemFunction*)GrowArray(menu->functions, &menu->item_capacity, sizeof(MenuItemFunction));
        void** new_function_data = (void**)GrowArray(menu->function_data, &menu->item_capacity, sizeof(void*));
        
        if (!new_items || !new_functions || !new_function_data) {
            // Handle allocation failure
            if (new_items) menu->items = new_items;
            if (new_functions) menu->functions = new_functions;
            if (new_function_data) menu->function_data = new_function_data;
            return;
        }
        
        menu->items = new_items;
        menu->functions = new_functions;
        menu->function_data = new_function_data;
    }
    
    // Add the item
    menu->items[menu->item_count] = item;
    menu->functions[menu->item_count] = function;
    menu->function_data[menu->item_count] = data;
    menu->item_count++;
    
    // Position the item
    PositionMenuItem(menu, item);
}

void PositionMenuItem(Menu* menu, Item* item) {
    // Base implementation does nothing - derived classes will override
    // to position items according to their layout
    (void)menu;
    (void)item;
}

void RemoveMenuItem(Menu* menu, Item* item) {
    int index = -1;
    
    // Find the item
    for (int i = 0; i < menu->item_count; i++) {
        if (menu->items[i] == item) {
            index = i;
            break;
        }
    }
    
    if (index == -1) {
        // Item not found
        return;
    }
    
    // Remove the item by shifting all items after it
    for (int i = index; i < menu->item_count - 1; i++) {
        menu->items[i] = menu->items[i + 1];
        menu->functions[i] = menu->functions[i + 1];
        menu->function_data[i] = menu->function_data[i + 1];
    }
    
    menu->item_count--;
}

void CleanupMenu(Menu* menu) {
    // Reposition all items
    for (int i = 0; i < menu->item_count; i++) {
        PositionMenuItem(menu, menu->items[i]);
    }
}

void RegisterOtherMenus(Menu* menu, Menu** other_menus, int count) {
    // Register other menus to coordinate with
    for (int i = 0; i < count; i++) {
        // Skip if the menu is ourselves
        if (other_menus[i] == menu) {
            continue;
        }
        
        // Check if already registered
        bool already_registered = false;
        for (int j = 0; j < menu->other_menu_count; j++) {
            if (menu->other_menus[j] == other_menus[i]) {
                already_registered = true;
                break;
            }
        }
        
        if (!already_registered) {
            // Grow array if needed
            if (menu->other_menu_count >= menu->other_menu_capacity) {
                struct Menu** new_other_menus = (struct Menu**)GrowArray(
                    menu->other_menus, 
                    &menu->other_menu_capacity, 
                    sizeof(struct Menu*)
                );
                
                if (!new_other_menus) {
                    // Handle allocation failure
                    return;
                }
                
                menu->other_menus = new_other_menus;
            }
            
            // Add the menu
            menu->other_menus[menu->other_menu_count] = other_menus[i];
            menu->other_menu_count++;
        }
    }
}

bool IsMouseOverMenuItem(const Menu* menu, const Item* item, Vector2 mouse_pos) {
    // Check if mouse position is inside the item
    return  mouse_pos.x >= item->x && 
            mouse_pos.x <= item->x + GetItemWidth(item) && 
            mouse_pos.y >= item->y && 
            mouse_pos.y <= item->y + GetItemHeight(item);
}

void UpdateMenu(Menu* menu, float delta_time) {
    // Track selected items
    Item* selected_items[menu->item_count];
    int selected_count = 0;
    
    // Update all items in the menu
    for (int i = 0; i < menu->item_count; i++) {
        Item* item = menu->items[i];
        
        // Update the item
        UpdateItem(item, delta_time);
        
        // Track selected items
        if (item->selected) {
            selected_items[selected_count++] = item;
            
            // Play sound if newly selected
            if (item != menu->previous_selected_item && menu->sound_loaded) {
                PlaySound(menu->sound_effect);
                menu->previous_selected_item = item;
            }
        }
    }
    
    // If no items are selected, reset previous selected item
    if (selected_count == 0) {
        menu->previous_selected_item = NULL;
    }
}

void DrawMenu(const Menu* menu) {
    // Draw all items in the menu
    for (int i = 0; i < menu->item_count; i++) {
        DrawItem(menu->items[i]);
    }
}

void SetMenuSoundEffect(Menu* menu, const char* sound_path) {
    // Unload existing sound if loaded
    if (menu->sound_loaded) {
        UnloadSound(menu->sound_effect);
        menu->sound_loaded = false;
    }
    
    // Load new sound effect
    const char* path = sound_path ? sound_path : DEFAULT_SOUND_EFFECT_PATH;
    menu->sound_effect = LoadSound(path);
    menu->sound_loaded = true;
} 