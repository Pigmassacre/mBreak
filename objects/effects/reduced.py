__author__ = "Olof Karlsson"
__license__ = "All Rights Reserved"

import pygame
import objects.groups as groups
import objects.effects.effect as effect
import settings.settings as settings

"""

This is the Reduced effect. When applied to a paddle, it decreases the vertical size of that paddle by a given amount.

"""

class Reduced(effect.Effect):

	# This is the amount of vertical height that the effect adds to paddles.
	size_decrease = 3 * settings.GAME_SCALE

	def __init__(self, parent, duration):
		# We start by calling the superconstructor.
		effect.Effect.__init__(self, parent, duration)

		# We store the parent.
		self.parent = parent

		# Then, we decrease the size of the parent.
		self.parent.set_size(self.parent.rect.width, self.parent.rect.height - Reduced.size_decrease)

		# Now, make sure that the position of the middle of the paddle isn't changed.
		self.parent.y += Reduced.size_decrease / 2

	def on_kill(self):
		# Increase the size of the paddle by the size we decreased it.
		self.parent.set_size(self.parent.rect.width, self.parent.rect.height + Reduced.size_decrease)

		# Now, make sure that the position of the middle of the paddle isn't changed.
		self.parent.y -= Reduced.size_decrease / 2