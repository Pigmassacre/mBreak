__author__ = "Olof Karlsson"
__license__ = "All Rights Reserved"

import pygame
import random
import math
import objects.powerups.powerup as powerup
import objects.effects.gravitationalpull as gravitationalpull
import objects.shadow as shadow
import objects.groups as groups
import settings.settings as settings

"""

This is the Gravity powerup. When this powerup is hit by a ball, it temporarily changes the gravity direction
for the opponent's balls, making them curve in a different direction. This adds an interesting gameplay element
as it makes the opponent's balls harder to predict.

"""

def convert():
	# We put this here so the game-class can call this method to "preload" the image used for this powerup.
	# I could probably put this in the constructor of the powerup, but I worry about performance so I make sure to only do it once.
	Gravity.image.convert_alpha()

class Gravity(powerup.Powerup):

	# Load the image file here, so any new instance of this class doesn't have to reload it every time, they can just copy the surface.
	image = pygame.image.load("res/powerup/gravity.png")

	# Standard values. These will be used unless any other values are specified per instance of this class.
	width = image.get_width()
	height = image.get_height()

	# The amount of time the effect will last.
	duration = 8000

	# Scale image if needed
	image = pygame.transform.scale(image, (width, height))

	def __init__(self, x, y):
		# We start by calling the superconstructor.
		powerup.Powerup.__init__(self, x, y, Gravity.width, Gravity.height)

		# Load the image file.
		self.image = Gravity.image.copy()

		# Create a shadow.
		self.shadow = shadow.Shadow(self)

	def create_effect(self, entity):
		return gravitationalpull.GravitationalPull(entity)

	def hit(self, entity):
		# Call the supermethod, it takes care of killing the powerup and printing debug message(s).
		powerup.Powerup.hit(self, entity)
		self.shadow.kill()

		# Find the opponent
		for player in groups.Groups.player_group:
			if player != entity.owner:
				opponent = player
				break

		# Initialize effect variable
		effect = None

		# Apply gravity effect to all of the opponent's balls
		for ball_entity in opponent.ball_group:
			# Create a gravitational pull effect for the ball
			effect = self.create_effect(ball_entity)
			effect.real_owner = entity.owner

		# Store a powerup of this type in entity owners powerup group, so we can display the powerups collected by a player.
		if effect is not None:
			entity.owner.add_powerup(Gravity, effect) 