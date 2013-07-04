__author__ = "Olof Karlsson"
__version__ = "0.1"
__license__ = "All Rights Reserved"

import pygame
from settings import *

class Block(pygame.sprite.Sprite):

	def __init__(self, x, y, width, height, image_path, owner):
		# We start by calling the superconstructor.
		pygame.sprite.Sprite.__init__(self)
		
		# Create the rect used for collision detection, position etc.
		self.rect = pygame.rect.Rect(x, y, width, height)

		# Keep track of x and y as floats, for preciseness sake (rect keeps track of x,y as ints)
		self.x = x
		self.y = y

		# Create the image attribute that is drawn to the surface.
		self.image = pygame.image.load(image_path)

		# Set the owner.
		self.owner = owner