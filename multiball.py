__author__ = "Olof Karlsson"
__version__ = "0.1"
__license__ = "All Rights Reserved"

import pygame
import powerup
from settings import *

class Multiball(powerup.Powerup):

	def __init__(self, x, y, width, height):
		# We start by calling the superconstructor.
		powerup.Powerup.__init__(self, x, y, width, height)

		if DEBUG_MODE:
			print("Multiball spawned @ (" + str(self.rect.x) + ", " + str(self.rect.y) + ")")
