__author__ = "Olof Karlsson"
__license__ = "All Rights Reserved"

import pygame
import other.useful as useful
import objects.blocks.block as block
import objects.shadow as shadow
import objects.groups as groups
import settings.settings as settings

"""

This is a subclass of Block. It is the normal block, with 20 health it can by default take two enemy ball hits.

"""

def convert():
	# Arguably this could be called in the constructor, but I worry about performance so I make sure to only call this once.
	NormalBlock.image.convert()

class NormalBlock(block.Block):

	# Load the image file here, so any new instance of this class doesn't have to reload it every time, they can just copy the surface.
	image = pygame.image.load("res/block/block.png")
	half_health_image = pygame.image.load("res/block/block.png")

	# Standard values. These will be used unless any other values are specified per instance of this class.
	width = image.get_width() * settings.GAME_SCALE
	height = image.get_height() * settings.GAME_SCALE
	health = 20

	# Scale image to settings.GAME_SCALE.
	image = pygame.transform.scale(image, (width, height))
	half_health_image = pygame.transform.scale(image, (width, height))

	def __init__(self, x, y, owner):
		# We start by calling the superconstructor.
		block.Block.__init__(self, owner, x, y, NormalBlock.width, NormalBlock.height, NormalBlock.health)	

		# Create the image attribute that is drawn to the surface.
		self.image = NormalBlock.image.copy()

		# Colorize the block.
		self.color = self.owner.color
		useful.colorize_image(self.image, self.color)

		# Create the image that is drawn when health is half or less.
		self.half_health_image = NormalBlock.half_health_image.copy()

		# Colorize that image.
		self.half_health_color = useful.blend_colors(self.owner.color, block.Block.half_health_blend_color)
		useful.colorize_image(self.half_health_image, self.half_health_color)

		# Create a shadow.
		self.shadow = shadow.Shadow(self)
