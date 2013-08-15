__author__ = "Olof Karlsson"
__version__ = "0.1"
__license__ = "All Rights Reserved"

import pygame
import other.useful as useful
import objects.ball as ball
import objects.groups as groups
import objects.effect as effect
import settings.settings as settings

class Timeout(effect.Effect):

	# Load the image file here, so any new instance of this class doesn't have to reload it every time, they can just copy the surface.
	image = pygame.image.load("res/effect/timeout.png")

	# Standard values. These will be used unless any other values are specified per instance of this class.
	width = image.get_width() * settings.GAME_SCALE
	height = image.get_height() * settings.GAME_SCALE

	# Scale image to match the game scale.
	image = pygame.transform.scale(image, (width, height))

	def __init__(self, parent, duration):
		# We start by calling the superconstructor.
		effect.Effect.__init__(self, parent, duration)

		# Create the image attribute that is drawn to the surface. We only do this if the parent is a ball, however.
		if self.parent.__class__ == ball.Ball:
			self.image = Timeout.image.copy()
			useful.colorize_image(self.image, self.parent.color)

		# Set the rects width and height to the standard values.
		self.rect.width = Timeout.width
		self.rect.height = Timeout.height

	def update(self, main_clock):
		# We make sure to call the supermethod.
		effect.Effect.update(self, main_clock)

	def on_kill(self):
		# Effect is over, so we fully kill the parent the effect is attached to.
		self.parent.destroy()