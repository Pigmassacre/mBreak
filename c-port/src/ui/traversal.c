/**
 * @file traversal.c
 * @brief Implementation of the Traversal UI component.
 */

#include "ui/traversal.h"
#include "ui/item.h"
#include <stdlib.h>
#include <math.h>
#include <float.h>

void TraverseMenus(int key, Vector2 mouse_position, bool mouse_clicked, Menu* menus[], int menu_count) {
    // If the given list is empty, we do nothing.
    if (menu_count == 0) {
        return;
    }
    
    // Check for mouse movement
    if (IsMouseButtonReleased(MOUSE_BUTTON_LEFT) == false && mouse_position.x != 0 && mouse_position.y != 0) {
        // If the mouse has been moved, we check every item in every menu.
        for (int i = 0; i < menu_count; i++) {
            Menu* a_menu = menus[i];
            for (int j = 0; j < a_menu->item_count; j++) {
                Item* item = a_menu->items[j];
                // If the mouse is positioned over an item, unselect all items and then select that item.
                if (IsMouseOverItem(item, mouse_position)) {
                    // Unselect all items in all menus
                    for (int k = 0; k < menu_count; k++) {
                        Menu* menu_to_unselect = menus[k];
                        for (int l = 0; l < menu_to_unselect->item_count; l++) {
                            menu_to_unselect->items[l]->selected = false;
                        }
                    }
                    
                    // Select this item
                    item->selected = true;
                }
            }
        }
    } 
    // Check for key press or mouse click
    else if (key == KEY_ENTER || mouse_clicked) {
        // Check through all menus
        for (int i = 0; i < menu_count; i++) {
            Menu* a_menu = menus[i];
            for (int j = 0; j < a_menu->item_count; j++) {
                Item* item = a_menu->items[j];
                
                if (mouse_clicked) {
                    // If the mouse button was clicked, we check if the mouse is positioned over the item, and if the item was selected.
                    if (IsMouseOverItem(item, mouse_position) && item->selected) {
                        // Call the item's function
                        if (a_menu->functions[j] != NULL) {
                            a_menu->functions[j](item);
                        }
                    }
                } else {
                    // Otherwise, if the item is selected we just call its function.
                    if (item->selected) {
                        // Call the item's function
                        if (a_menu->functions[j] != NULL) {
                            a_menu->functions[j](item);
                        }
                    }
                }
            }
        }
    } 
    // Check for arrow key presses
    else if (key == KEY_LEFT) {
        // We try to traverse the menu to the left.
        SelectLeftOrRight(menus, menu_count, true);
    } 
    else if (key == KEY_RIGHT) {
        // To the right...
        SelectLeftOrRight(menus, menu_count, false);
    } 
    else if (key == KEY_UP) {
        // Up...
        SelectUpOrDown(menus, menu_count, true);
    } 
    else if (key == KEY_DOWN) {
        // Or down.
        SelectUpOrDown(menus, menu_count, false);
    }
}

