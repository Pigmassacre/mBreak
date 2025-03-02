__author__ = "Olof Karlsson"
__license__ = "All Rights Reserved"

import pygame
import math
import gui.menu as menu
import gui.item as item
import settings.settings as settings

"""
This is a subclass of Menu that positions its items in a color wheel fashion.
It allows users to select colors from a continuous color wheel rather than from a limited set of predefined colors.
"""

class ColorWheelMenu(menu.Menu):

    def __init__(self, radius=40, center_x=0, center_y=0):
        # Call the superconstructor
        super(ColorWheelMenu, self).__init__()
        
        # Store the radius of the color wheel
        self.radius = radius
        
        # Store the center position of the color wheel
        self.center_x = center_x
        self.center_y = center_y
        
        # Create the color wheel surface
        self.wheel_surface = pygame.Surface((radius * 2, radius * 2), pygame.SRCALPHA)
        self.generate_color_wheel()
        
        # The currently selected color (will be set when user selects a color)
        self.selected_color = None
        
        # The currently selected position on the wheel (will be set when user selects a color)
        self.selected_pos = None
        
        # The current hover position (will be updated as mouse moves over the wheel)
        self.hover_pos = None
        
        # Create a special item to represent the selected color
        self.color_display = item.Item()
        self.color_display.width = 20
        self.color_display.height = 20
        self.color_display.rect.width = self.color_display.width
        self.color_display.rect.height = self.color_display.height
        
        # Flag to determine if color display should be updated automatically
        self.auto_position_color_display = True
        
        # Add a dummy item to make this menu compatible with the game's menu navigation system
        dummy_item = item.Item()
        dummy_item.width = 0
        dummy_item.height = 0
        self.add(dummy_item, self.dummy_function)
        
    def generate_color_wheel(self):
        """Generate the color wheel surface"""
        # Clear the surface with transparent background
        self.wheel_surface.fill((0, 0, 0, 0))
        
        for x in range(self.radius * 2):
            for y in range(self.radius * 2):
                # Calculate the position relative to the center
                dx = x - self.radius
                dy = y - self.radius
                
                # Calculate the distance from the center
                distance = math.sqrt(dx * dx + dy * dy)
                
                if distance <= self.radius:
                    # Calculate the hue based on the angle
                    angle = math.atan2(dy, dx)
                    hue = (angle / (2 * math.pi)) % 1.0
                    
                    # Calculate the saturation based on the distance from center
                    saturation = min(1.0, distance / self.radius)
                    
                    # Convert HSV to RGB
                    color = self.hsv_to_rgb(hue, saturation, 1.0)
                    
                    # Set the pixel color
                    self.wheel_surface.set_at((x, y), color)
    
    def hsv_to_rgb(self, h, s, v):
        """Convert HSV color values to RGB"""
        if s == 0.0:
            return (int(v * 255), int(v * 255), int(v * 255))
        
        h *= 6.0
        i = int(h)
        f = h - i
        p = v * (1.0 - s)
        q = v * (1.0 - s * f)
        t = v * (1.0 - s * (1.0 - f))
        
        if i == 0:
            return (int(v * 255), int(t * 255), int(p * 255))
        elif i == 1:
            return (int(q * 255), int(v * 255), int(p * 255))
        elif i == 2:
            return (int(p * 255), int(v * 255), int(t * 255))
        elif i == 3:
            return (int(p * 255), int(q * 255), int(v * 255))
        elif i == 4:
            return (int(t * 255), int(p * 255), int(v * 255))
        else:
            return (int(v * 255), int(p * 255), int(q * 255))
    
    def get_color_at_position(self, pos):
        """Get the color at a specific position on the wheel"""
        # Calculate position relative to the top-left corner of the wheel
        x = pos[0] - self.x
        y = pos[1] - self.y
        
        # Check if the position is within the wheel's bounding box
        if 0 <= x < self.radius * 2 and 0 <= y < self.radius * 2:
            # Calculate distance from center of the wheel
            dx = x - self.radius
            dy = y - self.radius
            distance = math.sqrt(dx * dx + dy * dy)
            
            if distance <= self.radius:
                # Return the color at this position
                return self.wheel_surface.get_at((int(x), int(y)))
        
        return None
    
    def select_color(self, pos):
        """Select a color at the given position"""
        color = self.get_color_at_position(pos)
        if color:
            self.selected_color = color
            # Store the position relative to the top-left corner of the wheel
            self.selected_pos = (pos[0] - self.x, pos[1] - self.y)
            self.color_display.color = color
            
            # Play a sound effect to indicate selection
            sound = self.sound_effect.play()
            if sound:
                sound.set_volume(settings.SOUND_VOLUME)
                
            return color
        return None
    
    def get_width(self):
        """Return the width of the color wheel"""
        return self.radius * 2
    
    def get_height(self):
        """Return the height of the color wheel"""
        return self.radius * 2
    
    def set_color_display_position(self, x, y):
        """Set a custom position for the color display"""
        self.color_display.x = x
        self.color_display.y = y
        self.auto_position_color_display = False
        
    def update(self, main_clock):
        """Update the color wheel menu"""
        super(ColorWheelMenu, self).update(main_clock)
        
        # Update the color display position if auto-positioning is enabled
        if self.auto_position_color_display:
            self.color_display.x = self.x + self.radius * 2 + 10
            self.color_display.y = self.y + self.radius - self.color_display.height / 2
        
        # Update hover position if mouse is over the wheel
        mouse_pos = pygame.mouse.get_pos()
        color = self.get_color_at_position(mouse_pos)
        if color:
            self.hover_pos = (mouse_pos[0] - self.x, mouse_pos[1] - self.y)
            
            # Update the color display to show the color under the cursor
            # If a color is selected, keep showing that color
            if not self.selected_color:
                self.color_display.color = color
        else:
            self.hover_pos = None
            
            # If no color is selected and mouse is not over the wheel, show a default color
            if not self.selected_color:
                self.color_display.color = pygame.Color(128, 128, 128)  # Gray
                
        self.color_display.update(main_clock)
    
    def draw(self, surface):
        """Draw the color wheel menu"""
        # Draw the color wheel
        surface.blit(self.wheel_surface, (self.x, self.y))
        
        # Draw the selected position indicator if a color is selected
        if self.selected_pos:
            # Draw a yellow square to mark the selected color
            square_size = 8
            pygame.draw.rect(
                surface,
                pygame.Color(255, 255, 0),  # Yellow
                pygame.Rect(
                    int(self.x + self.selected_pos[0] - square_size/2),
                    int(self.y + self.selected_pos[1] - square_size/2),
                    square_size,
                    square_size
                ),
                2  # Line width
            )
        
        # Draw the hover position indicator if mouse is over the wheel
        if self.hover_pos:
            # Draw a white circle to show the current hover position
            pygame.draw.circle(
                surface,
                pygame.Color(255, 255, 255),  # White
                (int(self.x + self.hover_pos[0]), int(self.y + self.hover_pos[1])),
                5,
                1
            )
        
        # Draw the color display
        self.color_display.draw(surface)
    
    def dummy_function(self, item):
        # This function does nothing, it's just to satisfy the menu system
        pass 

    def clear_selection(self):
        """Clear the selected color"""
        self.selected_color = None
        self.selected_pos = None 