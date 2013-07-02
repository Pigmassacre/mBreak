__author__ = "Olof Karlsson"
__version__ = "0.1"
__license__ = "All Rights Reserved"

import pygame
from settings import *

class Ball(pygame.sprite.Sprite):

	def __init__(self, x, y, width, height, velocity_x, velocity_y, speed, image_path):
		# We start by calling the superconstructor.
		pygame.sprite.Sprite.__init__(self)
		
		# Create the rect used for collision detection, position etc.
		self.rect = pygame.rect.Rect(x, y, width, height)

		# Keep track of x and y, for preciseness sake
		self.x = x
		self.y = y

		# Set the velocity variables.
		self.velocity_x = velocity_x
		self.velocity_y = velocity_y

		# Set the speed variable.
		self.speed = speed

		# Create the image attribute that is drawn to the surface.
		self.image = pygame.image.load(image_path)

		if DEBUG_MODE:
			print("Ball spawned @ (" + str(self.rect.x) + ", " + str(self.rect.y) + ") with velocity (" + str(self.velocity_x) + ", " + str(self.velocity_y) + ")")

	def update(self):
		self.x = self.x + (self.velocity_x * self.speed)
		self.y = self.y + (self.velocity_y * self.speed)
		self.rect.x = self.x
		self.rect.y = self.y
		if DEBUG_MODE:
			print("New pos @ (" + str(self.x) + ", " + str(self.y) + ")")
