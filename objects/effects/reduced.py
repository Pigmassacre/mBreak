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

		# We store how much left we have to enlarge the paddle.
		self.unapplied_size = Reduced.size_decrease

		# Then, we decrease the size of the parent.
		previous_height = self.parent.rect.height
		if self.parent.rect.height - Reduced.size_decrease > self.parent.min_height:
			self.parent.set_size(self.parent.rect.width, self.parent.rect.height - Reduced.size_decrease)
		else:
			# If we would decrease the size of the paddle to or under min_height, simply decrease to min height.
			self.parent.set_size(self.parent.rect.width, self.parent.min_height)

		# Save the height left we've yet to apply.
		self.unapplied_size -= previous_height - self.parent.rect.height

		# Now, make sure that the position of the middle of the paddle isn't changed.
		self.parent.y += (Reduced.size_decrease - self.unapplied_size) / 2

	def on_kill(self):
		# Reduce the size of the paddle by the size we decreased it.
		previous_height = self.parent.rect.height
		if self.parent.rect.height + (Reduced.size_decrease - self.unapplied_size) < self.parent.max_height:
			self.parent.set_size(self.parent.rect.width, self.parent.rect.height + (Reduced.size_decrease - self.unapplied_size))
		else:
			self.parent.set_size(self.parent.rect.width, self.parent.max_height)
		
		# Save the difference in size after resizing the paddle.
		size_difference = self.parent.rect.height - previous_height

		# Now, make sure that the position of the middle of the paddle isn't changed.
		self.parent.y += size_difference / 2

	def update(self, main_clock):
		# We make sure to call the supermethod.
		effect.Effect.update(self, main_clock)

		# Check if we can decrease the height of the paddle.
		previous_height = self.parent.rect.height
		previous_unapplied_size = self.unapplied_size
		if self.unapplied_size > 0:
			# decrease the height of the paddle.
			if self.parent.rect.height - self.unapplied_size > self.parent.min_height:
				self.parent.set_size(self.parent.rect.width, self.parent.rect.height - self.unapplied_size)
			elif self.parent.rect.height != self.parent.min_height:
				# If we would decrease the size of the paddle to or under min_height, simply decrease to min height.
				self.parent.set_size(self.parent.rect.width, self.parent.min_height)

			# Save the height left we've yet to apply.
			self.unapplied_size -= previous_height - self.parent.rect.height

			# Now, make sure that the position of the middle of the paddle isn't changed.
			if self.unapplied_size != previous_unapplied_size:
				self.parent.y += (Reduced.size_decrease - self.unapplied_size) / 2