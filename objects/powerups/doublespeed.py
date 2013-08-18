__author__ = "Olof Karlsson"
__license__ = "All Rights Reserved"

import pygame
import random
import math
import other.useful as useful
import objects.powerups.powerup as powerup
import objects.effects.timeout as timeout
import objects.effects.speed as speed
import objects.shadow as shadow
import objects.ball as ball
import objects.groups as groups
import settings.settings as settings

"""

This is the DoubleSpeed powerup. When picked up by a ball, it applies the speed effect to that ball and all the balls of the
owner of that ball.

"""

def convert():
	# We put this here so the game-class can call this method to "preload" the image used for this powerup.
	# I could probably put this in the constructor of the powerup, but I worry about performance so I make sure to only do it once.
	DoubleSpeed.image.convert_alpha()

class DoubleSpeed(powerup.Powerup):

	# Load the image file here, so any new instance of this class doesn't have to reload it every time, they can just copy the surface.
	image = pygame.image.load("res/powerup/doublespeed.png")

	# Standard values. These will be used unless any other values are specified per instance of this class.
	width = image.get_width() * settings.GAME_SCALE
	height = image.get_height() * settings.GAME_SCALE
	
	# The amount of time the effect will last.
	duration = 7500

	# Scale image to settings.GAME_SCALE.
	image = pygame.transform.scale(image, (width, height))

	def __init__(self, x, y):
		# We start by calling the superconstructor.
		powerup.Powerup.__init__(self, x, y, DoubleSpeed.width, DoubleSpeed.height)

		# Load the image file.
		self.image = DoubleSpeed.image.copy()

		# Create a shadow.
		self.shadow = shadow.Shadow(self)

	def hit(self, entity):
		# Call the supermethod, it takes care of killing the powerup and printing debug message(s).
		powerup.Powerup.hit(self, entity)
		self.shadow.kill()

		# Add the effect to all the balls of the entity owner. However, if the ball has timeout, make sure it cannot use that balls effect as
		# the effect to connect to the displayed powerup.
		for ball in entity.owner.ball_group:
			has_timeout = False
			for effect in ball.effect_group:
				if effect.__class__ == timeout.Timeout:
					speed.Speed(ball, DoubleSpeed.duration)
					has_timeout = True
					break
			if not has_timeout:
				# Create a speed effect to be added to the ball.
				speed_effect = speed.Speed(ball, DoubleSpeed.duration)

		# Add this effect to the owner of the ball.
		entity.owner.effect_group.add(speed_effect)

		# Store a powerup of this type in entity owners powerup group, so we can display the powerups collected by a player.
		entity.owner.add_powerup(DoubleSpeed, speed_effect)
