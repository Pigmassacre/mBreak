__author__ = "Olof Karlsson"
__version__ = "0.1"
__license__ = "All Rights Reserved"

import pygame
import random
import math
import other.useful as useful
import objects.powerup as powerup
import objects.homingrocket as homingrocket
import objects.shadow as shadow
import objects.groups as groups
import settings.settings as settings

def convert():
	Rocket.image.convert_alpha()

class Rocket(powerup.Powerup):

	# Load the image file here, so any new instance of this class doesn't have to reload it every time, they can just copy the surface.
	image = pygame.image.load("res/powerup/rocket.png")

	# Standard values. These will be used unless any other values are specified per instance of this class.
	width = image.get_width() * settings.GAME_SCALE
	height = image.get_height() * settings.GAME_SCALE
	width = 8 * settings.GAME_SCALE
	height = 8 * settings.GAME_SCALE

	# Scale image to settings.GAME_SCALE.
	image = pygame.transform.scale(image, (width, height))

	def __init__(self, x, y):
		# We start by calling the superconstructor.
		powerup.Powerup.__init__(self, x, y, Rocket.width, Rocket.height)

		# Load the image file.
		self.image = Rocket.image.copy()

		# Create a shadow.
		self.shadow = shadow.Shadow(self)

		if DEBUG_MODE:
			print("Rocket spawned @ (" + str(self.rect.x) + ", " + str(self.rect.y) + ")")

	def hit(self, entity):
		# Call the supermethod, it takes care of killing the powerup and printing debug message(s).
		powerup.Powerup.hit(self, entity)
		self.shadow.kill()

		#homingrocket.HomingRocket(, self.x, self.y, Rocket.speed, entity)