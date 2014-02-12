__author__ = "Olof Karlsson"
__license__ = "All Rights Reserved"

import pygame
import copy
import math
import objects.shadow as shadow
import gui.item as item
import settings.settings as settings

"""

This is an item that, much like TextItem, can be displayed either by itself or added to a menu. It's a 
filled rectangle with an image in the middle of it. It can, much like the other items, we selected and / or chosen.

Arguably, all these items (ImageItem, TextItem etc.) should subclass some more generic Item class. However,
while they share alot of the same names for the variables, they all differ so much that there's hardly any
point in them subclassing item. I tried several times, but I couldn't for the life of me figure out what item
should contain. I hope that this is OK.

"""

class ImageItem(item.Item):

	# Standard values. These will be used unless any other values are specified per instance of this class.
	x = 0
	y = 0
	width = 16 * settings.GAME_SCALE
	height = 16 * settings.GAME_SCALE
	shadow_color = pygame.Color(50, 50, 50)
	shadow_offset_x = 0 * settings.GAME_SCALE
	shadow_offset_y = 1 * settings.GAME_SCALE
	selected_border_color = pygame.Color(255, 255, 255)
	selected_border_size = 2 * settings.GAME_SCALE
	chosen_border_color = pygame.Color(200, 200, 200)
	chosen_border_size = 2 * settings.GAME_SCALE

	def __init__(self, path, color = pygame.Color(128, 128, 128)):
		item.Item.__init__(self)

		# These values cause the item to be drawn differently.
		self.selected = False
		self.chosen = False

		# We use these values to position and draw the item.
		self.x = ImageItem.x
		self.y = ImageItem.y
		self.width = ImageItem.width
		self.height = ImageItem.height

		# Values can be stored here, for when you want to retrieve it later (via chosing the item, for instance).
		self.value = None

		# Load the image from the path.
		self.image = pygame.image.load(path)

		# Scale image to settings.GAME_SCALE.
		self.image = pygame.transform.scale(self.image, (self.image.get_width() * settings.GAME_SCALE, self.image.get_height() * settings.GAME_SCALE))
		
		# Setup the color values.
		self.color = copy.copy(color)
		self.shadow_color = ImageItem.shadow_color
		self.shadow_offset_x = ImageItem.shadow_offset_x
		self.shadow_offset_y = ImageItem.shadow_offset_y
		self.selected_border_color = ImageItem.selected_border_color
		self.chosen_border_color = ImageItem.chosen_border_color

		# Create the rect used for drawing the ImageItem.
		self.rect = pygame.rect.Rect(self.x, self.y, self.width, self.height)
		self.selected_rect = pygame.rect.Rect(self.x - (ImageItem.selected_border_size / 2), self.y - (ImageItem.selected_border_size / 2), self.width + ImageItem.selected_border_size, self.height + ImageItem.selected_border_size)
		self.chosen_rect = pygame.rect.Rect(self.x - (ImageItem.chosen_border_size / 2), self.y - (ImageItem.chosen_border_size / 2), self.width + ImageItem.chosen_border_size, self.height + ImageItem.chosen_border_size)
		self.shadow_rect = pygame.rect.Rect(self.x + self.shadow_offset_x, self.y + self.shadow_offset_y, self.width, self.height)

	def get_width(self):
		return self.rect.width

	def get_height(self):
		return self.rect.height

	def update(self, main_clock):
		item.Item.update(self, main_clock)

		# Update the position of all the rects.
		self.rect.x = self.x
		self.rect.y = self.y + self.y_nudge
		self.selected_rect.x = self.x - (ImageItem.selected_border_size / 2.0)
		self.selected_rect.y = self.y - (ImageItem.selected_border_size / 2.0) + self.y_nudge
		self.chosen_rect.x = self.x - (ImageItem.chosen_border_size / 2.0)
		self.chosen_rect.y = self.y - (ImageItem.chosen_border_size / 2.0) + self.y_nudge
		self.shadow_rect.x = self.x + self.shadow_offset_x
		self.shadow_rect.y = self.y + self.shadow_offset_y + self.y_nudge

	def draw(self, surface):
		item.Item.draw(self, surface)

		# Draw the shadow.
		surface.fill(self.shadow_color, self.shadow_rect)
		surface.fill(self.color, self.rect)

		# If chosen, draw the chosen border around the item.
		if self.chosen:
			surface.fill(self.chosen_border_color, self.chosen_rect)

			# If also selected, draw a smaller selected border around the item.
			if self.selected:
				surface.fill(self.selected_border_color, self.rect)

		elif self.selected:
			# If selected, draw the selected border around the item.
			surface.fill(self.selected_border_color, self.selected_rect)

		# Finally, blit the image to the given surface (on top of everything else drawn in here).
		surface.blit(self.image, ((self.rect.x + (self.rect.width - self.image.get_width()) / 2), self.rect.y + (self.rect.height - self.image.get_height()) / 2))
