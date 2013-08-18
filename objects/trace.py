__author__ = "Olof Karlsson"
__license__ = "All Rights Reserved"

import pygame
from pygame.locals import *
import copy
import other.useful as useful
import objects.shadow as shadow
import objects.groups as groups
import settings.settings as settings

"""

This is the class that represents each trace in the game. Currently, only balls spawn traces (and only if the graphic options
for traces is set to True). A trace is the same size as its parent, and will eventually fade away until it is no longer visible,
at which point it will be killed.

Any object which has a color and a rect can spawn a trace attached to it.

"""

class Trace(pygame.sprite.Sprite):

	# Standard values. These will be used unless any other values are specified per instance of this class.
	shadow_blend_color = pygame.Color(100, 100, 100, 255)
	alpha_step = 16

	def __init__(self, parent):
		# We start by calling the superconstructor.
		pygame.sprite.Sprite.__init__(self)
		
		# Save the parent.
		self.parent = parent

		# Create the rect used for drawing the trace.
		width = self.parent.rect.width
		height = self.parent.rect.height
		self.x = self.parent.x
		self.y = self.parent.y
		self.rect = pygame.rect.Rect(self.x, self.y, width, height)

		# Setup the color values, used for drawing the trace.
		self.color = copy.copy(self.parent.color)

		# Since we're using fill, we create a new surface to handle alpha.
		self.surface = pygame.Surface((self.rect.width, self.rect.height), SRCALPHA)

		# Setup shadow color value, used for coloring the shadow.
		self.shadow_color = useful.blend_colors(self.color, Trace.shadow_blend_color)

		# Create a shadow.
		self.shadow = shadow.Shadow(self, self.shadow_color, False, True)

		# Add self to the main trace_group.
		groups.Groups.trace_group.add(self)

	def blit_to(self, surface):
		# Blits self to the given surface.
		self.surface.fill(self.color)
		return surface.blit(self.surface, self.rect)

	def destroy(self):
		# Takes care of killing ourselves and our shadow.
		self.kill()
		self.shadow.kill()

	def update(self):
		# Update the alpha in the RGBA color value. If it gets to or under 0, we kill ourself.
		if self.alpha_step > 0:
			if self.color.a - self.alpha_step < 0:
				self.destroy()
			else:
				self.color.a = self.color.a - Trace.alpha_step
				self.shadow.color.a = self.shadow.color.a - Trace.alpha_step

		# Kill the trace if it is no longer in the visible game area.
		if self.rect.x + self.rect.width <= settings.LEVEL_X:
			self.destroy()
		elif self.rect.x >= settings.LEVEL_MAX_X:
			self.destroy()
		if self.rect.y + self.rect.height <= settings.LEVEL_Y:
			self.destroy()
		elif self.rect.y >= settings.LEVEL_MAX_Y:
			self.destroy()
