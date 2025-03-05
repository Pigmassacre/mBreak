/**
 * @file colorwheelmenu.h
 * @brief Header file for the ColorWheelMenu UI component.
 * 
 * This is a subclass of Menu that positions its items in a color wheel fashion.
 * It allows users to select colors from a continuous color wheel rather than from a limited set of predefined colors.
 */

#ifndef COLORWHEELMENU_H
#define COLORWHEELMENU_H

#include "raylib.h"
#include "ui/menu.h"
#include "ui/item.h"

/**
 * @brief Structure representing a color wheel menu.
 * 
 * The ColorWheelMenu is a specialized menu that displays a color wheel
 * and allows the user to select colors from it.
 */
typedef struct ColorWheelMenu {
    Menu base;                  /**< Base menu structure */
    float radius;               /**< Radius of the color wheel */
    float center_x;             /**< X-coordinate of the center of the wheel */
    float center_y;             /**< Y-coordinate of the center of the wheel */
    Texture2D wheel_texture;    /**< Texture containing the color wheel */
    Color selected_color;       /**< Currently selected color */
    Vector2 selected_pos;       /**< Position of the selected color on the wheel */
    Vector2 hover_pos;          /**< Current hover position on the wheel */
    Item color_display;         /**< Item used to display the selected color */
    bool auto_position_color_display; /**< Whether to automatically position the color display */
    bool has_selection;         /**< Whether a color has been selected */
    bool has_hover;             /**< Whether the mouse is hovering over the wheel */
} ColorWheelMenu;

/**
 * @brief Initialize a color wheel menu.
 * 
 * @param radius Radius of the color wheel
 * @param center_x X-coordinate of the center of the wheel
 * @param center_y Y-coordinate of the center of the wheel
 * @return ColorWheelMenu The initialized color wheel menu
 */
ColorWheelMenu InitColorWheelMenu(float radius, float center_x, float center_y);

/**
 * @brief Unload a color wheel menu and free its resources.
 * 
 * @param colorwheel Pointer to the color wheel menu to unload
 */
void UnloadColorWheelMenu(ColorWheelMenu* colorwheel);

/**
 * @brief Generate the color wheel texture.
 * 
 * @param colorwheel Pointer to the color wheel menu
 */
void GenerateColorWheel(ColorWheelMenu* colorwheel);

/**
 * @brief Convert HSV color values to RGB.
 * 
 * @param h Hue value (0.0 to 1.0)
 * @param s Saturation value (0.0 to 1.0)
 * @param v Value/brightness (0.0 to 1.0)
 * @return Color The resulting RGB color
 */
Color HsvToRgb(float h, float s, float v);

/**
 * @brief Get the color at a specific position on the wheel.
 * 
 * @param colorwheel Pointer to the color wheel menu
 * @param pos Position to check
 * @param color Pointer to store the resulting color
 * @return bool True if the position is on the wheel and a color was found, false otherwise
 */
bool GetColorAtPosition(const ColorWheelMenu* colorwheel, Vector2 pos, Color* color);

/**
 * @brief Select a color at the given position.
 * 
 * @param colorwheel Pointer to the color wheel menu
 * @param pos Position to select color from
 * @return bool True if a color was selected, false otherwise
 */
bool SelectColor(ColorWheelMenu* colorwheel, Vector2 pos);

/**
 * @brief Get the width of the color wheel.
 * 
 * @param colorwheel Pointer to the color wheel menu
 * @return float The width of the color wheel
 */
float GetColorWheelWidth(const ColorWheelMenu* colorwheel);

/**
 * @brief Get the height of the color wheel.
 * 
 * @param colorwheel Pointer to the color wheel menu
 * @return float The height of the color wheel
 */
float GetColorWheelHeight(const ColorWheelMenu* colorwheel);

/**
 * @brief Set a custom position for the color display.
 * 
 * @param colorwheel Pointer to the color wheel menu
 * @param x X-coordinate for the color display
 * @param y Y-coordinate for the color display
 */
void SetColorDisplayPosition(ColorWheelMenu* colorwheel, float x, float y);

/**
 * @brief Update the color wheel menu.
 * 
 * @param colorwheel Pointer to the color wheel menu
 */
void UpdateColorWheelMenu(ColorWheelMenu* colorwheel);

/**
 * @brief Draw the color wheel menu.
 * 
 * @param colorwheel Pointer to the color wheel menu
 */
void DrawColorWheelMenu(const ColorWheelMenu* colorwheel);

/**
 * @brief Clear the selected color.
 * 
 * @param colorwheel Pointer to the color wheel menu
 */
void ClearColorSelection(ColorWheelMenu* colorwheel);

#endif // COLORWHEELMENU_H 