__author__ = "Olof Karlsson"
__license__ = "All Rights Reserved"

import pygame
import math
import other.useful as useful
import gui.item as item
import settings.settings as settings

"""

This is a class that is a pretty useful "wrapper" around pygame's font-module. It can be stored as an item in a menu,
or simply used to display text. It has a quite a few extra surfaces and variables that allows it to function as a button in a menu.

"""

def generate_list_from_string(string):
	list = []
	for letter in string:
		letter_item = TextItem(letter)
		list.append(letter_item)
	return list

class TextItem(item.Item):

	# Initialize the font module.
	pygame.font.init()

	# The standard text values are stored here, such as standard font, font size and so on.
	font_path = "fonts/ADDLG___.TTF"
	font_size = 9 * settings.GAME_SCALE
	font = pygame.font.Font(font_path, font_size)
	
	# Standard values. These will be used unless any other values are specified per instance of this class.
	on_color = pygame.Color(0, 90, 0)
	off_color = pygame.Color(90, 0, 0)
	selected_on_color = pygame.Color(0, 255, 0)
	selected_off_color = pygame.Color(255, 0, 0)

	# This is the rate at which the textitem will blink if blink() is called once per frame.
	blink_rate = 750

	def __init__(self, string, color = pygame.Color(128, 128, 128), alpha_value = 255, size = None):
		super(TextItem, self).__init__(color)

		# Load default values.
		self.selected_font_color = TextItem.selected_color
		self.on_font_color = TextItem.on_color
		self.off_font_color = TextItem.off_color
		self.selected_on_font_color = TextItem.selected_on_color
		self.selected_off_font_color = TextItem.selected_off_color
		self.is_on_off = False
		self.on = False
		self.font_size = TextItem.font_size
		self.font_path = TextItem.font_path

		# If blink is set to true, this item will "blink" (show/hide itself) at the set blink_rate.
		self.blink = False
		self.blink_rate = TextItem.blink_rate
		self.time_passed = 0

		# Set the given values.
		self.string = string
		self.off_string = string
		self.font_color = color
		self.alpha_value = alpha_value
		self.size = size

		# If no size was given, we default to the already loaded font object. If some size WAS given however,
		# we load a new font object with the given size.
		if self.size != None:
			self.font = pygame.font.Font(self.font_path, self.size)
		else:
			self.font = TextItem.font

		self.setup_surfaces()

	def setup_surfaces(self):
		# Render the font surface.
		self.surface = self.font.render(self.string, False, self.font_color)
		self.surface.set_alpha(self.alpha_value)

		# Render the selected font surface.
		self.selected_surface = self.font.render(self.string, False, self.selected_font_color)
		self.selected_surface.set_alpha(self.alpha_value)

		# Create the surface used for drawing the shadow.
		self.shadow_surface = self.font.render(self.string, False, self.shadow_color)
		self.shadow_surface.set_alpha(self.alpha_value)

	def setup_is_on_off(self, off_string, state):
		# Set the textitem to be on and off, set the on state and save the off text value.
		self.is_on_off = True
		self.on = state
		self.off_string = off_string

		# Render the on font surface.
		self.on_surface = self.font.render(self.string, False, self.on_font_color)
		self.on_surface.set_alpha(self.alpha_value)

		# Render the off font surface.
		self.off_surface = self.font.render(self.off_string, False, self.off_font_color)
		self.off_surface.set_alpha(self.alpha_value)

		# Render the selected and on surface.
		self.selected_on_surface = self.font.render(self.string, False, self.selected_on_font_color)
		self.selected_on_surface.set_alpha(self.alpha_value)

		# Render the selected and off surface.
		self.selected_off_surface = self.font.render(self.off_string, False, self.selected_off_font_color)
		self.selected_off_surface.set_alpha(self.alpha_value)

		# Create the surface used for drawing the shadow.
		self.shadow_off_surface = self.font.render(self.off_string, False, self.shadow_color)
		self.shadow_off_surface.set_alpha(self.alpha_value)

	def set_font(self, font_path):
		if not self.font_path == font_path:
			self.font = pygame.font.Font(font_path, self.font_size)
			self.setup_surfaces()

	def set_size(self, font_size):
		if not self.font_size == font_size:
			temp_alpha = self.surface.get_alpha()
			self.font_size = font_size
			self.font = pygame.font.Font(self.font_path, font_size)
			self.setup_surfaces()
			if self.is_on_off:
				self.setup_is_on_off(self.off_string, self.on)

	def set_string(self, string):
		if not self.string == string:
			self.string = string
			self.setup_surfaces()

	def set_bold(self, choice):
		self.font.set_bold(choice)
		self.setup_surfaces()

	def set_italic(self, choice):
		self.font.set_italic(choice)
		self.setup_surfaces()

	def set_color(self, color):
		self.font_color = color
		self.setup_surfaces()

	def get_width(self):
		return self.font.size(self.string)[0]

	def get_height(self):
		return self.font.size(self.string)[1]

	def update(self, main_clock):
		super(TextItem, self).update(main_clock)

		if self.blink:
			if self.time_passed > self.blink_rate:
				if self.surface.get_alpha() == 255:
					self.surface.set_alpha(0)
					self.selected_surface.set_alpha(0)
					self.shadow_surface.set_alpha(0)
					return self.blink_rate / 3
				else:
					self.surface.set_alpha(255)
					self.selected_surface.set_alpha(255)
					self.shadow_surface.set_alpha(255)
					return 0

	def toggle_on_off(self):
		self.on = not self.on
		return self.on

	def draw(self, surface):
		# First we determine what shadow to blit, and then blit that. We do this before we blit the text so the shadow is under the text.
		if self.is_on_off:
			if self.on:
				surface.blit(self.shadow_surface, (self.x + self.shadow_offset_x, self.y + self.shadow_offset_y + self.y_nudge))
			else:
				surface.blit(self.shadow_off_surface, (self.x + self.shadow_offset_x, self.y + self.shadow_offset_y + self.y_nudge))
		else:
			surface.blit(self.shadow_surface, (self.x + self.shadow_offset_x, self.y + self.shadow_offset_y + self.y_nudge))

		# Then we determine what text surface to blit, and blit that.
		if self.selected:
			if self.is_on_off:
				if self.on:
					surface.blit(self.selected_on_surface, (self.x, self.y + self.y_nudge))
				elif not self.on:
					surface.blit(self.selected_off_surface, (self.x, self.y + self.y_nudge))
			else:
				surface.blit(self.selected_surface, (self.x, self.y + self.y_nudge))
		elif self.is_on_off:
			if self.on:
				surface.blit(self.on_surface, (self.x, self.y + self.y_nudge))
			else:
				surface.blit(self.off_surface, (self.x, self.y + self.y_nudge))
		else:
			surface.blit(self.surface, (self.x, self.y + self.y_nudge))
