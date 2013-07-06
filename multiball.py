__author__ = "Olof Karlsson"
__version__ = "0.1"
__license__ = "All Rights Reserved"

import pygame
import powerup
import useful
import ball
from settings import *

class Multiball(powerup.Powerup):

	def __init__(self, x, y, width, height, color):
		# We start by calling the superconstructor.
		powerup.Powerup.__init__(self, x, y, width, height)

		# Load the image file.
		self.image = pygame.image.load("res/powerup/multiball.png")

		# Store the color.
		self.color = color

		# Colorize.
		useful.colorize_image(self.image, self.color)

		if DEBUG_MODE:
			print("Multiball spawned @ (" + str(self.rect.x) + ", " + str(self.rect.y) + ")")

	def hit(self, entity):
		# Call the supermethod, it takes care of killing the powerup and printing debug message(s).
		powerup.Powerup.hit(self, entity)

