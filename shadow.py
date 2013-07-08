__author__ = "Olof Karlsson"
__version__ = "0.1"
__license__ = "All Rights Reserved"

import pygame
import math
import useful
import groupholder
from settings import *

class Shadow(pygame.sprite.Sprite):

	# Standard values. These will be used unless any other values are specified per instance of this class.
	offset_x = 3
	offset_y = 4
	linger_time = 1000
	alpha_step = 50

	def __init__(self, parent, color=pygame.Color(0, 0, 0, 128), linger=False, fill=False):
		# We start by calling the superconstructor.
		pygame.sprite.Sprite.__init__(self)
		
		# Keep track of the parent, used to position the shadow.
		self.parent = parent

		# Create the rect used for drawing the shadow.
		self.rect = pygame.rect.Rect(self.parent.rect.x, self.parent.rect.y, self.parent.rect.width, self.parent.rect.height)

		# Store the offset, the distance from the parent the shadow is drawn from.
		self.offset_x = Shadow.offset_x
		self.offset_y = Shadow.offset_y

		# Store the variables used when timing out the shadow.
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
			
			# Colorize the image.
			useful.colorize_image(self.image, self.color)

			# Convert to alpha and apply the alpha value.
			self.image.convert_alpha()
			self.image.set_alpha(self.color.a)
		else:
			# If using fill instead of image, create a new surface to handle alpha.
			self.surface = pygame.Surface((self.rect.width, self.rect.height), SRCALPHA)

		# Add self to the main shadow_group.
		groupholder.shadow_group.add(self)

	def blit_to(self, window_surface):
		if self.fill:
			self.surface.fill(self.color)
			window_surface.blit(self.surface, self.rect)
		else:
			window_surface.blit(self.image, self.rect)

	def update(self, main_clock):
		if self.linger:
			self.linger_time_left = self.linger_time_left - main_clock.get_time()
			if self.linger_time_left <= 0:
				if self.color.a - self.alpha_step < 0:
					self.kill()
				else:
					self.color.a = self.color.a - self.alpha_step

		# Move the shadow so it's under its parent.
		self.x = self.parent.x + self.offset_x
		self.y = self.parent.y + self.offset_y
		self.rect.x = self.x
		self.rect.y = self.y
