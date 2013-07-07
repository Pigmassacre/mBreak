__author__ = "Olof Karlsson"
__version__ = "0.1"
__license__ = "All Rights Reserved"

import pygame
import useful
import shadow
from settings import *

class Block(pygame.sprite.Sprite):

	def __init__(self, x, y, width, height, health, image_path, owner):
		# We start by calling the superconstructor.
		pygame.sprite.Sprite.__init__(self)
		
		# Create the rect used for collision detection, position etc.
		self.rect = pygame.rect.Rect(x, y, width, height)

		# Keep track of x and y as floats, for preciseness sake (rect keeps track of x,y as ints)
		self.x = x
		self.y = y

		# Set the health. This is the amount of damage the block can take before it breaks.
		self.health = health

		# Set the owner.
		self.owner = owner

		# Store the ball in the owners ball_group.
		self.owner.block_group.add(self)

		# Create the image attribute that is drawn to the surface.
		self.image = pygame.image.load(image_path)

		# Set the color value, the image is colorized to this value.
		self.color = color

		# Colorize the block.
		useful.colorize_image(self.image, self.owner.color)

		# Create a shadow.
		self.shadow = shadow.Shadow(self.x, self.y, self.rect.width, self.rect.height, SHADOW_OFFSET, self)

	def damage(self, damage):
		self.health = self.health - damage
		if self.health <= 0:
			self.kill()
			self.shadow.kill()