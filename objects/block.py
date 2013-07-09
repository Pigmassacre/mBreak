__author__ = "Olof Karlsson"
__version__ = "0.1"
__license__ = "All Rights Reserved"

import pygame
import other.useful as useful
import objects.shadow as shadow
import objects.groups as groups
from settings.settings import *

def convert():
	Block.image.convert()

class Block(pygame.sprite.Sprite):

	# Load the image file here, so any new instance of this class doesn't have to reload it every time, they can just copy the surface.
	image = pygame.image.load("res/block/block.png")

	# Standard values. These will be used unless any other values are specified per instance of this class.
	width = image.get_width() * GAME_SCALE
	height = image.get_height() * GAME_SCALE

	# Scale image to game_scale.
	image = pygame.transform.scale(image, (width, height))

	def __init__(self, x, y, health, owner):
		# We start by calling the superconstructor.
		pygame.sprite.Sprite.__init__(self)
		
		# Create the rect used for collision detection, position etc.
		self.rect = pygame.rect.Rect(x, y, Block.width, Block.height)

		# Keep track of x and y as floats, for preciseness sake (rect keeps track of x,y as ints)
		self.x = x
		self.y = y

		# Set the health. This is the amount of damage the block can take before it breaks.
		self.health = health

		# The owner is the player that owns the block.
		self.owner = owner

		# Store the ball in the owners ball_group.
		self.owner.block_group.add(self)

		# Create the image attribute that is drawn to the surface.
		self.image = Block.image.copy()

		# Colorize the block.
		self.color = color
		useful.colorize_image(self.image, self.owner.color)

		# Create a shadow.
		self.shadow = shadow.Shadow(self)

		# Add self to owners block_group and main block_group.
		self.owner.block_group.add(self)
		groups.Groups.block_group.add(self)

	def damage(self, damage):
		self.health = self.health - damage
		if self.health <= 0:
			self.kill()
			self.shadow.kill()