void SelectLeftOrRight(Menu* menus[], int menu_count, bool left) {
    // First, we want to get the selected item
    Item* selected_item = GetSelectedItem(menus, menu_count);
    if (selected_item == NULL) {
        return; // No selected item found
    }
    
    // Fill up a list of possible items to traverse to
    // We'll allocate enough space for all items in all menus
    int total_items = 0;
    for (int i = 0; i < menu_count; i++) {
        total_items += menus[i]->item_count;
    }
    
    Item** list_of_possible = (Item**)malloc(total_items * sizeof(Item*));
    if (list_of_possible == NULL) {
        return; // Memory allocation failed
    }
    
    int possible_count = FillListOfPossible(menus, menu_count, list_of_possible);
    
    // Create a filtered list based on direction
    Item** filtered_list = (Item**)malloc(possible_count * sizeof(Item*));
    if (filtered_list == NULL) {
        free(list_of_possible);
        return; // Memory allocation failed
    }
    
    int filtered_count = 0;
    
    // Depending on if we're going left or right, we filter in different ways.
    if (left) {
        // If we're going left, we only want the items that have an x-value SMALLER than our selected items x-value.
        for (int i = 0; i < possible_count; i++) {
            Item* item = list_of_possible[i];
            if ((item->x + (GetItemWidth(item) / 2.0f)) < (selected_item->x + (GetItemWidth(selected_item) / 2.0f))) {
                filtered_list[filtered_count++] = item;
            }
        }
    } else {
        // If we're going right, we only want the items that have an x-value LARGER than our selected items x-value.
        for (int i = 0; i < possible_count; i++) {
            Item* item = list_of_possible[i];
            if ((item->x + (GetItemWidth(item) / 2.0f)) > (selected_item->x + (GetItemWidth(selected_item) / 2.0f))) {
                filtered_list[filtered_count++] = item;
            }
        }
    }
    
    // Find out if any of the possible items are in the same menu as the selected item
    Menu* selected_menu = NULL;
    for (int i = 0; i < menu_count; i++) {
        for (int j = 0; j < menus[i]->item_count; j++) {
            if (menus[i]->items[j] == selected_item) {
                selected_menu = menus[i];
                break;
            }
        }
        if (selected_menu != NULL) {
            break;
        }
    }
    
    Item** same_menu_items = (Item**)malloc(filtered_count * sizeof(Item*));
    if (same_menu_items == NULL) {
        free(list_of_possible);
        free(filtered_list);
        return; // Memory allocation failed
    }
    
    int same_menu_count = 0;
    
    if (selected_menu != NULL) {
        for (int i = 0; i < filtered_count; i++) {
            for (int j = 0; j < selected_menu->item_count; j++) {
                if (filtered_list[i] == selected_menu->items[j]) {
                    same_menu_items[same_menu_count++] = filtered_list[i];
                    break;
                }
            }
        }
    }
    
    if (filtered_count > 0) {
        // If there are any items left, we want to retain the item which has the least y-difference AND least x-difference.
        if (same_menu_count == 0) {
            // However, we only care about the y-difference if we're traveling from one menu to another.
            float least_y_difference = FLT_MAX;
            for (int i = 0; i < filtered_count; i++) {
                Item* an_item = filtered_list[i];
                // Find the least y difference.
                float this_difference = fabsf((an_item->y + (GetItemHeight(an_item) / 2.0f)) - 
                                            (selected_item->y + (GetItemHeight(selected_item) / 2.0f)));
                if (this_difference < least_y_difference) {
                    least_y_difference = this_difference;
                }
            }
            
            // We want to retain the items which have a y-difference equal to the least y-difference.
            Item** y_filtered_list = (Item**)malloc(filtered_count * sizeof(Item*));
            if (y_filtered_list == NULL) {
                free(list_of_possible);
                free(filtered_list);
                free(same_menu_items);
                return; // Memory allocation failed
            }
            
            int y_filtered_count = 0;
            
            for (int i = 0; i < filtered_count; i++) {
                Item* an_item = filtered_list[i];
                float this_difference = fabsf((an_item->y + (GetItemHeight(an_item) / 2.0f)) - 
                                            (selected_item->y + (GetItemHeight(selected_item) / 2.0f)));
                if (fabsf(this_difference - least_y_difference) < 0.001f) { // Floating point comparison with epsilon
                    y_filtered_list[y_filtered_count++] = an_item;
                }
            }
            
            // Update our filtered list
            free(filtered_list);
            filtered_list = y_filtered_list;
            filtered_count = y_filtered_count;
        } else {
            // If we're traveling within the same menu, we only care about those menu items and the x-positions.
            free(filtered_list);
            filtered_list = same_menu_items;
            filtered_count = same_menu_count;
            
            // We don't need the same_menu_items array anymore, but we'll free it later
        }
        
        // From these remaining items, we want to pick the item which has the least x difference.
        float least_x_difference = FLT_MAX;
        for (int i = 0; i < filtered_count; i++) {
            Item* an_item = filtered_list[i];
            // Find the least x difference.
            float this_difference = fabsf(an_item->x - selected_item->x);
            if (this_difference < least_x_difference) {
                least_x_difference = this_difference;
            }
        }
        
        Item** x_filtered_list = (Item**)malloc(filtered_count * sizeof(Item*));
        if (x_filtered_list == NULL) {
            free(list_of_possible);
            free(filtered_list);
            free(same_menu_items);
            return; // Memory allocation failed
        }
        
        int x_filtered_count = 0;
        
        for (int i = 0; i < filtered_count; i++) {
            Item* an_item = filtered_list[i];
            float this_difference = fabsf(an_item->x - selected_item->x);
            if (fabsf(this_difference - least_x_difference) < 0.001f) { // Floating point comparison with epsilon
                x_filtered_list[x_filtered_count++] = an_item;
            }
        }
        
        // Finally, we unselect the selected item, and then select the first item in the FINAL list of possible items.
        if (x_filtered_count > 0) {
            selected_item->selected = false;
            x_filtered_list[0]->selected = true;
        }
        
        // Free all allocated memory
        free(x_filtered_list);
    }
    
    // Free all allocated memory
    free(list_of_possible);
    free(filtered_list);
    free(same_menu_items);
}

