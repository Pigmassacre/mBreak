__author__ = "Olof Karlsson"
__license__ = "All Rights Reserved"

import pygame
import random
import math
import objects.powerups.powerup as powerup
import objects.effects.timeout as timeout
import objects.effects.freezing as freezing
import objects.shadow as shadow
import objects.particle as particle
import objects.ball as ball
import objects.groups as groups
import settings.settings as settings

"""

This is the Frost powerup. When picked up by a ball, it applys the "freezing" effect to that ball and all the other balls of
that balls owner. 

"""

def convert():
	# We put this here so the game-class can call this method to "preload" the image used for this powerup.
	# I could probably put this in the constructor of the powerup, but I worry about performance so I make sure to only do it once.
	Frost.image.convert_alpha()

class Frost(powerup.Powerup):

	# Load the image file here, so any new instance of this class doesn't have to reload it every time, they can just copy the surface.
	image = pygame.image.load("res/powerup/frost.png")

	# Standard values. These will be used unless any other values are specified per instance of this class.
	width = image.get_width() * settings.GAME_SCALE
	height = image.get_height() * settings.GAME_SCALE
	particle_spawn_rate = 600
	particle_spawn_amount = 2

	# Scale image to settings.GAME_SCALE.
	image = pygame.transform.scale(image, (width, height))

	def __init__(self, x, y):
		# We start by calling the superconstructor.
		powerup.Powerup.__init__(self, x, y, Frost.width, Frost.height, False)

		# When this reaches particle_spawn_rate, a particle is spawned.
		self.particle_spawn_time = 0

		# Load the image file.
		self.image = Frost.image.copy()

		# Create a shadow.
		self.shadow = shadow.Shadow(self)

	def create_effect(self, entity):
		return freezing.Freezing(entity)

	def hit(self, entity):
		# Call the supermethod, it takes care of killing the powerup and printing debug message(s).
		powerup.Powerup.hit(self, entity)
		self.shadow.kill()
		
		# Create a speed effect to be added to the ball.
		created_effect = self.create_effect(entity)

		# Add this effect to the owner of the ball.
		entity.owner.effect_group.add(created_effect)

		# Store a powerup of this type in entity owners powerup group, so we can display the powerups collected by a player.
		entity.owner.add_powerup(self.__class__, created_effect)

		#self.share_effect(entity, timeout.Timeout, self.create_effect)

	def update(self, main_clock):
		# We make sure to call the supermethod.
		powerup.Powerup.update(self, main_clock)

		# If it's time, spawn particles.
		self.particle_spawn_time += main_clock.get_time()
		if self.particle_spawn_time >= Frost.particle_spawn_rate:
			# Reset the particle spawn time.
			self.particle_spawn_time = 0

			# Spawn a random amount of particles.
			for _ in range(0, random.randrange(0, Frost.particle_spawn_amount)):
				angle = random.uniform(0, 2 * math.pi)
				speed = random.uniform(0.2 * settings.GAME_SCALE, 0.35 * settings.GAME_SCALE)
				retardation = speed / 76.0
				color = pygame.Color(random.randint(0, 50), random.randint(125, 255), random.randint(220, 255))
				particle.Particle(self.x + self.rect.width / 2, self.y + self.rect.height / 2, self.rect.width / 4, self.rect.width / 4, angle, speed, retardation, color, 1)