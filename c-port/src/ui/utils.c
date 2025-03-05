#include "ui/utils.h"
#include "raylib.h"
#include "ui/item.h"

// Check if two colors are equal
bool ColorEquals(Color a, Color b) {
    return a.r == b.r && a.g == b.g && a.b == b.b && a.a == b.a;
}

// Check if the mouse is over an item
bool IsMouseOverItem(const Item* item, Vector2 mouse_pos) {
    if (item == NULL) return false;
    
    // Create a rectangle representing the item's bounds
    Rectangle bounds = {
        item->x - item->width / 2,
        item->y - item->height / 2,
        item->width,
        item->height
    };
    
    // Check if the mouse position is within the bounds
    return CheckCollisionPointRec(mouse_pos, bounds);
} 