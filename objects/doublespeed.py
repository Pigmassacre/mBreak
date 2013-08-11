__author__ = "Olof Karlsson"
__version__ = "0.1"
__license__ = "All Rights Reserved"

import pygame
import random
import math
import other.useful as useful
import objects.powerup as powerup
import objects.speed as speed
import objects.shadow as shadow
import objects.ball as ball
import objects.groups as groups
import settings.settings as settings

def convert():
	DoubleSpeed.image.convert_alpha()

class DoubleSpeed(powerup.Powerup):

	# Load the image file here, so any new instance of this class doesn't have to reload it every time, they can just copy the surface.
	image = pygame.image.load("res/powerup/doublespeed.png")

	# Standard values. These will be used unless any other values are specified per instance of this class.
	width = image.get_width() * settings.GAME_SCALE
	height = image.get_height() * settings.GAME_SCALE
	width = 8 * settings.GAME_SCALE
	height = 8 * settings.GAME_SCALE

	# The amount of time the effect will last.
	duration = 10000

	# Scale image to settings.GAME_SCALE.
	image = pygame.transform.scale(image, (width, height))

	def __init__(self, x, y):
		# We start by calling the superconstructor.
		powerup.Powerup.__init__(self, x, y, DoubleSpeed.width, DoubleSpeed.height)

		# Load the image file.
		self.image = DoubleSpeed.image.copy()

		# Create a shadow.
		self.shadow = shadow.Shadow(self)

		if settings.DEBUG_MODE:
			print("DoubleSpeed spawned @ (" + str(self.rect.x) + ", " + str(self.rect.y) + ")")

	def hit(self, entity):
		# Call the supermethod, it takes care of killing the powerup and printing debug message(s).
		powerup.Powerup.hit(self, entity)
		self.shadow.kill()
		
		# Add the effect to all the balls of the entity owner.
		for ball in entity.owner.ball_group:
			# Create a speed effect to be added to the ball.
			speed_effect = speed.Speed(ball, DoubleSpeed.duration)
			
		# Add this effect to the owner of the ball.
		entity.owner.effect_group.add(speed_effect)
