__author__ = "Olof Karlsson"
__version__ = "0.1"
__license__ = "All Rights Reserved"

import pygame
import objects.groups as groups
import settings.settings as settings

class Powerup(pygame.sprite.Sprite):

	width = 8 * settings.GAME_SCALE
	height = 8 * settings.GAME_SCALE

	def __init__(self, x, y, width, height):
		# We start by calling the superconstructor.
		pygame.sprite.Sprite.__init__(self)

		# Create the rect used for collision detection, position etc.
		self.rect = pygame.rect.Rect(x, y, width, height)

		# Keep track of x and y as floats, for preciseness sake (rect keeps track of x,y as ints)
		self.x = x
		self.y = y

		# Store self in the main powerup_group.
		groups.Groups.powerup_group.add(self)

		if settings.DEBUG_MODE:
			print("Powerup spawned @ (" + str(self.rect.x) + ", " + str(self.rect.y) + ")")

	def hit(self, entity):
		self.kill()

		if settings.DEBUG_MODE:
			print("Powerup hit!")