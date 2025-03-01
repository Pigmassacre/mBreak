__author__ = "Olof Karlsson"
__license__ = "All Rights Reserved"

import pygame
import random
import math
import objects.powerups.powerup as powerup
import objects.effects.timeout as timeout
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

	# The gravity direction change (in radians)
	gravity_angle = math.pi / 4  # 45 degrees

	# Scale image if needed
	image = pygame.transform.scale(image, (width, height))

	def __init__(self, x, y):
		# We start by calling the superconstructor.
		powerup.Powerup.__init__(self, x, y, Gravity.width, Gravity.height)

		# Load the image file.
		self.image = Gravity.image.copy()

		# Create a shadow.
		self.shadow = shadow.Shadow(self)

	def hit(self, entity):
		# Call the supermethod, it takes care of killing the powerup and printing debug message(s).
		powerup.Powerup.hit(self, entity)
		self.shadow.kill()

		# Find the opponent
		for player in groups.Groups.player_group:
			if player != entity.owner:
				opponent = player
				break

		# Apply gravity effect to all of the opponent's balls
		for ball_entity in opponent.ball_group:
			# Apply gravity effect to the ball
			ball_entity.gravity_direction = random.uniform(0, 2 * math.pi)  # Random direction
			ball_entity.gravity_strength = 0.05  # Small gravity effect

			# Create a timeout effect which is added to the ball to reset gravity
			timeout_effect = GravityEffect(ball_entity, Gravity.duration)

		# Store a powerup of this type in entity owners powerup group, so we can display the powerups collected by a player.
		entity.owner.add_powerup(Gravity, timeout_effect)

# Custom effect class for the gravity powerup
class GravityEffect(timeout.Timeout):
	
	def __init__(self, entity, duration):
		# Call the superconstructor
		timeout.Timeout.__init__(self, entity, duration)
		
		# Store the original gravity values
		self.original_gravity_direction = getattr(entity, 'gravity_direction', 0)
		self.original_gravity_strength = getattr(entity, 'gravity_strength', 0)
		
	def on_remove(self):
		# Reset gravity values when the effect expires
		self.entity.gravity_direction = self.original_gravity_direction
		self.entity.gravity_strength = self.original_gravity_strength
		
		# Call the supermethod
		timeout.Timeout.on_remove(self) 