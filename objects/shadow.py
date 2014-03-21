__author__ = "Olof Karlsson"
__license__ = "All Rights Reserved"

import pygame
from pygame.locals import *
import objects.camera as camera
import other.useful as useful
import objects.groups as groups
import settings.settings as settings

"""

This is the Shadow class. A shadow is connected to a parent, and we can easily choose wether or not we want to use an 
image to draw the shadow (probably more performance heavy than filling) or using the fill method to draw the shadow.
The Game class takes care of drawing the shadow before the item the shadow is attached to, so it appears below it.

It's trivial to add a shadow to any sprite in the game.

"""

class Shadow(pygame.sprite.Sprite):

	# Standard values. These will be used unless any other values are specified per instance of this class.
	offset_x = 1 * settings.GAME_SCALE
	offset_y = 2 * settings.GAME_SCALE
	linger_time = 25 * settings.GAME_FPS
	alpha_step = 50 * settings.GAME_FPS

	def __init__(self, parent, color = pygame.Color(0, 0, 0, 128), linger = False, fill = False):
		# We start by calling the superconstructor.
		pygame.sprite.Sprite.__init__(self)
		
		# Keep track of the parent, used to position the shadow.
		self.parent = parent

		# Create the rect used for drawing the shadow.
		self.rect = pygame.rect.Rect(self.parent.rect.x, self.parent.rect.y, self.parent.rect.width, self.parent.rect.height)

		# Store the offset, the distance from the parent the shadow is drawn from.
		self.offset_x = Shadow.offset_x
		self.offset_y = Shadow.offset_y

		# Store the variables used when timing out the shadow. If set to linger, the shadow eventually fades away.
		self.linger = linger
		self.linger_time_left = Shadow.linger_time
		self.alpha_step = Shadow.alpha_step

		# Store whether or not to use image resource or fill blitting.
		self.fill = fill

		# Store the color.
		self.color = color

		# Copy the parents image, and then colorize it to the shadow color.
		if not self.fill:
			self.image = self.parent.image.copy()
			
			# Colorize the image. If the image doesn't have any alpha values, don't blend alphas. If it does, do blend alphas.
			if self.image.get_alpha() == None:
				useful.colorize_image(self.image, self.color)
			else:
				useful.colorize_image(self.image, self.color, True)

			# Convert to alpha and apply the alpha value.
			self.image.convert_alpha()
			self.image.set_alpha(self.color.a)

			# Store a copy of this image as the original image. Used when rotating the shadow.
			self.original_image = self.image.copy()
		else:
			# If using fill instead of image, create a new surface to handle alpha.
			self.surface = pygame.Surface((self.rect.width, self.rect.height), SRCALPHA)

		# Add self to the main shadow_group.
		groups.Groups.shadow_group.add(self)

	def blit_to(self, surface):
		# Blits the shadow to the given surface.
		if self.fill:
			# If using fill, first we fill our own surface with the color, then we blit that surface to the given surface.
			# This is to make the alpha value work (filling doesn't work with alpha otherwise).
			self.surface.fill(self.color)
			return surface.blit(self.surface, (self.rect.x - camera.CAMERA.x, self.rect.y - camera.CAMERA.y))
		else:
			# If we're not using fill, we simply blit the image to the given surface.
			return surface.blit(self.image, (self.rect.x - camera.CAMERA.x, self.rect.y - camera.CAMERA.y))

	def update(self, main_clock):
		# Check if we're supposed to linger.
		if self.linger:
			# If we're supposed to linger, check if there's any time left to linger.
			self.linger_time_left = self.linger_time_left - main_clock.get_time()
			if self.linger_time_left <= 0:
				# The time is out, so we reduce our alpha to zero, or if it's already zero we destroy ourselves.
				if self.color.a - int(self.alpha_step * main_clock.delta_time) < 0:
					self.kill()
				else:
					self.color.a -= int(self.alpha_step * main_clock.delta_time)

		# Move the shadow so it's under its parent.
		self.x = self.parent.x + self.offset_x
		self.y = self.parent.y + self.offset_y
		self.rect.x = self.x
		self.rect.y = self.y
