__author__ = "Olof Karlsson"
__version__ = "0.1"
__license__ = "All Rights Reserved"

import pygame
import math
import useful
import groupholder
from settings import *

class Shadow(pygame.sprite.Sprite):

	def __init__(self, x, y, width, height, offset, parent, time_out=False, fill=False):
		# We start by calling the superconstructor.
		pygame.sprite.Sprite.__init__(self)
		
		# Create the rect used for drawing the shadow.
		self.rect = pygame.rect.Rect(x, y, width, height)

		# Keep track of x and y as floats, for preciseness sake (rect keeps track of x,y as ints)
		self.x = x
		self.y = y

		# Store the offset, the distance from the parent the shadow is drawn from.
		self.offset = offset

		# Store the variables used when timing out the shadow.
		self.time_out = time_out
		self.time_left = SHADOW_LINGER_TIME
		self.alpha_step = SHADOW_ALPHA_STEP

		# Keep track of the parent, used to position the shadow.
		self.parent = parent

		# Store whether or not to use image resource or fill blitting.
		self.fill = fill

		# Store the color.
		self.color = SHADOW_COLOR

		# Copy the parents image, and then colorize it to the shadow color.
		if not self.fill:
			self.image = self.parent.image.copy()
			useful.colorize_image(self.image, self.color)

		# Add self to the main shadow_group.
		groupholder.shadow_group.add(self)

	def blit_to(self, window_surface):
		if self.fill:
			window_surface.fill(self.color, self.rect)
		else:
			window_surface.blit(self.image, self.rect)

	def update(self, main_clock):
		if self.time_out:
			self.time_left = self.time_left - main_clock.get_time()
			if self.time_left <= 0:
				self.color.a = self.color.a - self.alpha_step

			if self.color.a - self.alpha_step < 0:
				self.kill()
			else:
				self.color.a = self.color.a - self.alpha_step

		# Move the shadow so it's under whatever object it's supposed to shadow.
		self.x = self.parent.x + self.offset
		self.y = self.parent.y + self.offset
		self.rect.x = self.x
		self.rect.y = self.y
