__author__ = "Olof Karlsson"
__license__ = "All Rights Reserved"

import pygame
import random
import math
import objects.powerups.powerup as powerup
import objects.effects.timeout as timeout
import objects.effects.burning as burning
import objects.shadow as shadow
import objects.particle as particle
import objects.ball as ball
import objects.groups as groups
import settings.settings as settings

"""

This is the Fire powerup. When picked up by a ball, it applies the "burning" effect to that ball and all the balls of
the owner of that ball.

"""

def convert():
	# We put this here so the game-class can call this method to "preload" the image used for this powerup.
	# I could probably put this in the constructor of the powerup, but I worry about performance so I make sure to only do it once.
	Fire.image.convert_alpha()

class Fire(powerup.Powerup):

	# Load the image file here, so any new instance of this class doesn't have to reload it every time, they can just copy the surface.
	image = pygame.image.load("res/powerup/fire.png")

	# Standard values. These will be used unless any other values are specified per instance of this class.
	width = image.get_width() * settings.GAME_SCALE
	height = image.get_height() * settings.GAME_SCALE
	particle_spawn_rate = 100
	particle_least_spawn_amount = 2
	particle_maximum_spawn_amount = 4

	# Scale image to settings.GAME_SCALE.
	image = pygame.transform.scale(image, (width, height))

	def __init__(self, x, y):
		# We start by calling the superconstructor.
		powerup.Powerup.__init__(self, x, y, Fire.width, Fire.height)

		# When this reaches particle_spawn_rate, a particle is spawned.
		self.particle_spawn_time = 0

		# Load the image file.
		self.image = Fire.image.copy()

		# Create a shadow.
		self.shadow = shadow.Shadow(self)

	def create_effect(self, entity):
		return burning.Burning(entity)

	def hit(self, entity):
		# Call the supermethod, it takes care of killing the powerup and printing debug message(s).
		powerup.Powerup.hit(self, entity)
		self.shadow.kill()

		self.share_effect(entity, timeout.Timeout, self.create_effect)

	def update(self, main_clock):
		# We make sure to call the supermethod.
		powerup.Powerup.update(self, main_clock)
		
		# If it's time, spawn particles.
		self.particle_spawn_time += main_clock.get_time()
		if self.particle_spawn_time >= Fire.particle_spawn_rate:
			# Reset the particle spawn time.
			self.particle_spawn_time = 0

			# Spawn a random amount of particles.
			for _ in range(0, random.randrange(Fire.particle_least_spawn_amount, Fire.particle_maximum_spawn_amount)):
				angle = random.uniform(0, 2 * math.pi)
				speed = random.uniform(0.75 * settings.GAME_FPS * settings.GAME_SCALE, 0.9 * settings.GAME_FPS * settings.GAME_SCALE)
				retardation = speed / 24.0
				color = pygame.Color(random.randint(200, 255), random.randint(0, 255), 0)
				particle.Particle(self.x + self.rect.width / 2, self.y + self.rect.height / 2, self.rect.width / 8, self.rect.width / 8, angle, speed, retardation, color, 5 * settings.GAME_FPS)
