__author__ = "Olof Karlsson"
__version__ = "0.1"
__license__ = "All Rights Reserved"

import pygame
from settings import *

class Ball(pygame.sprite.Sprite):

	def __init__(self, x, y, width, height, velocity_x, velocity_y, image_path):
		# We start by calling the superconstructor.
		pygame.sprite.Sprite.__init__(self)
		
		# Create the rect used for collision detection, position etc.
		self.rect = pygame.rect.Rect(x, y, width, height)

		# Set the velocity variables.
		self.velocity_x = velocity_x
		self.velocity_y = velocity_y

		# Create the image attribute that is drawn to the surface.
		self.image = pygame.image.load(image_path)

		if DEBUG_MODE:
			print("Ball spawned @ (" + str(self.rect.x) + ", " + str(self.rect.y) + ")")

	def update(self):
		self.rect.move_ip(self.velocity_x, self.velocity_y)
