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
	shadow_color = pygame.Color(0, 0, 0, 128)
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
		
		# Create the rect used for drawing the ColorItem.
		self.rect = pygame.rect.Rect(self.x, self.y, self.width, self.height)
		self.selected_rect = pygame.rect.Rect(self.x - (ColorItem.selected_border_size / 2), self.y - (ColorItem.selected_border_size / 2), self.width + ColorItem.selected_border_size, self.height + ColorItem.selected_border_size)

		# Setup the color values, used for drawing the ColorItem.
		self.color = copy.copy(color)
		self.selected_border_color = ColorItem.selected_border_color

		# Create a shadow.
		# self.shadow = shadow.Shadow(self, self.shadow_color, False, True)

	def get_width(self):
		return self.rect.width

	def get_height(self):
		return self.rect.height

	def draw(self, surface):
		self.rect.x = self.x
		self.rect.y = self.y
		self.selected_rect.x = self.x - (ColorItem.selected_border_size / 2.0)
		self.selected_rect.y = self.y - (ColorItem.selected_border_size / 2.0)
		if self.selected:
			surface.fill(self.selected_border_color, self.selected_rect)
		surface.fill(self.color, self.rect)
