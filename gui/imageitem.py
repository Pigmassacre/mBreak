__author__ = "Olof Karlsson"
__license__ = "All Rights Reserved"

import pygame
import math
import copy
import other.useful as useful
import objects.shadow as shadow
import objects.groups as groups
import settings.settings as settings

class ImageItem():

	# Initialize the font module.
	pygame.font.init()

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
		# These values cause the item to be drawn differently.
		self.selected = False
		self.chosen = False

		# We use these values to position and draw the item.
		self.x = ImageItem.x
		self.y = ImageItem.y
		self.width = ImageItem.width
		self.height = ImageItem.height

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

	def draw(self, surface):
		self.rect.x = self.x
		self.rect.y = self.y
		self.selected_rect.x = self.x - (ImageItem.selected_border_size / 2.0)
		self.selected_rect.y = self.y - (ImageItem.selected_border_size / 2.0)
		self.chosen_rect.x = self.x - (ImageItem.chosen_border_size / 2.0)
		self.chosen_rect.y = self.y - (ImageItem.chosen_border_size / 2.0)
		self.shadow_rect.x = self.x + self.shadow_offset_x
		self.shadow_rect.y = self.y + self.shadow_offset_y

		surface.fill(self.shadow_color, self.shadow_rect)
		surface.fill(self.color, self.rect)

		if self.chosen:
			surface.fill(self.chosen_border_color, self.chosen_rect)

		if self.selected:
			surface.fill(self.selected_border_color, self.selected_rect)

		surface.blit(self.image, ((self.rect.x + (self.rect.width - self.image.get_width()) / 2), self.rect.y + (self.rect.height - self.image.get_height()) / 2))
