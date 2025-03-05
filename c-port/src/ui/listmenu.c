/**
 * @file listmenu.c
 * @brief Implementation of the ListMenu UI component.
 */

#include "ui/listmenu.h"
#include "ui/item.h"

ListMenu InitListMenu(float x, float y, int position) {
    ListMenu menu;
    
    // Initialize base menu
    menu.base = InitMenu(x, y, position);
    
    return menu;
}

void UnloadListMenu(ListMenu* menu) {
    // Unload base menu
    UnloadMenu(&menu->base);
}

void PositionListMenuItem(ListMenu* menu, Item* item) {
    // Find the index of the item in the menu
    int index = -1;
    for (int i = 0; i < menu->base.item_count; i++) {
        if (menu->base.items[i] == item) {
            index = i;
            break;
        }
    }
    
    if (index == -1) {
        // Item not found in menu
        return;
    }
    
    // Position the item in a top-to-bottom fashion
    item->x = menu->base.x - (GetItemWidth(item) / 2.0f);
    item->y = menu->base.y + ((GetItemHeight(item) * 2.0f) * index);
}

void AddListMenuItem(ListMenu* menu, Item* item, MenuItemFunction function, void* data) {
    // Add the item to the base menu
    AddMenuItem(&menu->base, item, function, data);
    
    // Position the item according to list menu layout
    PositionListMenuItem(menu, item);
}

void UpdateListMenu(ListMenu* menu, float delta_time) {
    // Update the base menu
    UpdateMenu(&menu->base, delta_time);
}

void DrawListMenu(const ListMenu* menu) {
    // Draw the base menu
    DrawMenu(&menu->base);
} 