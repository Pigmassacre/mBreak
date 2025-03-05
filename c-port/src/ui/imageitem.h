/**
 * @file imageitem.h
 * @brief Image item component for UI.
 */

#ifndef IMAGEITEM_H
#define IMAGEITEM_H

#include "raylib.h"
#include "ui/item.h"

/**
 * @brief ImageItem structure for displaying images in UI.
 * 
 * This is a wrapper around Raylib's texture rendering. It can be used in menus
 * or simply to display images. It can function as a button in a menu.
 */
typedef struct ImageItem {
    // Base item properties
    Item base;
    
    // Image properties
    Texture2D texture;
    bool texture_loaded;
    
    // Rect to extract from the texture (for sprite sheets)
    Rectangle source_rect;
    
    // Alpha value for transparency
    int alpha_value;
    
    // Scaling
    float scale_x;
    float scale_y;
} ImageItem;

/**
 * @brief Initialize an ImageItem with the given image and properties.
 * 
 * @param image_path Path to the image file.
 * @param color The tint color for the image.
 * @param alpha_value The alpha transparency (0-255).
 * @return An initialized ImageItem.
 */
ImageItem InitImageItem(const char* image_path, Color color, int alpha_value);

/**
 * @brief Initialize an ImageItem from an already loaded texture.
 * 
 * @param texture The texture to use.
 * @param color The tint color for the image.
 * @param alpha_value The alpha transparency (0-255).
 * @return An initialized ImageItem.
 */
ImageItem InitImageItemFromTexture(Texture2D texture, Color color, int alpha_value);

/**
 * @brief Clean up resources used by an ImageItem.
 * 
 * @param item Pointer to the ImageItem to clean up.
 */
void UnloadImageItem(ImageItem* item);

/**
 * @brief Set the source rectangle to extract from the texture.
 * 
 * This allows using sprite sheets or extracting parts of an image.
 * 
 * @param item Pointer to the ImageItem.
 * @param source The rectangle defining the part of the texture to use.
 */
void SetImageItemSourceRect(ImageItem* item, Rectangle source);

/**
 * @brief Set the scale of the image.
 * 
 * @param item Pointer to the ImageItem.
 * @param scale_x The horizontal scale factor.
 * @param scale_y The vertical scale factor.
 */
void SetImageItemScale(ImageItem* item, float scale_x, float scale_y);

/**
 * @brief Get the width of the image.
 * 
 * @param item Pointer to the ImageItem.
 * @return The width of the image after scaling.
 */
float GetImageItemWidth(const ImageItem* item);

/**
 * @brief Get the height of the image.
 * 
 * @param item Pointer to the ImageItem.
 * @return The height of the image after scaling.
 */
float GetImageItemHeight(const ImageItem* item);

/**
 * @brief Update the ImageItem's state.
 * 
 * @param item Pointer to the ImageItem to update.
 * @param delta_time The time passed since the last frame in seconds.
 */
void UpdateImageItem(ImageItem* item, float delta_time);

/**
 * @brief Draw the ImageItem to the screen.
 * 
 * @param item Pointer to the ImageItem to draw.
 */
void DrawImageItem(const ImageItem* item);

#endif // IMAGEITEM_H 