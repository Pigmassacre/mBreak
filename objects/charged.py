__author__ = "Olof Karlsson"
__version__ = "0.1"
__license__ = "All Rights Reserved"

import pygame
import math
import random
import objects.groups as groups
import objects.effect as effect
import objects.blocks.block as block
import objects.particle as particle
import settings.settings as settings

class Charged(effect.Effect):

	damage_width = 8 * settings.GAME_SCALE
	damage_height = 8 * settings.GAME_SCALE
	damage = 5
	max_speed_reduction = 0.41 * settings.GAME_SCALE
	paddle_Charged_duration = 1100
	particle_spawn_rate = 600
	particle_spawn_amount = 2
	duration = 10000

	def __init__(self, parent, duration = None):
		# We check if a duration has been given.
		if not duration == None:
			# We start by calling the superconstructor with the given duration value.
			effect.Effect.__init__(self, parent, duration)
		else:
			# We start by calling the superconstructor with the standard duration value.
			effect.Effect.__init__(self, parent, Charged.duration)

		# When this reaches particle_spawn_rate, a particle is spawned.
		self.particle_spawn_time = 0

		self.damage_rect = pygame.rect.Rect(self.rect.x + ((self.rect.width - self.damage_width) / 2), self.rect.y + ((self.rect.height - self.damage_height) / 2), self.damage_width, self.damage_height)

	def on_hit_block(self, hit_block):
		if hit_block.owner != self.parent.owner:
			for block in hit_block.owner.block_group:
				if self.damage_rect.contains(block.rect):
					block.on_hit(Charged.damage)
					self.spawn_particles(block)
		self.kill()

	def update(self, main_clock):
		# We make sure to call the supermethod.
		effect.Effect.update(self, main_clock)

		# Position the damage rect.
		self.damage_rect.x = self.rect.x + ((self.rect.width - self.damage_width) / 2)
		self.damage_rect.y = self.rect.y + ((self.rect.height - self.damage_height) / 2)

		# If it's time, spawn particles.
		self.particle_spawn_time += main_clock.get_time()
		if self.particle_spawn_time >= Charged.particle_spawn_rate:
			# Reset the particle spawn time.
			self.particle_spawn_time = 0

			# Spawn a random amount of particles.
			self.spawn_particles(self)

	def spawn_particles(self, entity):
		for _ in range(0, random.randrange(0, Charged.particle_spawn_amount)):
			angle = random.uniform(0, 2 * math.pi)
			random_value = random.randint(200, 255)
			color = pygame.Color(random_value, random_value, random.randint(0, 25))
			particle.Particle(entity.rect.x + entity.rect.width / 2, entity.rect.y + entity.rect.height / 2, entity.rect.width / 4, entity.rect.width / 4, angle, 0, 0, color, 10)
