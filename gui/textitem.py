__author__ = "Olof Karlsson"
__version__ = "0.1"
__license__ = "All Rights Reserved"

import pygame
import math
from settings.settings import *

class TextItem:

	# Initialize the font module.
	pygame.font.init()

	# The standard text values are store here, such as standard font, font size and so on.
	font_path = "fonts/8-BIT WONDER.TTF"
	font_size = 9 * GAME_SCALE
	font = pygame.font.Font(font_path, font_size)
	x = 0
	y = 0
	shadow_offset = 3
	shadow_color = pygame.Color(0, 0, 0, 255)

	def __init__(self, text_value, font_color, alpha_value):
		# Load default values.
		self.x = TextItem.x
		self.y = TextItem.y
		self.font = TextItem.font

		# Set the given values.
		self.text_value = text_value
		self.font_color = font_color

		# Render the font surface.
		self.surface = self.font.render(self.text_value, False, self.font_color)
		self.surface.set_alpha(alpha_value)

		# Setup the shadow.
		self.shadow_color = TextItem.shadow_color
		self.shadow_offset = TextItem.shadow_offset

		# Create the surface used for drawing the shadow.
		self.shadow_surface = self.font.render(self.text_value, False, self.shadow_color)
		self.shadow_surface.set_alpha(alpha_value)

	def set_font(self, font_path):
		if not self.font_path == font_path:
			self.font = pygame.font.Font(font_path, self.font_size)

	def set_size(self, font_size):
		if not self.font_size == font_size:
			temp_alpha = self.surface.get_alpha()
			self.font_size = font_size
			self.font = pygame.font.Font(self.font_path, self.font_size)
			self.surface = self.font.render(self.text_value, False, self.font_color)
			self.surface.set_alpha(temp_alpha)

	def get_width(self):
		return self.font.size(self.text_value)[0]

	def get_height(self):
		return self.font.size(self.text_value)[1]

	def blink(self, time_passed, blink_rate):
		"""
		If called once per loop, switches the target surface alpha value between 255 and 0 every blink_rate.
		The surface spends 2/3s of the time with alpha value 0 as with 255.
		"""
		if time_passed > blink_rate:
			if self.surface.get_alpha() == 255:
				self.surface.set_alpha(0)
				self.shadow_surface.set_alpha(0)
				return blink_rate // 3
			else:
				self.surface.set_alpha(255)
				self.shadow_surface.set_alpha(255)
				return 0
		else:
			return time_passed

	def draw(self, window_surface):
		# First blit shadow, then self. Keeps shadow UNDER the text.
		window_surface.blit(self.shadow_surface, (self.x + self.shadow_offset, self.y + self.shadow_offset))
		window_surface.blit(self.surface, (self.x, self.y))
