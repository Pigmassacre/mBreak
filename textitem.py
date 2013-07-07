__author__ = "Olof Karlsson"
__version__ = "0.1"
__license__ = "All Rights Reserved"

import pygame
import math
from settings import *

class TextItem:

	def __init__(self, text_value, font_path, font_size, font_color, alpha_value):
		self.x = 0
		self.y = 0
		self.text_value = text_value
		self.font_color = font_color
		self.font = pygame.font.Font(font_path, font_size)
		self.surface = self.font.render(self.text_value, False, self.font_color)
		self.surface.set_alpha(alpha_value)

		# Store the color.
		self.shadow_color = pygame.Color(TEXT_SHADOW_COLOR[0], TEXT_SHADOW_COLOR[1], TEXT_SHADOW_COLOR[2], TEXT_SHADOW_COLOR[3])
		# Create the surface used for drawing the shadow.
		self.shadow_surface = self.font.render(self.text_value, False, self.shadow_color)
		self.shadow_surface.set_alpha(alpha_value)
		# Store the offset, the distance from the parent the shadow is drawn from.
		self.shadow_offset = TEXT_SHADOW_OFFSET

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
