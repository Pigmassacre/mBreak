__author__ = "Olof Karlsson"
__license__ = "All Rights Reserved"

import pygame
import settings.settings as settings
import settings.graphics as graphics

class Background:
	
	def __init__(self, folder_name):
		# Setup the background surfaces.
		self.floor_surface = pygame.image.load("res/background/" + folder_name + "/floor.png")
		self.floor_surface = pygame.transform.scale(self.floor_surface, (self.floor_surface.get_width() * settings.GAME_SCALE, self.floor_surface.get_height() * settings.GAME_SCALE))
		self.wall_vertical = pygame.image.load("res/background/" + folder_name + "/wall_vertical.png")
		self.wall_vertical = pygame.transform.scale(self.wall_vertical, (self.wall_vertical.get_width() * settings.GAME_SCALE, self.wall_vertical.get_height() * settings.GAME_SCALE))
		self.wall_horizontal = pygame.image.load("res/background/" + folder_name + "/wall_horizontal.png")
		self.wall_horizontal = pygame.transform.scale(self.wall_horizontal, (self.wall_horizontal.get_width() * settings.GAME_SCALE, self.wall_horizontal.get_height() * settings.GAME_SCALE))
		self.corner_top_left = pygame.image.load("res/background/" + folder_name + "/corner_top_left.png")
		self.corner_top_left = pygame.transform.scale(self.corner_top_left, (self.corner_top_left.get_width() * settings.GAME_SCALE, self.corner_top_left.get_height() * settings.GAME_SCALE))
		self.corner_top_right = pygame.image.load("res/background/" + folder_name + "/corner_top_right.png")
		self.corner_top_right = pygame.transform.scale(self.corner_top_right, (self.corner_top_right.get_width() * settings.GAME_SCALE, self.corner_top_right.get_height() * settings.GAME_SCALE))

		# Convert the surfaces, for performances sake.
		self.floor_surface.convert()
		self.wall_vertical.convert()
		self.wall_horizontal.convert()
		self.corner_top_left.convert()
		self.corner_top_right.convert()

		# Setup the rects used to display a white border around the level if graphics.BACKGROUND is False.
		self.wall_horizontal_top_rect = pygame.Rect(settings.LEVEL_X - self.wall_vertical.get_width(), settings.LEVEL_Y - self.wall_horizontal.get_height(), self.wall_horizontal.get_width() + (2 * self.wall_vertical.get_width()), self.wall_horizontal.get_height())
		self.wall_horizontal_bottom_rect = pygame.Rect(settings.LEVEL_X - self.wall_vertical.get_width(), settings.LEVEL_MAX_Y, self.wall_horizontal.get_width() + (2 * self.wall_vertical.get_width()), self.wall_horizontal.get_height())
		self.wall_vertical_left_rect = pygame.Rect(settings.LEVEL_X - self.wall_vertical.get_width(), settings.LEVEL_Y, self.wall_vertical.get_width(), self.wall_vertical.get_height())
		self.wall_vertical_right_rect = pygame.Rect(settings.LEVEL_MAX_X, settings.LEVEL_Y, self.wall_vertical.get_width(), self.wall_vertical.get_height())

	def draw(self, surface):
		# We either blit the background images or fill the rects, depending on graphics.BACKGROUND.
		if graphics.BACKGROUND:
			surface.blit(self.wall_horizontal, (settings.LEVEL_X, settings.LEVEL_Y - self.wall_horizontal.get_height()))
			surface.blit(self.wall_horizontal, (settings.LEVEL_X, settings.LEVEL_MAX_Y))
			surface.blit(self.wall_vertical, (settings.LEVEL_X - self.wall_vertical.get_width(), settings.LEVEL_Y))
			surface.blit(self.wall_vertical, (settings.LEVEL_MAX_X, settings.LEVEL_Y))
			surface.blit(self.corner_top_left, (settings.LEVEL_X - self.wall_vertical.get_width(), settings.LEVEL_Y - self.wall_horizontal.get_height()))
			surface.blit(self.corner_top_left, (settings.LEVEL_MAX_X, settings.LEVEL_MAX_Y))
			surface.blit(self.corner_top_right, (settings.LEVEL_MAX_X, settings.LEVEL_Y - self.wall_horizontal.get_height()))
			surface.blit(self.corner_top_right, (settings.LEVEL_X - self.wall_vertical.get_width(), settings.LEVEL_MAX_Y))
		else:
			surface.fill(settings.BORDER_COLOR, self.wall_horizontal_top_rect)
			surface.fill(settings.BORDER_COLOR, self.wall_horizontal_bottom_rect)
			surface.fill(settings.BORDER_COLOR, self.wall_vertical_left_rect)
			surface.fill(settings.BORDER_COLOR, self.wall_vertical_right_rect)
