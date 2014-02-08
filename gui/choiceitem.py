__author__ = "Olof Karlsson"
__license__ = "All Rights Reserved"

import pygame
import copy
import objects.shadow as shadow
import settings.settings as settings

"""

This is an item that, much like the other items, can be displayed on its on or added to a menu. It can be selected and / or chosen, much
like the other items. The thing about this item is that a font item is displayed in the middle of this item.

This is used for allowing the players to select the amount of rounds the want to play.

"""

class ChoiceItem():

	# Initialize the font module.
	pygame.font.init()

	# The standard text values are stored here, such as standard font, font size and so on.
	font_path = "fonts/ADDLG___.TTF"
	font_size = 9 * settings.GAME_SCALE
	font = pygame.font.Font(font_path, font_size)

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

	def __init__(self, value, color = pygame.Color(128, 128, 128), font_color = pygame.Color(255, 255, 255), alpha_value = 255):
		# These values cause the item to be drawn differently.
		self.selected = False
		self.chosen = False

		# We use these values to position and draw the item.
		self.x = ChoiceItem.x
		self.y = ChoiceItem.y
		self.width = ChoiceItem.width
		self.height = ChoiceItem.height

		# Setup font values.
		self.font = ChoiceItem.font
		self.font_color = font_color
		self.value = value
		self.alpha_value = alpha_value

		# Render the font surface.
		self.font_surface = self.font.render(str(self.value), False, self.font_color)
		self.font_surface.set_alpha(self.alpha_value)
		
		# Setup the color values.
		self.color = copy.copy(color)
		self.shadow_color = ChoiceItem.shadow_color
		self.shadow_offset_x = ChoiceItem.shadow_offset_x
		self.shadow_offset_y = ChoiceItem.shadow_offset_y
		self.selected_border_color = ChoiceItem.selected_border_color
		self.chosen_border_color = ChoiceItem.chosen_border_color

		# Create the rect used for drawing the ChoiceItem.
		self.rect = pygame.rect.Rect(self.x, self.y, self.width, self.height)
		self.selected_rect = pygame.rect.Rect(self.x - (ChoiceItem.selected_border_size / 2), self.y - (ChoiceItem.selected_border_size / 2), self.width + ChoiceItem.selected_border_size, self.height + ChoiceItem.selected_border_size)
		self.chosen_rect = pygame.rect.Rect(self.x - (ChoiceItem.chosen_border_size / 2), self.y - (ChoiceItem.chosen_border_size / 2), self.width + ChoiceItem.chosen_border_size, self.height + ChoiceItem.chosen_border_size)
		self.shadow_rect = pygame.rect.Rect(self.x + self.shadow_offset_x, self.y + self.shadow_offset_y, self.width, self.height)

	def get_width(self):
		return self.rect.width

	def get_height(self):
		return self.rect.height

	def draw(self, surface):
		# Update the position of the rects.
		self.rect.x = self.x
		self.rect.y = self.y
		self.selected_rect.x = self.x - (ChoiceItem.selected_border_size / 2.0)
		self.selected_rect.y = self.y - (ChoiceItem.selected_border_size / 2.0)
		self.chosen_rect.x = self.x - (ChoiceItem.chosen_border_size / 2.0)
		self.chosen_rect.y = self.y - (ChoiceItem.chosen_border_size / 2.0)
		self.shadow_rect.x = self.x + self.shadow_offset_x
		self.shadow_rect.y = self.y + self.shadow_offset_y

		# Draw the shadow.
		surface.fill(self.shadow_color, self.shadow_rect)

		# Draw the color of the item.
		surface.fill(self.color, self.rect)

		if self.chosen:
			# If the item is chosen, draw the chosen border.
			surface.fill(self.chosen_border_color, self.chosen_rect)

		if self.selected:
			# If the item is selected, draw the selected border.
			surface.fill(self.selected_border_color, self.selected_rect)

		# Draw the font surface in the middle of this item.
		surface.blit(self.font_surface, ((self.rect.x + (self.rect.width - self.font_surface.get_width()) / 2), self.rect.y + (self.rect.height - self.font_surface.get_height()) / 2))
