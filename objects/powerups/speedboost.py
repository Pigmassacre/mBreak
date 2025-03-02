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

This is the SpeedBoost powerup. When picked up by a ball, it applies the speed effect to that ball 
and all the balls of the owner of that ball. The speed effect increases the ball's speed by a configurable percentage.

"""

def convert():
	# We put this here so the game-class can call this method to "preload" the image used for this powerup.
	# I could probably put this in the constructor of the powerup, but I worry about performance so I make sure to only do it once.
	SpeedBoost.image.convert_alpha()

class SpeedBoost(powerup.Powerup):

	# Load the image file here, so any new instance of this class doesn't have to reload it every time, they can just copy the surface.
	image = pygame.image.load("res/powerup/speedboost.png")

	# Standard values. These will be used unless any other values are specified per instance of this class.
	width = image.get_width()
	height = image.get_height()
	
	# The amount of time the effect will last.
	duration = 7500
	
	# The speed multiplier to apply (1.0 = normal speed, 2.0 = double speed)
	speed_multiplier = 2.0

	# Scale image.
	image = pygame.transform.scale(image, (width, height))

	def __init__(self, x, y, speed_multiplier=None):
		# We start by calling the superconstructor.
		powerup.Powerup.__init__(self, x, y, SpeedBoost.width, SpeedBoost.height)

		# Store the speed multiplier, use default if none provided
		self.speed_multiplier = speed_multiplier if speed_multiplier is not None else SpeedBoost.speed_multiplier

		# Load the image file.
		self.image = SpeedBoost.image.copy()

		# Create a shadow.
		self.shadow = shadow.Shadow(self)

	def create_effect(self, entity):
		return speed.Speed(entity, SpeedBoost.duration, self.speed_multiplier)

	def hit(self, entity):
		# Call the supermethod, it takes care of killing the powerup and printing debug message(s).
		powerup.Powerup.hit(self, entity)
		self.shadow.kill()

		# Apply the effect to the entity that hit the powerup and all other balls owned by the same player
		effect = self.create_effect(entity)
		effect.real_owner = entity.owner
		
		# Store a powerup of this type in entity owners powerup group, so we can display the powerups collected by a player.
		entity.owner.add_powerup(SpeedBoost, effect)
		
		# Apply the effect to all other balls owned by the same player
		for ball_entity in entity.owner.ball_group:
			if ball_entity != entity:
				effect = self.create_effect(ball_entity)
				effect.real_owner = entity.owner 