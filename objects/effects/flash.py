__author__ = "Olof Karlsson"
__license__ = "All Rights Reserved"

import pygame
import objects.camera as camera
import objects.groups as groups
import objects.effects.effect as effect
import settings.settings as settings

"""

Simple on-hit effect.

"""

class Flash(effect.Effect):

	def __init__(self, parent, start_color, final_color, tick_amount, duration = 3000):
		# We start by calling the superconstructor.
		effect.Effect.__init__(self, parent, duration)

		self.surface = pygame.Surface((self.parent.rect.width, self.parent.rect.height), pygame.locals.SRCALPHA)

		self.start_color = start_color
		self.current_color = self.start_color
		self.final_color = final_color

		if self.final_color.a > self.current_color.a:
			self.add = True
		else:
			self.add = False

		self.tick_amount = tick_amount

	def update(self, main_clock):
		# We make sure to call the supermethod.
		effect.Effect.update(self, main_clock)

		# We make sure that our size matches the parent.
		if self.parent.rect.width != self.surface.get_width() or self.parent.rect.height != self.surface.get_height():
			self.surface = pygame.transform.scale(self.surface, (self.parent.width, self.parent.height))
		
		# We update the current color.
		if self.add:
			if (self.current_color.a + int(self.tick_amount * main_clock.delta_time)) < self.final_color.a:
				self.current_color.a += int(self.tick_amount * main_clock.delta_time)
			else:
				self.current_color.a = self.final_color.a
		else:
			if (self.current_color.a - int(self.tick_amount * main_clock.delta_time)) > self.final_color.a:
				self.current_color.a -= int(self.tick_amount * main_clock.delta_time)
			else:
				self.current_color.a = self.final_color.a

		# If we've reached our final color, we destroy ourselves.
		if self.current_color.a == self.final_color.a:
			self.destroy()

	def draw(self, surface):
		# Draw the flash effect with the current color.
		self.surface.fill(self.current_color)
		
		# This is to make the alpha value work (filling doesn't work with alpha otherwise).
		return surface.blit(self.surface, (self.parent.rect.x - camera.CAMERA.x, self.parent.rect.y - camera.CAMERA.y))
