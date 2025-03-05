#ifndef UI_UTILS_H
#define UI_UTILS_H

#include "raylib.h"
#include <stdbool.h>

// Forward declarations
typedef struct Item Item;

// Check if two colors are equal
bool ColorEquals(Color a, Color b);

// Check if the mouse is over an item
bool IsMouseOverItem(const Item* item, Vector2 mouse_pos);

#endif // UI_UTILS_H 