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

		# We store how much left we have to enlarge the paddle.
		self.unapplied_size = Enlarged.size_increase

		# Then, we increase the size of the parent.
		previous_height = self.parent.rect.height
		if not self.parent.rect.height + Enlarged.size_increase > self.parent.max_height:
			self.parent.set_size(self.parent.rect.width, self.parent.rect.height + Enlarged.size_increase)
		else:
			# If we would increase the size of the paddle over max_height, simply increase to max height.
			self.parent.set_size(self.parent.rect.width, self.parent.max_height)

		# Save the height left we've yet to apply.
		self.unapplied_size -= self.parent.rect.height - previous_height

		# Now, make sure that the position of the middle of the paddle isn't changed.
		self.parent.y -= (Enlarged.size_increase - self.unapplied_size) / 2

	def on_kill(self):
		# Reduce the size of the paddle by the size we increased it.
		self.parent.set_size(self.parent.rect.width, self.parent.rect.height - (Enlarged.size_increase - self.unapplied_size))

		# Now, make sure that the position of the middle of the paddle isn't changed.
		self.parent.y += (Enlarged.size_increase - self.unapplied_size) / 2

	def update(self, main_clock):
		# We make sure to call the supermethod.
		effect.Effect.update(self, main_clock)

		# Check if we can increase the height of the paddle.
		previous_height = self.parent.rect.height
		if self.unapplied_size > 0:
			# Increase the height of the paddle.
			if not self.parent.rect.height + self.unapplied_size > self.parent.max_height:
				self.parent.set_size(self.parent.rect.width, self.parent.rect.height + self.unapplied_size)
			elif self.parent.rect.height != self.parent.max_height:
				# If we would increase the size of the paddle over max_height, simply increase to max height.
				self.parent.set_size(self.parent.rect.width, self.parent.max_height)

			# Save the height left we've yet to apply.
			self.unapplied_size -= self.parent.rect.height - previous_height
