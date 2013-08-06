__author__ = "Olof Karlsson"
__version__ = "0.1"
__license__ = "All Rights Reserved"

import pygame
import math
import other.useful as useful
from settings.settings import *

class TextItem:

	# Initialize the font module.
	pygame.font.init()

	# The standard text values are stored here, such as standard font, font size and so on.
	font_path = "fonts/8-BIT WONDER.TTF"
	font_size = 9 * GAME_SCALE
	font = pygame.font.Font(font_path, font_size)
	x = 0
	y = 0
	shadow_offset = 3
	shadow_color = pygame.Color(50, 50, 50, 255)
	selected_color = pygame.Color(128, 128, 128, 255)
	on_color = pygame.Color(20, 255, 20, 255)
	off_color = pygame.Color(255, 20, 20, 255)
	blink_rate = 750

	def __init__(self, text_value, font_color, alpha_value = 255):
		# Load default values.
		self.x = TextItem.x
		self.y = TextItem.y
		self.font = TextItem.font
		self.selected_font_color = TextItem.selected_color
		self.selected = False
		self.on_font_color = TextItem.on_color
		self.off_font_color = TextItem.off_color
		self.selected_on_font_color = useful.blend_colors(self.on_font_color, self.selected_font_color, True)
		self.selected_off_font_color = useful.blend_colors(self.off_font_color, self.selected_font_color, True)
		self.is_on_off = False
		self.on = False
		self.blink_rate = TextItem.blink_rate

		# Set the given values.
		self.text_value = text_value
		self.font_color = font_color
		self.alpha_value = alpha_value

		# Setup the shadow.
		self.shadow_color = TextItem.shadow_color
		self.shadow_offset = TextItem.shadow_offset

		self.setup_surfaces()

	def setup_surfaces(self):
		# Render the font surface.
		self.surface = self.font.render(self.text_value, False, self.font_color)
		self.surface.set_alpha(self.alpha_value)

		# Render the selected font surface.
		self.selected_surface = self.font.render(self.text_value, False, self.selected_font_color)
		self.selected_surface.set_alpha(self.alpha_value)

		# Render the on font surface.
		self.on_surface = self.font.render(self.text_value, False, self.on_font_color)
		self.on_surface.set_alpha(self.alpha_value)

		# Render the off font surface.
		self.off_surface = self.font.render(self.text_value, False, self.off_font_color)
		self.off_surface.set_alpha(self.alpha_value)

		# Render the selected and on surface.
		self.selected_on_surface = self.font.render(self.text_value, False, self.selected_on_font_color)
		self.selected_on_surface.set_alpha(self.alpha_value)

		# Render the selected and off surface.
		self.selected_off_surface = self.font.render(self.text_value, False, self.selected_off_font_color)
		self.selected_off_surface.set_alpha(self.alpha_value)

		# Create the surface used for drawing the shadow.
		self.shadow_surface = self.font.render(self.text_value, False, self.shadow_color)
		self.shadow_surface.set_alpha(self.alpha_value)

	def set_font(self, font_path):
		if not self.font_path == font_path:
			self.font = pygame.font.Font(font_path, self.font_size)
			self.setup_surfaces()

	def set_size(self, font_size):
		if not self.font_size == font_size:
			temp_alpha = self.surface.get_alpha()
			self.font_size = font_size
			self.font = pygame.font.Font(self.font_path, self.font_size)
			self.setup_surfaces()

	def get_width(self):
		return self.font.size(self.text_value)[0]

	def get_height(self):
		return self.font.size(self.text_value)[1]

	def blink(self, time_passed):
		"""
		If called once per loop, switches the target surface alpha value between 255 and 0 every blink_rate.
		The surface spends 2/3s of the time with alpha value 0 as with 255.
		"""
		if time_passed > self.blink_rate:
			if self.surface.get_alpha() == 255:
				self.surface.set_alpha(0)
				self.shadow_surface.set_alpha(0)
				return self.blink_rate // 3
			else:
				self.surface.set_alpha(255)
				self.shadow_surface.set_alpha(255)
				return 0
		else:
			return time_passed

	def toggle_on_off(self):
		self.on = not self.on
		return self.on

	def draw(self, surface):
		# First blit shadow, then self. Keeps shadow UNDER the text.
		surface.blit(self.shadow_surface, (self.x + self.shadow_offset, self.y + self.shadow_offset))
		if self.selected:
			if self.is_on_off:
				if self.on:
					surface.blit(self.selected_on_surface, (self.x, self.y))
				elif not self.on:
					surface.blit(self.selected_off_surface, (self.x, self.y))
			else:
				surface.blit(self.selected_surface, (self.x, self.y))
		elif self.is_on_off:
			if self.on:
				surface.blit(self.on_surface, (self.x, self.y))
			else:
				surface.blit(self.off_surface, (self.x, self.y))
		else:
			surface.blit(self.surface, (self.x, self.y))
