__author__ = "Olof Karlsson"
__license__ = "All Rights Reserved"

import pygame
import math
import settings.settings as settings
import objects.shadow as shadow
import objects.groups as groups

class ArrowIndicator(pygame.sprite.Sprite):
    def __init__(self, x, y, angle):
        # Call the parent class constructor
        pygame.sprite.Sprite.__init__(self)
        
        # Create a surface for the arrow
        self.width = 15  # Back to half length
        self.height = 6  # Taller to accommodate shadow offset
        self.image = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
        
        # Draw the arrow shape
        arrow_color = (255, 255, 255, 180)  # White with some transparency
        
        # Draw arrow body (2px wide line)
        pygame.draw.line(self.image, arrow_color, (0, self.height//2), (self.width - 6, self.height//2), 2)
        
        # Draw arrow head (smaller triangle)
        arrow_head = [
            (self.width - 6, self.height//2 - 3),  # Top point
            (self.width, self.height//2),          # Tip
            (self.width - 6, self.height//2 + 3)   # Bottom point
        ]
        pygame.draw.polygon(self.image, arrow_color, arrow_head)
        
        # Store the original image for rotation
        self.original_image = self.image
        
        # Create rect and position it
        self.rect = self.image.get_rect()
        self.x = x
        self.y = y
        
        # Store and apply the angle
        self.angle = angle
        self.update_rotation()

        # Create a shadow
        self.shadow = shadow.Shadow(self)
        groups.Groups.shadow_group.add(self.shadow)
    
    def update_rotation(self):
        """Rotate the arrow to match the current angle"""
        # Convert angle from radians to degrees and adjust for pygame's rotation system
        angle_degrees = math.degrees(self.angle)
        self.image = pygame.transform.rotate(self.original_image, -angle_degrees)
        
        # Get the new rect after rotation
        self.rect = self.image.get_rect()
        
        # Calculate angle-based offset to maintain start point
        cos_angle = math.cos(self.angle)
        sin_angle = math.sin(self.angle)
        
        # Set both rect and sprite position, adjusting based on direction
        if cos_angle < 0:  # Pointing left
            self.rect.x = self.x - self.rect.width
            # Keep self.x at the start of the arrow for shadow positioning
            self.x = self.rect.x
        else:  # Pointing right
            self.rect.x = self.x
        self.rect.y = self.y - self.rect.height // 2
    
    def update(self, x, y, angle):
        """Update the arrow's position and angle"""
        self.x = x
        self.y = y
        if self.angle != angle:
            self.angle = angle
        self.update_rotation()
        
        # Update shadow position
        self.shadow.update()
    
    def draw(self, surface):
        """Draw the arrow on the given surface"""
        surface.blit(self.image, self.rect)
        
    def destroy(self):
        """Takes care of killing self and shadow."""
        self.kill()
        self.shadow.kill() 