void SelectUpOrDown(Menu* menus[], int menu_count, bool up) {
    // First, we want to get the selected item
    Item* selected_item = GetSelectedItem(menus, menu_count);
    if (selected_item == NULL) {
        return; // No selected item found
    }
    
    // Fill up a list of possible items to traverse to
    // We'll allocate enough space for all items in all menus
    int total_items = 0;
    for (int i = 0; i < menu_count; i++) {
        total_items += menus[i]->item_count;
    }
    
    Item** list_of_possible = (Item**)malloc(total_items * sizeof(Item*));
    if (list_of_possible == NULL) {
        return; // Memory allocation failed
    }
    
    int possible_count = FillListOfPossible(menus, menu_count, list_of_possible);
    
    // Create a filtered list based on direction
    Item** filtered_list = (Item**)malloc(possible_count * sizeof(Item*));
    if (filtered_list == NULL) {
        free(list_of_possible);
        return; // Memory allocation failed
    }
    
    int filtered_count = 0;
    
    // Depending on if we're going up or down, we filter in different ways.
    if (up) {
        // If we're going up, we only want the items that have a y-value SMALLER than our selected items y-value.
        for (int i = 0; i < possible_count; i++) {
            Item* item = list_of_possible[i];
            if ((item->y + (GetItemHeight(item) / 2.0f)) < (selected_item->y + (GetItemHeight(selected_item) / 2.0f))) {
                filtered_list[filtered_count++] = item;
            }
        }
    } else {
        // If we're going down, we only want the items that have a y-value LARGER than our selected items y-value.
        for (int i = 0; i < possible_count; i++) {
            Item* item = list_of_possible[i];
            if ((item->y + (GetItemHeight(item) / 2.0f)) > (selected_item->y + (GetItemHeight(selected_item) / 2.0f))) {
                filtered_list[filtered_count++] = item;
            }
        }
    }
    
    // Find out if any of the possible items are in the same menu as the selected item
    Menu* selected_menu = NULL;
    for (int i = 0; i < menu_count; i++) {
        for (int j = 0; j < menus[i]->item_count; j++) {
            if (menus[i]->items[j] == selected_item) {
                selected_menu = menus[i];
                break;
            }
        }
        if (selected_menu != NULL) {
            break;
        }
    }
    
    Item** same_menu_items = (Item**)malloc(filtered_count * sizeof(Item*));
    if (same_menu_items == NULL) {
        free(list_of_possible);
        free(filtered_list);
        return; // Memory allocation failed
    }
    
    int same_menu_count = 0;
    
    if (selected_menu != NULL) {
        for (int i = 0; i < filtered_count; i++) {
            for (int j = 0; j < selected_menu->item_count; j++) {
                if (filtered_list[i] == selected_menu->items[j]) {
                    same_menu_items[same_menu_count++] = filtered_list[i];
                    break;
                }
            }
        }
    }
    
    if (filtered_count > 0) {
        // If there are any items left, we want to retain the item which has the least x-difference AND least y-difference.
        if (same_menu_count == 0) {
            // However, we only care about the x-difference if we're traveling from one menu to another.
            float least_x_difference = FLT_MAX;
            for (int i = 0; i < filtered_count; i++) {
                Item* an_item = filtered_list[i];
                // Find the least x difference.
                float this_difference = fabsf((an_item->x + (GetItemWidth(an_item) / 2.0f)) - 
                                            (selected_item->x + (GetItemWidth(selected_item) / 2.0f)));
                if (this_difference < least_x_difference) {
                    least_x_difference = this_difference;
                }
            }
            
            // We want to retain the items which have an x-difference equal to the least x-difference.
            Item** x_filtered_list = (Item**)malloc(filtered_count * sizeof(Item*));
            if (x_filtered_list == NULL) {
                free(list_of_possible);
                free(filtered_list);
                free(same_menu_items);
                return; // Memory allocation failed
            }
            
            int x_filtered_count = 0;
            
            for (int i = 0; i < filtered_count; i++) {
                Item* an_item = filtered_list[i];
                float this_difference = fabsf((an_item->x + (GetItemWidth(an_item) / 2.0f)) - 
                                            (selected_item->x + (GetItemWidth(selected_item) / 2.0f)));
                if (fabsf(this_difference - least_x_difference) < 0.001f) { // Floating point comparison with epsilon
                    x_filtered_list[x_filtered_count++] = an_item;
                }
            }
            
            // Update our filtered list
            free(filtered_list);
            filtered_list = x_filtered_list;
            filtered_count = x_filtered_count;
        } else {
            // If we're traveling within the same menu, we only care about those menu items and the y-positions.
            free(filtered_list);
            filtered_list = same_menu_items;
            filtered_count = same_menu_count;
            
            // We don't need the same_menu_items array anymore, but we'll free it later
        }
        
        // From these remaining items, we want to pick the item which has the least y difference.
        float least_y_difference = FLT_MAX;
        for (int i = 0; i < filtered_count; i++) {
            Item* an_item = filtered_list[i];
            // Find the least y difference.
            float this_difference = fabsf(an_item->y - selected_item->y);
            if (this_difference < least_y_difference) {
                least_y_difference = this_difference;
            }
        }
        
        Item** y_filtered_list = (Item**)malloc(filtered_count * sizeof(Item*));
        if (y_filtered_list == NULL) {
            free(list_of_possible);
            free(filtered_list);
            free(same_menu_items);
            return; // Memory allocation failed
        }
        
        int y_filtered_count = 0;
        
        for (int i = 0; i < filtered_count; i++) {
            Item* an_item = filtered_list[i];
            float this_difference = fabsf(an_item->y - selected_item->y);
            if (fabsf(this_difference - least_y_difference) < 0.001f) { // Floating point comparison with epsilon
                y_filtered_list[y_filtered_count++] = an_item;
            }
        }
        
        // Finally, we unselect the selected item, and then select the first item in the FINAL list of possible items.
        if (y_filtered_count > 0) {
            selected_item->selected = false;
            y_filtered_list[0]->selected = true;
        }
        
        // Free all allocated memory
        free(y_filtered_list);
    }
    
    // Free all allocated memory
    free(list_of_possible);
    free(filtered_list);
    free(same_menu_items);
}

Item* GetSelectedItem(Menu* menus[], int menu_count) {
    for (int i = 0; i < menu_count; i++) {
        Menu* a_menu = menus[i];
        for (int j = 0; j < a_menu->item_count; j++) {
            Item* item = a_menu->items[j];
            if (item->selected) {
                return item;
            }
        }
    }
    
    return NULL; // No selected item found
}

int FillListOfPossible(Menu* menus[], int menu_count, Item* items[]) {
    int count = 0;
    
    for (int i = 0; i < menu_count; i++) {
        Menu* a_menu = menus[i];
        for (int j = 0; j < a_menu->item_count; j++) {
            items[count++] = a_menu->items[j];
        }
    }
    
    return count;
} 