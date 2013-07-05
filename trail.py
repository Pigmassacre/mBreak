__author__ = "Olof Karlsson"
__version__ = "0.1"
__license__ = "All Rights Reserved"

import pygame
from settings import *

class Trail(pygame.sprite.Sprite):

	def __init__(self, x, y, width, height, alpha_step, image_path):
		# We start by calling the superconstructor.
		pygame.sprite.Sprite.__init__(self)
		
		# Create the rect used for collision detection, position etc.
		self.rect = pygame.rect.Rect(x, y, width, height)

		# Keep track of x and y as floats, for preciseness sake (rect keeps track of x,y as ints)
		self.x = x
		self.y = y

		self.alpha_step = alpha_step

		# Create the image attribute that is drawn to the surface.
		self.image = pygame.image.load(image_path)

		self.image.set_alpha(255)

	def update(self):
		if self.image.get_alpha() > 0:
			self.image.set_alpha(self.image.get_alpha() - self.alpha_step)
		else:
			self.kill()