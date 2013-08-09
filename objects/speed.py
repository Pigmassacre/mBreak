__author__ = "Olof Karlsson"
__version__ = "0.1"
__license__ = "All Rights Reserved"

import pygame
import objects.groups as groups
import objects.effect as effect
from settings.settings import *

class Speed(effect.Effect):

	def __init__(self, parent, duration):
		# We start by calling the superconstructor.
		effect.Effect.__init__(self, parent, duration)

	def update(self, main_clock):
		# We make sure to call the supermethod.
		effect.Effect.update(self, main_clock)

		# To simulate double speed and make sure that all collisions are handled, we simply call the parents update method.
		self.parent.update(main_clock)
