__author__ = "Olof Karlsson"
__version__ = "0.1"
__license__ = "All Rights Reserved"

import pygame
import math
import copy
import other.useful as useful
import objects.shadow as shadow
import objects.groups as groups
from settings.settings import *

class ColorItem():

	# Standard values. These will be used unless any other values are specified per instance of this class.
	shadow_color = pygame.Color(50, 50, 50, 255)
	shadow_offset_x = 0
	shadow_offset_y = 3
	selected_border_color = pygame.Color(255, 255, 255, 255)
	selected_border_size = 2 * GAME_SCALE
	x = 0
	y = 0
	width = 16 * GAME_SCALE
	height = 16 * GAME_SCALE

	def __init__(self, color):
		self.selected = False

		self.x = ColorItem.x
		self.y = ColorItem.y
		self.width = ColorItem.width
		self.height = ColorItem.height
		
		# Setup the color values, used for drawing the ColorItem.
		self.color = copy.copy(color)
		self.selected_border_color = ColorItem.selected_border_color
		self.shadow_color = ColorItem.shadow_color
		self.shadow_offset_x = ColorItem.shadow_offset_x
		self.shadow_offset_y = ColorItem.shadow_offset_y

		# Create the rect used for drawing the ColorItem.
		self.rect = pygame.rect.Rect(self.x, self.y, self.width, self.height)
		self.selected_rect = pygame.rect.Rect(self.x - (ColorItem.selected_border_size / 2), self.y - (ColorItem.selected_border_size / 2), self.width + ColorItem.selected_border_size, self.height + ColorItem.selected_border_size)
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
		self.shadow_rect.x = self.x + self.shadow_offset_x
		self.shadow_rect.y = self.y + self.shadow_offset_y

		surface.fill(self.shadow_color, self.shadow_rect)

		if self.selected:
			surface.fill(self.selected_border_color, self.selected_rect)

		surface.fill(self.color, self.rect)
