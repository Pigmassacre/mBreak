/**
 * @file imageitem.c
 * @brief Implementation of the ImageItem UI component.
 */

#include "ui/imageitem.h"

ImageItem InitImageItem(const char* image_path, Color color, int alpha_value) {
    ImageItem item;
    
    // Initialize base item
    item.base = InitItem(color);
    
    // Load the texture
    item.texture = LoadTexture(image_path);
    item.texture_loaded = true;
    
    // Set the source rect to the entire texture
    item.source_rect = (Rectangle){ 0, 0, (float)item.texture.width, (float)item.texture.height };
    
    // Set alpha value
    item.alpha_value = alpha_value;
    
    // Default scale is 1.0
    item.scale_x = 1.0f;
    item.scale_y = 1.0f;
    
    // Update the item's dimensions based on the texture
    item.base.width = item.texture.width;
    item.base.height = item.texture.height;
    
    // Update the base item's rectangles
    item.base.rect.width = item.texture.width;
    item.base.rect.height = item.texture.height;
    item.base.selected_rect.width = item.texture.width + item.base.selected_border_size;
    item.base.selected_rect.height = item.texture.height + item.base.selected_border_size;
    item.base.chosen_rect.width = item.texture.width + item.base.chosen_border_size;
    item.base.chosen_rect.height = item.texture.height + item.base.chosen_border_size;
    item.base.shadow_rect.width = item.texture.width;
    item.base.shadow_rect.height = item.texture.height;
    
    return item;
}

ImageItem InitImageItemFromTexture(Texture2D texture, Color color, int alpha_value) {
    ImageItem item;
    
    // Initialize base item
    item.base = InitItem(color);
    
    // Set the texture (we don't own it)
    item.texture = texture;
    item.texture_loaded = false;  // We don't own the texture, so we won't unload it
    
    // Set the source rect to the entire texture
    item.source_rect = (Rectangle){ 0, 0, (float)texture.width, (float)texture.height };
    
    // Set alpha value
    item.alpha_value = alpha_value;
    
    // Default scale is 1.0
    item.scale_x = 1.0f;
    item.scale_y = 1.0f;
    
    // Update the item's dimensions based on the texture
    item.base.width = texture.width;
    item.base.height = texture.height;
    
    // Update the base item's rectangles
    item.base.rect.width = texture.width;
    item.base.rect.height = texture.height;
    item.base.selected_rect.width = texture.width + item.base.selected_border_size;
    item.base.selected_rect.height = texture.height + item.base.selected_border_size;
    item.base.chosen_rect.width = texture.width + item.base.chosen_border_size;
    item.base.chosen_rect.height = texture.height + item.base.chosen_border_size;
    item.base.shadow_rect.width = texture.width;
    item.base.shadow_rect.height = texture.height;
    
    return item;
}

void UnloadImageItem(ImageItem* item) {
    if (item->texture_loaded) {
        UnloadTexture(item->texture);
        item->texture_loaded = false;
    }
}

void SetImageItemSourceRect(ImageItem* item, Rectangle source) {
    item->source_rect = source;
    
    // Update the item's dimensions based on the source rect
    item->base.width = source.width * item->scale_x;
    item->base.height = source.height * item->scale_y;
    
    // Update the base item's rectangles
    item->base.rect.width = source.width * item->scale_x;
    item->base.rect.height = source.height * item->scale_y;
    item->base.selected_rect.width = source.width * item->scale_x + item->base.selected_border_size;
    item->base.selected_rect.height = source.height * item->scale_y + item->base.selected_border_size;
    item->base.chosen_rect.width = source.width * item->scale_x + item->base.chosen_border_size;
    item->base.chosen_rect.height = source.height * item->scale_y + item->base.chosen_border_size;
    item->base.shadow_rect.width = source.width * item->scale_x;
    item->base.shadow_rect.height = source.height * item->scale_y;
}

void SetImageItemScale(ImageItem* item, float scale_x, float scale_y) {
    item->scale_x = scale_x;
    item->scale_y = scale_y;
    
    // Update the item's dimensions based on the scale
    item->base.width = item->source_rect.width * scale_x;
    item->base.height = item->source_rect.height * scale_y;
    
    // Update the base item's rectangles
    item->base.rect.width = item->source_rect.width * scale_x;
    item->base.rect.height = item->source_rect.height * scale_y;
    item->base.selected_rect.width = item->source_rect.width * scale_x + item->base.selected_border_size;
    item->base.selected_rect.height = item->source_rect.height * scale_y + item->base.selected_border_size;
    item->base.chosen_rect.width = item->source_rect.width * scale_x + item->base.chosen_border_size;
    item->base.chosen_rect.height = item->source_rect.height * scale_y + item->base.chosen_border_size;
    item->base.shadow_rect.width = item->source_rect.width * scale_x;
    item->base.shadow_rect.height = item->source_rect.height * scale_y;
}

float GetImageItemWidth(const ImageItem* item) {
    return item->source_rect.width * item->scale_x;
}

float GetImageItemHeight(const ImageItem* item) {
    return item->source_rect.height * item->scale_y;
}

void UpdateImageItem(ImageItem* item, float delta_time) {
    // Update base item for animations, etc.
    UpdateItem(&item->base, delta_time);
}

void DrawImageItem(const ImageItem* item) {
    // Skip drawing if alpha is 0
    if (item->alpha_value == 0) {
        return;
    }
    
    // Alpha to use for drawing
    float alpha_ratio = (float)item->alpha_value / 255.0f;
    
    // First draw the shadow
    Color shadow_color = ColorAlpha(item->base.shadow_color, alpha_ratio);
    Rectangle dest_shadow_rect = {
        item->base.x + item->base.shadow_offset_x + item->base.x_nudge,
        item->base.y + item->base.shadow_offset_y + item->base.y_nudge,
        item->source_rect.width * item->scale_x,
        item->source_rect.height * item->scale_y
    };
    DrawTexturePro(item->texture, item->source_rect, dest_shadow_rect, (Vector2){ 0, 0 }, 0, shadow_color);
    
    // Draw the various states
    if (item->base.chosen) {
        // If chosen, draw the chosen border
        DrawRectangleRec(item->base.chosen_rect, item->base.chosen_color);
    } else if (item->base.selected) {
        // If selected, draw the selected border
        DrawRectangleRec(item->base.selected_rect, item->base.selected_color);
    }
    
    // Draw the image with the item's color as a tint
    Rectangle dest_rect = {
        item->base.x + item->base.x_nudge,
        item->base.y + item->base.y_nudge,
        item->source_rect.width * item->scale_x,
        item->source_rect.height * item->scale_y
    };
    Color tint_color = ColorAlpha(item->base.color, alpha_ratio);
    DrawTexturePro(item->texture, item->source_rect, dest_rect, (Vector2){ 0, 0 }, 0, tint_color);
    
    // If disabled, draw the disabled overlay
    if (item->base.disabled) {
        Color disabled_color = ColorAlpha(item->base.disabled_color, alpha_ratio);
        DrawRectangleRec(item->base.rect, disabled_color);
    }
} 