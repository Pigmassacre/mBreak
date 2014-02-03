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

		# We store how much left we have to change the paddle.
		self.unapplied_size = self.size_change

		# Then, we change the size of the parent.
		previous_height = self.parent.rect.height
		if self.parent.rect.height + self.size_change < self.parent.max_height and self.parent.rect.height + self.size_change > self.parent.min_height:
			self.parent.set_size(self.parent.rect.width, self.parent.rect.height + self.size_change)
		elif self.parent.rect.height + self.size_change >= self.parent.max_height:
			# If we would change the size of the paddle to or over max_height, simply change to max height.
			self.parent.set_size(self.parent.rect.width, self.parent.max_height)
		else:
			# If we would change the size of the paddle to or under min_height, simply change to min height.
			self.parent.set_size(self.parent.rect.width, self.parent.min_height)
		
		# Save the height left we've yet to apply.
		self.unapplied_size -= self.parent.rect.height - previous_height
		
		# Now, make sure that the position of the middle of the paddle isn't changed.
		self.parent.y -= (self.size_change - self.unapplied_size) / 2

	def on_kill(self):
		applied_size = self.size_change - self.unapplied_size

		# Reduce the size of the paddle by the size we changed it.
		previous_height = self.parent.rect.height
		if self.parent.rect.height - applied_size > self.parent.min_height and self.parent.rect.height - applied_size < self.parent.max_height:
			self.parent.set_size(self.parent.rect.width, self.parent.rect.height - applied_size)
		elif self.parent.rect.height - applied_size <= self.parent.min_height:
			# If we would change the size of the paddle to or over max_height, simply change to max height.
			self.parent.set_size(self.parent.rect.width, self.parent.min_height)
		else:
			# If we would change the size of the paddle to or under min_height, simply change to min height.
			self.parent.set_size(self.parent.rect.width, self.parent.max_height)
		
		# Save the difference in size after resizing the paddle.
		size_difference = previous_height - self.parent.rect.height

		# Now, make sure that the position of the middle of the paddle isn't changed.
		self.parent.y += size_difference / 2

	def update(self, main_clock):
		# We make sure to call the supermethod.
		effect.Effect.update(self, main_clock)

		# Check if we can change the height of the paddle.
		if self.unapplied_size > 0:
			previous_height = self.parent.rect.height
			previous_unapplied_size = self.unapplied_size

			# Change the height of the paddle.
			if self.parent.rect.height + self.size_change < self.parent.max_height and self.parent.rect.height + self.size_change > self.parent.min_height:
				self.parent.set_size(self.parent.rect.width, self.parent.rect.height + self.size_change)
			elif self.parent.rect.height + self.size_change >= self.parent.max_height:
				# If we would change the size of the paddle to or over max_height, simply change to max height.
				self.parent.set_size(self.parent.rect.width, self.parent.max_height)
			else:
				# If we would change the size of the paddle to or under min_height, simply change to min height.
				self.parent.set_size(self.parent.rect.width, self.parent.min_height)
				
			# Save the height left we've yet to apply.
			self.unapplied_size -= self.parent.rect.height - previous_height
			
			# Now, make sure that the position of the middle of the paddle isn't changed.
			if self.unapplied_size != previous_unapplied_size:
				self.parent.y -= (self.size_change - self.unapplied_size) / 2
