__author__ = "Olof Karlsson"
__license__ = "All Rights Reserved"

import pygame
import objects.groups as groups
import objects.effects.effect as effect
import settings.settings as settings

"""

This is the SizeChange effect. When applied to a paddle, it changes the vertical size of that paddle by a given amount.

"""

class SizeChange(effect.Effect):

	def __init__(self, parent, duration, size_change):
		# We start by calling the superconstructor.
		effect.Effect.__init__(self, parent, duration)

		# We store the parent.
		self.parent = parent

		# We store the amount that we've to change the paddles height. This can be negative!
		self.size_change = size_change

		# We add our size change amount to the paddle.
		self.parent.add_size(0, self.size_change)

	def on_kill(self):
		# We simply remove the size change amount from the paddle.
		self.parent.add_size(0, -self.size_change)