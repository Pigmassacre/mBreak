__author__ = "Olof Karlsson"
__version__ = "0.1"
__license__ = "All Rights Reserved"

import pygame
import objects.groups as groups
import objects.effect as effect
from settings.settings import *

class Timeout(effect.Effect):

	# Load the image file here, so any new instance of this class doesn't have to reload it every time, they can just copy the surface.
	image = pygame.image.load("res/ball/ball.png")

	# Standard values. These will be used unless any other values are specified per instance of this class.
	width = image.get_width() * GAME_SCALE
	height = image.get_height() * GAME_SCALE

	# Scale image to match the game scale.
	image = pygame.transform.scale(image, (width, height))

	def __init__(self, parent, duration):
		# We start by calling the superconstructor.
		effect.Effect.__init__(self, parent, duration)

		# Create the image attribute that is drawn to the surface.
		self.image = Timeout.image.copy()

	def on_hit_ball(self, hit_ball):
		print(str(self.parent) + " hit ball " + str(hit_ball))

	def on_hit_block(self, hit_block):
		print(str(self.parent) + " hit block " + str(hit_block))
		
	def on_hit_paddle(self, hit_paddle):
		print(str(self.parent) + " hit paddle " + str(hit_paddle))

	def on_hit_wall(self):
		print(str(self.parent) + " hit a wall.")

	def update(self, main_clock):
		# We make sure to call the supermethod.
		effect.Effect.update(self, main_clock)

	def on_kill(self):
		# Timeout effect is over, so we fully kill the ball the effect is attached to.
		self.parent.destroy()