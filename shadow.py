__author__ = "Olof Karlsson"
__version__ = "0.1"
__license__ = "All Rights Reserved"

import pygame
import math
import useful
import groupholder
from settings import *

class Shadow(pygame.sprite.Sprite):

	def __init__(self, x, y, width, height, offset, parent):
		# We start by calling the superconstructor.
		pygame.sprite.Sprite.__init__(self)
		
		# Create the rect used for drawing the shadow.
		self.rect = pygame.rect.Rect(x, y, width, height)

		# Keep track of x and y as floats, for preciseness sake (rect keeps track of x,y as ints)
		self.x = x
		self.y = y

		# Store the offset, the distance from the parent the shadow is drawn from.
		self.offset = offset

		# Keep track of the parent, used to position the shadow.
		self.parent = parent

		# Copy the parents image, and then colorize it to the shadow color.
		self.image = self.parent.image.copy()
		self.color = SHADOW_COLOR
		useful.colorize_image(self.image, self.color)

		# Add self to the main shadow_group.
		groupholder.shadow_group.add(self)

	def update(self):
		# Move the shadow so it's under whatever object it's supposed to shadow.
		self.x = self.parent.x + self.offset
		self.y = self.parent.y + self.offset
		self.rect.x = self.x
		self.rect.y = self.y
