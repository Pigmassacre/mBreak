__author__ = "Olof Karlsson"
__license__ = "All Rights Reserved"

import pygame
import random
import math
import objects.powerups.powerup as powerup
import objects.missile as missile
import objects.shadow as shadow
import objects.groups as groups
import settings.settings as settings

"""

This is the Rocket effect. When picked up by a ball, it spawns a missile that homes in on a random block owned by the enemy of the owner
of that ball.

"""

def convert():
	# We put this here so the game-class can call this method to "preload" the image used for this powerup.
	# I could probably put this in the constructor of the powerup, but I worry about performance so I make sure to only do it once.
	Rocket.image.convert_alpha()

class Rocket(powerup.Powerup):

	# Load the image file here, so any new instance of this class doesn't have to reload it every time, they can just copy the surface.
	image = pygame.image.load("res/powerup/rocket.png")

	# Standard values. These will be used unless any other values are specified per instance of this class.
	width = image.get_width() * settings.GAME_SCALE
	height = image.get_height() * settings.GAME_SCALE
	particle_spawn_rate = 100
	particle_spawn_amount = 3

	# Scale image to settings.GAME_SCALE.
	image = pygame.transform.scale(image, (width, height))

	def __init__(self, x, y):
		# We start by calling the superconstructor.
		powerup.Powerup.__init__(self, x, y, Rocket.width, Rocket.height)

		# When this reaches particle_spawn_rate, a particle is spawned.
		self.particle_spawn_time = 0

		# Load the image file.
		self.image = Rocket.image.copy()

		# Create a shadow.
		self.shadow = shadow.Shadow(self)

	def hit(self, entity):
		# Call the supermethod, it takes care of killing the powerup and printing debug message(s).
		powerup.Powerup.hit(self, entity)
		self.shadow.kill()

		# Create a list of all available blocks to target.
		block_list = []
		for player in groups.Groups.player_group:
			if player != entity.owner:
				block_list = player.block_group.sprites()

		# Create a missile that homes in on a random block in the block list.
		missile.Missile(entity.x, entity.y, random.uniform(0, 2*math.pi), entity.owner, random.choice(block_list))