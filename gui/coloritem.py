__author__ = "Olof Karlsson"
__license__ = "All Rights Reserved"

import pygame
import math
import copy
import other.useful as useful
import objects.shadow as shadow
import objects.groups as groups
import settings.settings as settings

class ColorItem():

	# Standard values. These will be used unless any other values are specified per instance of this class.
	x = 0
	y = 0
	width = 16 * settings.GAME_SCALE
	height = 16 * settings.GAME_SCALE
	shadow_color = pygame.Color(50, 50, 50, 255)
	shadow_offset_x = 0 * settings.GAME_SCALE
	shadow_offset_y = 1 * settings.GAME_SCALE
	selected_border_color = pygame.Color(255, 255, 255, 255)
	selected_border_size = 2 * settings.GAME_SCALE
	chosen_border_color = pygame.Color(200, 200, 200)
	chosen_border_size = 2 * settings.GAME_SCALE
	unavailable_color = pygame.Color(100, 100, 100)

	def __init__(self, color):
		# These values cause the item to be drawn differently.
		self.selected = False
		self.chosen = False
		self.unavailable = False

		# We use these values to position and draw the item.
		self.x = ColorItem.x
		self.y = ColorItem.y
		self.width = ColorItem.width
		self.height = ColorItem.height
		
		# Setup the color values.
		self.color = copy.copy(color)
		self.shadow_color = ColorItem.shadow_color
		self.shadow_offset_x = ColorItem.shadow_offset_x
		self.shadow_offset_y = ColorItem.shadow_offset_y
		self.selected_border_color = ColorItem.selected_border_color
		self.chosen_border_color = ColorItem.chosen_border_color
		self.unavailable_color = ColorItem.unavailable_color

		# Create the rect used for drawing the item.
		self.rect = pygame.rect.Rect(self.x, self.y, self.width, self.height)
		self.selected_rect = pygame.rect.Rect(self.x - (ColorItem.selected_border_size / 2), self.y - (ColorItem.selected_border_size / 2), self.width + ColorItem.selected_border_size, self.height + ColorItem.selected_border_size)
		self.chosen_rect = pygame.rect.Rect(self.x - (ColorItem.chosen_border_size / 2), self.y - (ColorItem.chosen_border_size / 2), self.width + ColorItem.chosen_border_size, self.height + ColorItem.chosen_border_size)
		self.shadow_rect = pygame.rect.Rect(self.x + self.shadow_offset_x, self.y + self.shadow_offset_y, self.width, self.height)

	def get_width(self):
		return self.rect.width

	def get_height(self):
		return self.rect.height

	def draw(self, surface):
		self.rect.x = self.x
		self.rect.y = self.y
		self.selected_rect.x = self.x - (ColorItem.selected_border_size / 2.0)
		self.selected_rect.y = self.y - (ColorItem.selected_border_size / 2.0)
		self.chosen_rect.x = self.x - (ColorItem.chosen_border_size / 2.0)
		self.chosen_rect.y = self.y - (ColorItem.chosen_border_size / 2.0)
		self.shadow_rect.x = self.x + self.shadow_offset_x
		self.shadow_rect.y = self.y + self.shadow_offset_y

		surface.fill(self.shadow_color, self.shadow_rect)

		if self.chosen:
			surface.fill(self.chosen_border_color, self.chosen_rect)

		if self.selected:
			surface.fill(self.selected_border_color, self.selected_rect)

		if self.unavailable:
			surface.fill(self.unavailable_color, self.rect)
		else:
			surface.fill(self.color, self.rect)
