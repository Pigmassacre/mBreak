__author__ = "Olof Karlsson"
__license__ = "All Rights Reserved"

import pygame
import random
import math
import other.useful as useful
import objects.powerup as powerup
import objects.charged as charged
import objects.shadow as shadow
import objects.particle as particle
import objects.ball as ball
import objects.groups as groups
import settings.settings as settings

def convert():
	Electricity.image.convert_alpha()

class Electricity(powerup.Powerup):

	# Load the image file here, so any new instance of this class doesn't have to reload it every time, they can just copy the surface.
	image = pygame.image.load("res/powerup/electricity.png")

	# Standard values. These will be used unless any other values are specified per instance of this class.
	width = image.get_width() * settings.GAME_SCALE
	height = image.get_height() * settings.GAME_SCALE
	particle_spawn_rate = 550
	particle_spawn_amount = 5

	# Scale image to settings.GAME_SCALE.
	image = pygame.transform.scale(image, (width, height))

	def __init__(self, x, y):
		# We start by calling the superconstructor.
		powerup.Powerup.__init__(self, x, y, Electricity.width, Electricity.height)

		# When this reaches particle_spawn_rate, a particle is spawned.
		self.particle_spawn_time = 0

		# Load the image file.
		self.image = Electricity.image.copy()

		# Create a shadow.
		self.shadow = shadow.Shadow(self)

	def hit(self, entity):
		# Call the supermethod, it takes care of killing the powerup and printing debug message(s).
		powerup.Powerup.hit(self, entity)
		self.shadow.kill()
		
		# Create one effect and add it to this ball.	
		charged_effect = charged.Charged(entity)
		
		# Add this effect to the owner of the ball.
		entity.owner.effect_group.add(charged_effect)

		# Store a powerup of this type in entity owners powerup group, so we can display the powerups collected by a player.
		entity.owner.add_powerup(Electricity, charged_effect)

	def update(self, main_clock):
		# We make sure to call the supermethod.
		powerup.Powerup.update(self, main_clock)

		# If it's time, spawn particles.
		self.particle_spawn_time += main_clock.get_time()
		if self.particle_spawn_time >= Electricity.particle_spawn_rate:
			# Reset the particle spawn time.
			self.particle_spawn_time = 0

			# Spawn a random amount of particles.
			for _ in range(0, random.randrange(2, Electricity.particle_spawn_amount)):
				angle = random.uniform(0, 2 * math.pi)
				speed = random.uniform(0.9 * settings.GAME_SCALE, 1.4 * settings.GAME_SCALE)
				retardation = speed / 46.0
				random_value = random.randint(225, 255)
				color = pygame.Color(random_value, random_value, random.randint(0, 100))
				random_size = random.randint(self.rect.width / 8, self.rect.width / 6)
				particle.Particle(self.x + self.rect.width / 2, self.y + self.rect.height / 2, random_size, random_size, angle, speed, retardation, color, 20)