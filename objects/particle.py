__author__ = "Olof Karlsson"
__license__ = "All Rights Reserved"

import pygame
import math
import copy
import other.useful as useful
import objects.shadow as shadow
import objects.groups as groups
import settings.settings as settings

"""

This is the class that handles each particle in the game. Particles can be easily created, and they handle their own movement
and destruction.

"""

class Particle(pygame.sprite.Sprite):

	# Standard values. These will be used unless any other values are specified per instance of this class.
	shadow_blend_color = pygame.Color(100, 100, 100, 255)

	def __init__(self, x, y, width, height, angle, speed, retardation, color, alpha_step = 0):
		# We start by calling the superconstructor.
		pygame.sprite.Sprite.__init__(self)
		
		# Create the rect used for drawing the particle.
		self.rect = pygame.rect.Rect(x, y, width, height)

		# Keep track of x and y as floats, for preciseness sake (rect keeps track of x,y as ints)
		self.x = x
		self.y = y

		# Setup speed, angle and retardation values, used when moving the particle.
		self.angle = angle
		self.speed = speed
		self.retardation = retardation
		
		# Setup alpha values.
		self.alpha_step = alpha_step
		self.alpha = 255

		# Setup the color values, used for drawing the particle.
		self.color = copy.copy(color)

		# Setup shadow color value, used for coloring the shadow.
		self.shadow_color = useful.blend_colors(self.color, Particle.shadow_blend_color)

		# Create a shadow.
		self.shadow = shadow.Shadow(self, self.shadow_color, True, True)

		# Add self to the main particle_group.
		groups.Groups.particle_group.add(self)

	def destroy(self):
		# Takes care of killing both itself and the shadow.
		self.kill()
		self.shadow.kill()

	def update(self):
		# Update speed, and kill self if speed gets to or under 0.
		self.speed = self.speed - self.retardation
		if self.speed <= 0:
			self.kill()
		
		# Update the alpha in the RGBA color value. If it gets to or under 0, kill self.
		if self.alpha_step > 0:
			if self.color.a - self.alpha_step < 0:
				self.kill()
			else:
				self.color.a = self.color.a - self.alpha_step

		# Finally, move the particle with speed in consideration.
		self.x = self.x + (math.cos(self.angle) * self.speed)
		self.y = self.y + (math.sin(self.angle) * self.speed)
		self.rect.x = self.x
		self.rect.y = self.y

		# Kill the particle if it is no longer in the visible game area.
		if self.rect.x + self.rect.width <= settings.LEVEL_X:
			self.destroy()
		elif self.rect.x >= settings.LEVEL_MAX_X:
			self.destroy()
		if self.rect.y + self.rect.height <= settings.LEVEL_Y:
			self.destroy()
		elif self.rect.y >= settings.LEVEL_MAX_Y:
			self.destroy()
