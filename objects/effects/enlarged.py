__author__ = "Olof Karlsson"
__license__ = "All Rights Reserved"

import pygame
import objects.groups as groups
import objects.effects.effect as effect
import settings.settings as settings

"""

This is the Enlarged effect. When applied to a paddle, it increases the vertical size of that paddle by a given amount.

"""

class Enlarged(effect.Effect):

	# This is the amount of vertical height that the effect adds to paddles.
	size_increase = 3 * settings.GAME_SCALE

	def __init__(self, parent, duration):
		# We start by calling the superconstructor.
		effect.Effect.__init__(self, parent, duration)

		# We store the parent.
		self.parent = parent

		# Then, we increase the size of the parent.
		self.parent.set_size(self.parent.rect.width, self.parent.rect.height + Enlarged.size_increase)

		# Now, make sure that the position of the middle of the paddle isn't changed.
		self.parent.y -= Enlarged.size_increase / 2

	def on_kill(self):
		# Reduce the size of the paddle by the size we increased it.
		self.parent.set_size(self.parent.rect.width, self.parent.rect.height - Enlarged.size_increase)

		# Now, make sure that the position of the middle of the paddle isn't changed.
		self.parent.y += Enlarged.size_increase / 2