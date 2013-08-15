__author__ = "Olof Karlsson"
__version__ = "0.1"
__license__ = "All Rights Reserved"

import pygame
import other.useful as useful
import objects.blocks.block as block
import objects.shadow as shadow
import objects.groups as groups
import settings.settings as settings

def convert():
	WeakBlock.image.convert()

class WeakBlock(block.Block):

	# Load the image file here, so any new instance of this class doesn't have to reload it every time, they can just copy the surface.
	image = pygame.image.load("res/block/block_weak.png")
	half_health_image = pygame.image.load("res/block/block_weak.png")

	# Standard values. These will be used unless any other values are specified per instance of this class.
	width = image.get_width() * settings.GAME_SCALE
	height = image.get_height() * settings.GAME_SCALE
	health = 10

	# Scale image to settings.GAME_SCALE.
	image = pygame.transform.scale(image, (width, height))
	half_health_image = pygame.transform.scale(image, (width, height))

	def __init__(self, x, y, owner):
		# We start by calling the superconstructor.
		block.Block.__init__(self, owner, x, y, WeakBlock.width, WeakBlock.height, WeakBlock.health)

		# Create the image attribute that is drawn to the surface.
		self.image = WeakBlock.image.copy()

		# Colorize the block.
		self.color = self.owner.color
		useful.colorize_image(self.image, self.color)

		# Create the image that is drawn when health is half or less.
		self.half_health_image = WeakBlock.half_health_image.copy()

		# Colorize that image.
		self.half_health_color = useful.blend_colors(self.owner.color, block.Block.half_health_blend_color)
		useful.colorize_image(self.half_health_image, self.half_health_color)

		# Create a shadow.
		self.shadow = shadow.Shadow(self)